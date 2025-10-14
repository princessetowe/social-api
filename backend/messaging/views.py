from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# Create your views here.

class ChatListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer):
        chat = serializer.save()
        chat.members.add(self.request.user)

class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        if not chat.members.filter(id=request.user.id).exists():
            return Response({"error": "You are not a member of this chat"}, status=status.HTTP_403_FORBIDDEN)
        
        messages = Message.objects.filter(chat__id=chat_id)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.members.filter(id=self.request.user.id).exists():
            return PermissionError("You are not a member of this chat")
        serializer.save(sender=self.request.user, chat=chat)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionError):
            return Response({"error":str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)

class MarkAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request,chat_id, message_id):
        chat = get_object_or_404(Chat, id=chat_id)
        message = get_object_or_404(Message, id=message_id, chat=chat)
        if not chat.members.filter(id=request.user.id).exists():
            return Response({"error": "You are not a member of this chat"}, status=status.HTTP_403_FORBIDDEN)

        if message.sender==request.user:
            return Response({"error":"You cannot mark your message as read"}, status=status.HTTP_403_FORBIDDEN)
        
        if not message.is_read:
            message.is_read=True
            message.save()
            return Response({"message":"Message marked as read"}, status=status.HTTP_200_OK)
        return Response({"message":"Message already marked as read"}, status=status.HTTP_200_OK)