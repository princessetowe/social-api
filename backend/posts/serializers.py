from rest_framework import serializers
from .models import Post, Comment, Like
from accounts.serializers import CustomUserSerializer

class PostSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only = True)

    class Meta:
        model = Post
        fields = ('id', 'creator', 'caption', 'image', 'created_at')
        read_only_fields = ("id", "creator", "created_at")

class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created-at']
        read_only_fields = ['id', 'user', 'id']