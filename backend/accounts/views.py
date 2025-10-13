from rest_framework import generics, status
from .models import CustomUser, EmailVerificationToken, Follow, FollowRequest
from .serializers import CustomUserSerializer, FollowSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
import uuid
from django.shortcuts import get_object_or_404
# from drf_yasg.utils import swagger_auto_schema


User = settings.AUTH_USER_MODEL

# Create your views here.

class CustomUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class SignupAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)

        try:
            customuser = serializer.save()
            user = customuser
            user.is_active=False
            user.save()

            token = EmailVerificationToken.objects.create(customuser=customuser)
            verification_url = f"http://127.0.0.1:8000/api/accounts/verify-email/{token.token}"
            send_mail(
                    "Confirm your email",
                    f"Hi {user.username}, please confirm your email by clicking this link: {verification_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            return Response({
                    "message": "User registered successfully",
                    "user":{
                        "id":user.id,
                        "username":user.username,
                        "email":user.email,
                    }
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = "username"

class CustomUserUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"

    def perform_update(self, serializer):
        user = self.get_object()
        
        if self.request.user != user:
            raise PermissionDenied("You can only update your own profile")
        
        old_email = user.email
        new_email = self.request.data.get("email", old_email)

        updated_user = serializer.save()

        if old_email != new_email:
            updated_user.is_active = False  
            updated_user.save()
            token = str(uuid.uuid4())
            EmailVerificationToken.objects.create(customuser=updated_user, token=token)


            verification_link = f"http://localhost:8000/api/accounts/verify-email/{token}/"  
            send_mail(
                subject="Verify your new email address",
                message=f"Hi {updated_user.username}, please verify your new email by clicking: {verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
            )

class CustomUserDestroyAPIView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"

    def perform_destroy(self, instance):
        if self.request.user != instance:
            raise PermissionDenied("You can only delete your own account.")
        instance.delete()

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    
    # @swagger_auto_schema(
    #     request_body=LoginSerializer,
    #     responses={
    #         200: "Login successful",
    #         400: "Invalid credentials",
    #     },
    #     operation_description="Login using email, username, or phone number."
    # )

    def post(self, request, *args, **kwargs):
        login = request.data.get("login")
        password = request.data.get("password")

        
        if not login or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import authenticate

        customuser = authenticate(request, username=login, password=password)

        user = customuser
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Please verify your email before logging in"}, status=status.HTTP_403_FORBIDDEN)

        
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "phone_number": str(user.phone_number),
                "profile_picture": user.profile_picture.url if user.profile_picture else None
            }
        }, status=status.HTTP_200_OK)
        
class LogoutView(APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            return Response({"error": "Not logged in"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class VerifyEmailAPIView(APIView):
    def get(self, request, token, *args, **kwargs):
        try:
            token_obj = EmailVerificationToken.objects.get(token=token)
            user = token_obj.customuser
            user.is_active = True
            user.save()
            token_obj.delete()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        except EmailVerificationToken.DoesNotExist:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

class FollowAPIView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, username, *args, **kwargs):
        followuser = get_object_or_404(CustomUser, username=username)

        if request.user == followuser:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
        
        if followuser.is_private:
            follow_request, created = FollowRequest.objects.get_or_create(from_user=request.user, to_user=followuser)

            if not created:
                return Response({"message": "Follow request already sent"}, status=status.HTTP_200_OK)
            return Response({"message": f"Follow request sent to {followuser.username}"}, status=status.HTTP_201_CREATED) 
        
        follow, created = Follow.objects.get_or_create(follower=request.user, following=followuser)
        if not created:
            return Response({"message": "You already follow this account"}, status=status.HTTP_200_OK)
        return Response( {"message": f"You are now following {followuser.username}"},status=status.HTTP_201_CREATED)

class UnfollowAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        username = kwargs.get("username")

        unfollowuser =  get_object_or_404(CustomUser, username=username)
        try:
            follow = Follow.objects.get(follower=request.user, following=unfollowuser)
            follow.delete()
            return Response({"message": "Unfollowed"}, status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            return Response({"error": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)
    
class FollowersListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username, *args, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        followers = Follow.objects.filter(following=user).select_related("follower")
        usernames = [f.follower.username for f in followers]

        return Response({"followers": usernames}, status=status.HTTP_200_OK)
    
class FollowingListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username, *args, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        following = Follow.objects.filter(follower=user).select_related("following")
        usernames = [f.following.username for f in following]

        return Response({"following": usernames}, status=status.HTTP_200_OK)

class FollowRequestListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        requests = FollowRequest.objects.filter(to_user=request.user).select_related("from_user")
        usernames = [r.from_user.username for r in requests]
        return Response({"requests": usernames}, status=status.HTTP_200_OK)
    
class FollowRequestAcceptOrRejectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username, *args, **kwargs):
        from_user = get_object_or_404(CustomUser, username=username)

        try:
            follow_request = FollowRequest.objects.get(from_user=from_user, to_user=request.user)

        except FollowRequest.DoesNotExist:
            return Response({"error": "No follow request from this user"}, status=status.HTTP_404_NOT_FOUND)
        
        action = request.data.get("action")
        if action == "accept":
            Follow.objects.create(follower=from_user, following=request.user)
            follow_request.delete()
            return Response({"message": f"{from_user.username} started following you"},status=status.HTTP_200_OK)
        
        elif action == "reject":
            follow_request.delete()
            return Response({"message": "Follow request rejected"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)