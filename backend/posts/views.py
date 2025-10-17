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

class PostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        responses={200: PostSerializer(many=True)},
        operation_description="Retrieve a list of all posts",
    )

    def get(self, request):
        posts = Post.objects.all().order_by("-created_at")
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

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        post_id = self.kwargs["post_pk"]
        return Comment.objects.filter(post_id=post_id,).select_related("user").order_by("-created_at")
    
    def perform_create(self, serializer):
        post_id = self.kwargs["post_pk"]
        comment = serializer.save(user=self.request.user, post_id=post_id)

class LikeAPIView(generics.GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, post_id):
        like, created = Like.objects.get_or_create(user=request.user, post_id=post_id)
        if not created:
            return Response({"message": "Liked by you already"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, post_id):
        try:
            like= Like.objects.get(user=request.user, post_id=post_id)
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_204_NO_CONTENT)
        
        except Like.DoesNotExist:
            return Response({"message": "You have not liked this post"}, status=status.HTTP_400_BAD_REQUEST)