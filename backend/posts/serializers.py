from rest_framework import serializers
from .models import Post, Comment, Like, PostMedia, Hashtag
from accounts.serializers import CustomUserSerializer
from django.contrib.auth import get_user_model
from utils.tags import handle_tags
from utils.hashtag import extract_hashtags

User = get_user_model

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type']

class PostSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only = True)
    media = PostMediaSerializer(many=True, read_only =True)
    files = serializers.ListField(
        child=serializers.FileField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True, 
        required=False
    )
    class Meta:
        model = Post
        fields = ('id', 'creator', 'caption', 'media', 'files', 'created_at')
        read_only_fields = ("id", "creator", "created_at",  'user_post_id')

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        request = self.context.get("request")
        user = request.user

        validated_data.pop('creator', None)
        validated_data.pop('user_post_id', None)

        last_post = Post.objects.filter(creator=user).order_by("-user_post_id").first()
        next_id = (last_post.user_post_id + 1) if last_post else 1

        post = Post.objects.create(creator=user, user_post_id=next_id, **validated_data)

        for file in files:
            #Checks file extension
            ext = file.name.lower()
            if ext.endswith(('.mp4', '.mov', '.mkv')):
                media_type = 'video'

            elif ext.endswith(('.jpeg', '.png', 'jpg', '.bmp', '.gif', '.tiff', '.webp', '.svg')):
                media_type = 'image'

            else:
                raise serializers.ValidationError({"file": "Unsupported file format"})
            
            PostMedia.objects.create(post=post, file=file, media_type=media_type)

        hashtags = extract_hashtags(post.caption or "")
        for tag in hashtags:
            hashtag_obj, created = Hashtag.objects.get_or_create(name=tag.lower())
            if not created:
                hashtag_obj.save()
        return post
    
    def to_representation(self, instance):
        creator = instance.creator
        creator_data = {
            "username": creator.username,
            "profile_picture": creator.profile_picture.url if creator.profile_picture else None,
        }

        media_data = PostMediaSerializer(instance.media.all(), many=True, context=self.context).data
        return {
            "creator": creator_data,
            "user_post_id": instance.user_post_id,
            "caption": instance.caption,
            "media": media_data,
        }
        
class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    tagged_users =serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'replies', 'main', 'tagged_users']
        read_only_fields = ['id', 'user', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_tagged_users(self, obj):
        users = handle_tags(obj.text)
        return [user.username for user in users]

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'id']
