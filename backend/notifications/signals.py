from django.db.models.signals import post_save 
from django.dispatch import receiver
from posts.models import Like, Comment
from .models import Notification

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        if instance.post.creator != instance.user:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.post.creator,
                message=f"{instance.user.username} liked your post",
                notification_type='like'
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        if instance.post.creator != instance.user:
            Notification.objects.create(
                recipient=instance.post.creator,
                sender=instance.user,
                message=f"{instance.user.username} commented on your post",
            )

  
        if instance.main and instance.main.user != instance.user:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.main.user,
                message=f"{instance.user.username} replied to your comment."
            )  