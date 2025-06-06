from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .serializers import UserSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            
            # Validate required fields
            if not username or not email or not password:
                return Response(
                    {"errors": "Username, email, and password are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check duplicates
            if User.objects.filter(username=username).exists():
                return Response(
                    {"errors": "User with this username already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if User.objects.filter(email=email).exists():
                return Response(
                    {"errors": "User with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Password strength
            try:
                validate_password(password)
            except ValidationError as e:
                return Response(
                    {"errors": " ".join(e.messages)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create active user (no OTP required)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            
            # Issue JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "User registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get the user object
            user = User.objects.get(username=request.data.get('username'))
            
            # Add user data to response
            response.data['user'] = UserSerializer(user).data
            response.data['success'] = True
        
        return response

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
