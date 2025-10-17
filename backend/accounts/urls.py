from django.urls import path
from .views import (
    CustomUserListView, CustomUserRetrieveAPIView, 
    LoginView, SignupAPIView, VerifyEmailAPIView,
    CustomUserUpdateAPIView, CustomUserDestroyAPIView,
    FollowAPIView, UnfollowAPIView, FollowersListAPIView,
    FollowingListAPIView, FollowRequestListAPIView, 
    FollowRequestAcceptOrRejectAPIView, LogoutView
)

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name="user-registration"),
    path('', CustomUserListView.as_view(), name="user-list"),
    path('<str:username>/profile/', CustomUserRetrieveAPIView.as_view(), name="user-detail"),
    path('<str:username>/edit-profile/', CustomUserUpdateAPIView.as_view(), name="user-detail"),
    path('<str:username>/deleteaccount/', CustomUserDestroyAPIView.as_view(), name="user-delete"),
    path('login/', LoginView.as_view(), name="user-login"),
    path('logout/', LogoutView.as_view()),
    path('verify-email/<uuid:token>/', VerifyEmailAPIView.as_view(), name="verify-email"),
    path('follow/<str:username>/', FollowAPIView.as_view()),
    path('unfollow/<str:username>/', UnfollowAPIView.as_view()),
    path('<str:username>/followers/', FollowersListAPIView.as_view()),
    path('<str:username>/following/', FollowingListAPIView.as_view()),
    path('follow-requests/', FollowRequestListAPIView.as_view()),
    path('follow-requests/<str:username>/', FollowRequestAcceptOrRejectAPIView.as_view()),
]