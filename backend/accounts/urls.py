from django.urls import path
from .views import CustomUserListCreateView, CustomUserRetrieveUpdateDestroyView, LogoutView, LoginView

urlpatterns = [
    path('', CustomUserListCreateView.as_view()),
    path('<int:pk>', CustomUserRetrieveUpdateDestroyView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
]