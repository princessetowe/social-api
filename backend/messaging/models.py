from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

#Group Chats or normal chats
class Chat(models.Model):
    members = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat for {', '.join([user.username for user in self.members.all()])}"
    
    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

#Messages sent in the chat
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat.id}"
    
    @property
    def recipients(self):
        return self.chat.members.exclude(id=self.sender.id)
    
class MessageMedia(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'), 
        ('file', 'File')
    )

    message = models.ForeignKey(Message, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="posts/media/")
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)

    def __str__(self):
        return f"Media for {self.message.chat.members}"