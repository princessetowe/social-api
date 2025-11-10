from rest_framework import serializers
from .models import CustomUser, Follow, UserStats, Block

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'date_joined', 'profile_picture', 'bio', 'is_active', 'updated_at', 'password', 'is_private']
        read_only_fields = ['id', 'date_joined', 'updated_at', 'is_active']
        extra_kwargs = {'password': {"write_only":True}}

    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = ["id", "created_at", "follower"]

class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = ['user', 'posts_count', 'followers_count', 'following_count']
        read_only_fields = ['user']

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'created_at']
        read_only_fields = ['id', 'created_at', 'blocker']

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
        )
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
        )
    
    def validate_new_password(self, value):
        if attrs.get('current_password') == value:
            raise serializers.ValidationError("New password must be different from the current password.")
        return attrs
