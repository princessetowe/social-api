from django.urls import path
from .views import (
    PostListCreateAPIView, PostRetrieveUpdateDestroyAPIView,
    CommentListCreateAPIView
)

urlpatterns = [
    path("", PostListCreateAPIView.as_view(), name="post-list"),
    path("<int:pk>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="post-detail"),
    path("<int:post_pk>/comments/", CommentListCreateAPIView.as_view(), name="comment"),
]
