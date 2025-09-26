from django.urls import path
from .views import CustomUserListView, CustomUserRetrieveUpdateDestroyView, LoginView, SignupAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view()),
    path('', CustomUserListView.as_view()),
    path('<int:pk>', CustomUserRetrieveUpdateDestroyView.as_view()),
    path("login/", LoginView.as_view()),
    # path("logout/", LogoutView.as_view()),
]