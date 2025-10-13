from rest_framework import serializers
from accounts.models import CustomUser
from posts.models import Post

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name", "profile_picture"]

class PostSearchSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "user", "caption", "media"]
