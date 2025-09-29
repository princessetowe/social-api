from django.urls import path
from .views import (
    CustomUserListView, CustomUserRetrieveUpdateDestroyView, 
    LoginView, SignupAPIView, VerifyEmailAPIView
)

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name="user-registration"),
    path('', CustomUserListView.as_view(), name="user-list"),
    path('<int:pk>/', CustomUserRetrieveUpdateDestroyView.as_view(), name="user-detail"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("verify-email/<uuid:token>/", VerifyEmailAPIView.as_view(), name="verify-email"),
]