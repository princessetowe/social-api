from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        # fields = ['id', 'sender_username', 'message', 'notification_type', 'created_at']