from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
import uuid
from django.utils import timezone
from django_countries.fields import CountryField
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

User = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text=('The groups this user belongs to.'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='accounts/profile_pics', null=True, blank=True)
    bio = models.TextField(blank=True)
    country = CountryField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    phone_number = PhoneNumberField(region=None, null=True, blank=True, unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS =["email"]
    def __str__(self):
        return self.username
    
class EmailVerificationToken(models.Model):
    customuser = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="email_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=8)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at
    
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user} requested to follow {self.to_user}"

class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="stats")
    posts_count = models.PositiveIntegerField(default=0)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.user.username}"
   
class Block(models.Model):
    blocker = models.ForeignKey(User, related_name="blocking", on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name="blocked_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"