from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"

class Post(models.Model):
    creator = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_post_id = models.PositiveIntegerField()

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("creator", "user_post_id")

    def save(self, *args, **kwargs):
        if not self.pk:
            last_post = Post.objects.filter(creator=self.creator).order_by("-user_post_id").first()
            self.user_post_id = (last_post.user_post_id + 1) if last_post else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Post for {self.creator.username} - {self.user_post_id}"

class PostMedia(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video')
    )

    post = models.ForeignKey(Post, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="posts/media/")
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)

    def __str__(self):
        return f"{self.media_type} for {self.post.creator}'s post"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    main = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} commented on {self.post.id}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} liked {self.post.id}"