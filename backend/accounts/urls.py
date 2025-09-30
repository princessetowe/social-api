from django.urls import path
from .views import (
    CustomUserListView, CustomUserRetrieveAPIView, 
    LoginView, SignupAPIView, VerifyEmailAPIView,
    CustomUserUpdateAPIView, CustomUserDestroyAPIView
)

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name="user-registration"),
    path('', CustomUserListView.as_view(), name="user-list"),
    path('<str:username>/fetch/', CustomUserRetrieveAPIView.as_view(), name="user-detail"),
    path('<str:username>/edit/', CustomUserUpdateAPIView.as_view(), name="user-detail"),
    path('<str:username>/delete/', CustomUserDestroyAPIView.as_view(), name="user-delete"),
    path('login/', LoginView.as_view(), name="user-login"),
    path("verify-email/<uuid:token>/", VerifyEmailAPIView.as_view(), name="verify-email"),
]