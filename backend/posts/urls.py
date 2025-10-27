from django.urls import path
from .views import (
    PostListCreateAPIView, PostRetrieveUpdateDestroyAPIView,
    CommentListCreateAPIView, LikeAPIView
)

urlpatterns = [
    path("", PostListCreateAPIView.as_view(), name="post-list"),
    path("<str:creator>/<int:user_post_id>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="post-detail"),
    path("<str:username>/<int:post_pk>/comments/", CommentListCreateAPIView.as_view(), name="comment"),
    path("<int:post_id>/likes/", LikeAPIView.as_view(), name="comment"),
]
