from django.db.models.signals import post_save 
from django.dispatch import receiver
from posts.models import Like, Comment, Post
from .models import Notification
from accounts.models import Follow, FollowRequest, CustomUser
import re

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
        #Normal comment
        if instance.post.creator != instance.user:
            Notification.objects.create(
                recipient=instance.post.creator,
                sender=instance.user,
                message=f"{instance.user.username} commented on your post",
            )

        #Replied to a comment    
        if instance.main and instance.main.user != instance.user:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.main.user,
                message=f"{instance.user.username} replied to your comment"
            )  

        #Tagged in a comment
        tagged_usernames = re.findall(r'@(\w+)', instance.caption)
        for username in tagged_usernames:
            try:
                tagged_user = CustomUser.objects.get(username=username)
                if tagged_user != instance.user:
                    Notification.objects.create(
                        sender=instance.user,
                        recipient=tagged_user,
                        notification_type='tag',
                        message=f"{instance.user.username} tagged you in a comment."
                    )
            except CustomUser.DoesNotExist:
                continue

@receiver(post_save, sender=Post)
def create_post_tags_notification(sender, instance, created, **kwargs):
    if not created:
        return

    tagged_usernames = re.findall(r'@(\w+)', instance.caption)
    for username in tagged_usernames:
        try:
            tagged_user = CustomUser.objects.get(username=username)
            if tagged_user != instance.creator:
                Notification.objects.create(
                    sender=instance.creator,
                    recipient=tagged_user,
                    notification_type='tag',
                    message=f"{instance.creator.username} tagged you in a post"
                )
        except CustomUser.DoesNotExist:
            continue

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.follower,
            recipient=instance.following,
            message=f"{instance.follower.username} started following you",
            notification_type='follow'
        )
            
@receiver(post_save, sender=FollowRequest)
def create_follow_request_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.from_user,
            recipient=instance.to_user,
            message=f"{instance.from_user.username} sent you a follow request",
            notification_type='follow_request'
        )