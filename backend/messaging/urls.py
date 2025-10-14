from django.urls import path
from .views import ChatListCreateAPIView, MessageListCreateAPIView, MarkAsReadAPIView

urlpatterns = [
    path('chat/', ChatListCreateAPIView.as_view()),
    path('message/<int:chat_id>/', MessageListCreateAPIView.as_view()),
    path('chat/<int:chat_id>/message/<int:message_id>/read/', MarkAsReadAPIView.as_view()),
]