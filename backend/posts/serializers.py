from rest_framework import serializers
from .models import Post
from accounts.serializers import CustomUserSerializer

class PostSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only = True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'owner', 'caption', 'image', 'created_at', 'likes_count')
        read_only_fields = ("id", "owner", "created_at", "likes_count")