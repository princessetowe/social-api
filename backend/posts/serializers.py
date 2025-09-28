from rest_framework import serializers
from .models import Post, Comment
from accounts.serializers import CustomUserSerializer

class PostSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only = True)

    class Meta:
        model = Post
        fields = ('id', 'creator', 'caption', 'image', 'created_at')
        read_only_fields = ("id", "creator", "created_at")

class CommentSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'creator', 'content', 'created_at']
        read_only_fields = ['id', 'creator', 'created_at']
