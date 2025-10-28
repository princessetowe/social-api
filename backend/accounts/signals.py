from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Follow, UserStats
from posts.models import Post

@receiver(post_save, sender=Follow)
def update_stats_on_follow(sender, instance, created, **kwargs):
    if created:
        UserStats.objects.get_or_create(user=instance.follower)
        UserStats.objects.get_or_create(user=instance.following)

        following_stats = UserStats.objects.get(user=instance.follower)
        followers_stats = UserStats.objects.get(user=instance.following)

        following_stats.following_count = Follow.objects.filter(follower=instance.follower).count()
        followers_stats.followers_count = Follow.objects.filter(following=instance.following).count()

        following_stats.save()
        followers_stats.save()

@receiver(post_delete, sender=Follow)
def update_stats_on_unfollow(sender, instance, **kwargs):
    try:
        following_stats = UserStats.objects.get(user=instance.follower)
        followers_stats = UserStats.objects.get(user=instance.following)

        following_stats.following_count = Follow.objects.filter(follower=instance.follower).count()
        followers_stats.followers_count = Follow.objects.filter(following=instance.following).count()

        following_stats.save()
        followers_stats.save()
    except UserStats.DoesNotExist:
        pass

@receiver(post_save, sender=Post)
def update_stats_on_post_create(sender, instance, created, **kwargs):
    if created:
        stats, _ = UserStats.objects.get_or_create(user=instance.creator)
        stats.posts_count = Post.objects.filter(creator=instance.creator).count()
        stats.save()


@receiver(post_delete, sender=Post)
def update_stats_on_post_delete(sender, instance, **kwargs):
    stats, _ = UserStats.objects.get_or_create(user=instance.creator)
    stats.posts_count = Post.objects.filter(creator=instance.creator).count()
    stats.save()