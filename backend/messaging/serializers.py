# messaging/serializers.py
from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "text", "is_read", "created_at"]
        read_only_fields = ["id", "chat", "sender", "is_read", "created_at"]

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    members = serializers.ListField(
        child=serializers.CharField(), write_only=True
        )
    member_usernames = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "members", "member_usernames", "messages", "created_at"]

    def get_member_usernames(self, obj):
        return [user.username for user in obj.members.all()]
    
    def create(self, validated_data):
        usernames = validated_data.pop('members', [])
        request_user = self.context['request'].user

        usernames = list(set(usernames + [request_user.username]))

        users = User.objects.filter(username__in=usernames)

        if len(users) != len(usernames):
            missing = set(usernames) -set(users.values_list('username', flat=True))
            raise serializers.ValidationError({"members":f"User(s) not found: {', '.join(missing)}"})
        
        chat = Chat.objects.create()
        chat.members.set(users)
        return chat