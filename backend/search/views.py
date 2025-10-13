from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.db.models import Q
from accounts.models import CustomUser
from posts.models import Post
from .serializers import UserSearchSerializer, PostSearchSerializer

# Create your views here.

class SearchAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        #Hashtag search
        if query.startswith("#"):
            hashtag = query[1:]
            posts = Post.objects.filter(caption__icontains=f"#{hashtag}")
            serializer = PostSearchSerializer(posts, many=True, context={"request": request})
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        #Users search
        elif query.startswith("@"):
            username = query[1:]
            users = CustomUser.objects.filter(username__icontains=username)
            serializer = UserSearchSerializer(users, many=True, context={"request": request})
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        #Name search
        else:
            users = CustomUser.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
            user_data = UserSearchSerializer(users, many=True, context={"request": request}).data

            return Response({
                "users": user_data,
            }, status=status.HTTP_200_OK)
