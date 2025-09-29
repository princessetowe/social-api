from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
import uuid
from django.utils import timezone
from django_countries.fields import CountryField

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    bio = models.TextField(blank=True)
    country = CountryField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS =["username"]
    def __str__(self):
        return self.email
    
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