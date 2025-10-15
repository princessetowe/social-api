from rest_framework import serializers
from .models import Chat, Message, MessageMedia
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageMedia
        fields = ['id', 'file', 'media_type']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")
    media = MessageMediaSerializer(many=True, read_only =True)
    files = serializers.ListField(
        child=serializers.FileField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True, 
        required=False
    )

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "text","media", "files","is_read", "created_at"]
        read_only_fields = ["id", "chat", "sender", "is_read", "created_at"]

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        message = Message.objects.create(**validated_data)

        for file in files:
            #Checks file extension
            ext = file.name.lower()
            if ext.endswith(('.mp4', '.mov', '.mkv')):
                media_type = 'video'

            elif ext.endswith(('.jpeg', '.png', 'jpg', '.bmp', '.gif', '.tiff', '.webp', '.svg')):
                media_type = 'image'
            else:
                media_type = "file"
            
            MessageMedia.objects.create(message=message, file=file, media_type=media_type)

        return message

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    members = serializers.ListField(
        child=serializers.CharField(), write_only=True
        )#List of usernames
    member_usernames = serializers.SerializerMethodField(read_only=True)#To display usernames
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "members", "member_usernames", "messages", "created_at"]

    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.unread_count(user)

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