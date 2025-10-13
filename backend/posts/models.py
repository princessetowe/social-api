from django.db import models
from django.conf import settings
# Create your models here.
User = settings.AUTH_USER_MODEL
class Post(models.Model):
    creator = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post for {self.creator}"

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