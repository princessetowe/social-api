from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from accounts.models import CustomUser
from posts.models import Post
from .serializers import UserSearchSerializer, PostSearchSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication

class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search query. Use '@' for username, '#' for hashtag, or plain text for name search.",
                type=openapi.TYPE_STRING,
                required=True,
                example="@bola",
            ),
        ],
        responses={
            200: openapi.Response(description="Search results"),
            400: openapi.Response(description="Missing query parameter"),
        },
        operation_summary="Search users or posts",
        operation_description="Search for users by username/name or posts by hashtag.",
    )

    def get(self, request):
        query = request.query_params.get("search", "").strip()
        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        #Hashtag search
        if query.startswith("#"):
            hashtag = query[1:]
            posts = Post.objects.filter(caption__icontains=f"#{hashtag}", creator__is_private=False)
            serializer = PostSearchSerializer(posts, many=True, context={"request": request})
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        #Users search
        elif query.startswith("@"):
            username = query[1:]
            users = CustomUser.objects.filter(username__icontains=username)
            results = []
            for user in users:
                if user.is_private and user != request.user:
                    results.append({
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "profile_picture": (
                            request.build_absolute_uri(user.profile_picture.url)
                            if user.profile_picture else None
                        ),
                        "is_private": True
                    })
                else:
                     results.append(UserSearchSerializer(user, context={"request": request}).data)
            return Response({"results": results}, status=status.HTTP_200_OK)

        #Name search
        else:
            users = CustomUser.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
            results = []
            for user in users:
                if user.is_private and user != request.user:
                    results.append({
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "profile_picture": (
                            request.build_absolute_uri(user.profile_picture.url)
                            if user.profile_picture else None
                        ),
                        "is_private": True
                    })
                else:
                    results.append(UserSearchSerializer(user, context={"request": request}).data)

            return Response({"users": results}, status=status.HTTP_200_OK)