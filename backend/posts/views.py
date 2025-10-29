from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from utils.tags import handle_tags
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from accounts.models import Block

User = get_user_model()
class PostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'username',
                openapi.IN_QUERY,
                description="Filter posts by username",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: PostSerializer(many=True)},
        operation_description="Retrieve posts. You can filter by ?username=<username>.",
    )

    def get(self, request):
        user = request.user
        posts = Post.objects.select_related("creator")

        username = request.query_params.get("username")

        blocked_by_users = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
        blocking_users = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
        posts = posts.exclude(creator__id__in=blocked_by_users).exclude(creator__id__in=blocking_users)

        if username:
            posts = posts.filter(creator__username=username)
            
            try:
                target_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if Block.objects.filter(blocker=user, blocked=target_user).exists() or \
               Block.objects.filter(blocker=target_user, blocked=user).exists():
                return Response({"error": "You cannot view this user's posts"}, status=status.HTTP_403_FORBIDDEN)
            
            if target_user.is_private and target_user != user:
                return Response({"error": "This account is private"}, status=status.HTTP_403_FORBIDDEN)
            
            posts = posts.filter(creator=target_user)
        else:
            posts = posts.exclude(creator__is_private=True) | posts.filter(creator=user)

        posts = posts.distinct().order_by("-created_at")
        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'caption': openapi.Schema(type=openapi.TYPE_STRING, description='Caption for the post'),
                'files': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_FILE),
                    description='List of image/video files to upload'
                ),
            },
            required=['files'],
        ),
        responses={
            201 : "Post Created",
            400 : "Bad Request",
        },
        operation_description="Create a new post",

    )

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        creator = self.kwargs.get("creator")
        user_post_id = self.kwargs.get("user_post_id")
        post = get_object_or_404(Post.objects.select_related("creator"), user_post_id=user_post_id, creator__username=creator)

        if post.creator.is_private and self.request.user != post.creator:
            raise PermissionDenied("This is a private account")
        
        if Block.objects.filter(blocker=self.request.user, blocked=post.creator).exists() or \
           Block.objects.filter(blocker=post.creator, blocked=self.request.user).exists():
            raise PermissionDenied("You cannot view this user's post")
        
        if self.request.method in ["PUT", "PATCH", "DELETE"] and post.creator != self.request.user:
            raise PermissionDenied("You can only make changes to your posts")
        
        return post
class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        username = self.kwargs["username"]
        post_id = self.kwargs["user_post_id"]
        user = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, user_post_id=post_id, creator__username=username)

        if user.is_private and user != self.request.user:
            raise PermissionDenied("This is a private account")
        
        if Block.objects.filter(blocker=self.request.user, blocked=user).exists() or \
           Block.objects.filter(blocker=user, blocked=self.request.user).exists():
            raise PermissionDenied("You cannot view or comment on this user's posts")
        
        return Comment.objects.filter(post=post).select_related("user").order_by("-created_at")
    
    def perform_create(self, serializer):
        username = self.kwargs["username"]
        post_id = self.kwargs["user_post_id"]
        user = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, user_post_id=post_id, creator__username=username)

        if user.is_private and user != self.request.user:
            raise PermissionDenied("This is a private account")
        
        if Block.objects.filter(blocker=self.request.user, blocked=user).exists() or \
           Block.objects.filter(blocker=user, blocked=self.request.user).exists():
            raise PermissionDenied("You cannot comment on this user's posts")
        
        serializer.save(user=self.request.user, post=post)

class LikeAPIView(generics.GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, username, user_post_id):
        user = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, user_post_id=user_post_id, creator__username=username)

        if post.creator == request.user:
            return Response({"error": "You cannot like your own post"}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_private and user != request.user:
            raise PermissionDenied("This is a private account")
        
        if Block.objects.filter(blocker=request.user, blocked=user).exists() or \
           Block.objects.filter(blocker=user, blocked=request.user).exists():
            raise PermissionDenied("You cannot like this user's post")
        
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({"message": "Liked by you already"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, username, user_post_id):
        user = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, user_post_id=user_post_id, creator__username=username)

        if user.is_private and user != request.user:
            raise PermissionDenied("This is a private account")
        
        if Block.objects.filter(blocker=request.user, blocked=user).exists() or \
           Block.objects.filter(blocker=user, blocked=request.user).exists():
            raise PermissionDenied("You cannot interact with this user's post")
        
        try:
            like= Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_204_NO_CONTENT)
        
        except Like.DoesNotExist:
            return Response({"message": "You have not liked this post"}, status=status.HTTP_400_BAD_REQUEST)