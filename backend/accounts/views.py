from django.shortcuts import render
from rest_framework import generics, status
from .models import CustomUser, EmailVerificationToken
from .serializers import CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings

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

class CustomUserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        
        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import authenticate

        customuser = authenticate(request, email=email, password=password)

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
