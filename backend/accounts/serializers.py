from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'date_joined', 'profile_picture', 'bio', 'is_active', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'updated_at']