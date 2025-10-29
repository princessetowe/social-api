from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.models import Block

class ChatListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Chat.objects.filter(members=self.request.user)
   
    def perform_create(self, serializer):
        chat = serializer.save()
        chat.members.add(self.request.user)

class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        chat_id = self.kwargs.get("chat_id")
        return Message.objects.filter(chat__id=chat_id)

    @swagger_auto_schema(
        operation_description="List all messages in a chat",
        responses={200: MessageSerializer(many=True)},
    )

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
    
        for member in chat.members.all():
            if Block.objects.filter(blocker=self.request.user, blocked=member).exists() or \
               Block.objects.filter(blocker=member, blocked=self.request.user).exists():
                raise PermissionError("You cannot send messages to this user")

        serializer.save(sender=self.request.user, chat=chat)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionError):
            return Response({"error":str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)

class MarkAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Mark a specific message as read",
        manual_parameters=[
            openapi.Parameter('chat_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description="Chat ID"),
            openapi.Parameter('message_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description="Message ID"),
        ],
        responses={
            200: openapi.Response("Message marked as read"),
            403: "You cannot mark your message as read",
            404: "Message or Chat not found",
        },
    )

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
    
class UnreadCountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get unread message count for the logged-in user",
        responses={200: openapi.Response(description="Unread message count")},
    )

    def get(self, request, *args, **kwargs):
        user = request.user
        unread_count = Message.objects.filter(chat__members=user, is_read=False).exclude(sender=user).count()
        return Response({"unread_message":unread_count}, status=status.HTTP_200_OK)