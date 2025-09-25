from django.urls import path
from .views import CustomUserListCreateView, CustomUserRetrieveUpdateDestroyView

urlpatterns = [
    path('', CustomUserListCreateView.as_view()),
    path('<int:pk>', CustomUserRetrieveUpdateDestroyView.as_view())
]