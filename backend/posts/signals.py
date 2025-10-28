import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Post, PostMedia


@receiver(post_delete, sender=PostMedia)
def delete_media_file_on_delete(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)


@receiver(post_delete, sender=Post)
def delete_all_post_media_on_post_delete(sender, instance, **kwargs):
    for media in instance.media.all():
        if media.file and os.path.isfile(media.file.path):
            os.remove(media.file.path)