from rest_framework import serializers
from .models import Post, Comment, Like, PostMedia
from accounts.serializers import CustomUserSerializer
import re
from django.contrib.auth import get_user_model
User = get_user_model

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type']

class PostSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only = True)
    media = PostMediaSerializer(many=True, read_only =True)
    files = serializers.ListField(
        child=serializers.FileField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True, 
        required=False
    )
    class Meta:
        model = Post
        fields = ('id', 'creator', 'caption', 'media', 'files', 'created_at')
        read_only_fields = ("id", "creator", "created_at")

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        post = Post.objects.create(**validated_data)

        for file in files:
            #Checks file extension
            ext = file.name.lower()
            if ext.endswith(('.mp4', '.mov', '.mkv')):
                media_type = 'video'

            elif ext.endswith(('.jpeg', '.png', 'jpg', '.bmp', '.gif', '.tiff', '.webp', '.svg')):
                media_type = 'image'

            else:
                raise serializers.ValidationError({"file": "Unsupported file format"})
            
            PostMedia.objects.create(post=post, file=file, media_type=media_type)
        caption_text = validated_data.get("caption", "")
        self.handle_tags(caption_text, post)
        return post
    
    def handle_tags(self, text, instance):
        tagged_usernames = re.findall(r'@(\w+)', text)

        for username in tagged_usernames:
            try:
                tagged_user = User.objects.get(username=username)
                print(f"{tagged_user.username} was mentioned")
            except User.DoesNotExist:
                continue

class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'replies', 'main']
        read_only_fields = ['id', 'user', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'id']
