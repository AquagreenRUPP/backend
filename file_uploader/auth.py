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
            # Extract data from request
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            verify_email = request.data.get('verify_email', True)  # Default to requiring verification
            
            # Validate required fields
            if not username or not email or not password:
                return Response(
                    {"errors": "Username, email, and password are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already exists
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
            
            # Validate password strength
            try:
                validate_password(password)
            except ValidationError as e:
                return Response(
                    {"errors": " ".join(e.messages)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create user but set as inactive if email verification is required
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=not verify_email  # Set to inactive if verification required
            )
            
            if verify_email:
                # Import here to avoid circular imports
                from .otp import generate_otp, store_otp
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                from django.conf import settings
                
                # Generate OTP
                otp = generate_otp()
                store_otp(email, otp)
                
                # Send OTP via email
                subject = 'Verify Your AquaGreen Monitoring Account'
                html_message = render_to_string('otp_email.html', {
                    'otp': otp,
                    'user': user,
                    'valid_minutes': 10,
                })
                plain_message = strip_tags(html_message)
                
                try:
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except Exception as e:
                    # Log the error but don't expose details to the client
                    print(f"Error sending OTP email: {str(e)}")
                
                return Response({
                    "success": True,
                    "message": "Registration initiated. Please verify your email with the OTP code sent to your email address.",
                    "requires_verification": True,
                    "email": email
                }, status=status.HTTP_201_CREATED)
            else:
                # For cases where email verification is bypassed (e.g., admin created accounts)
                # Generate tokens for the new user
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "success": True,
                    "message": "User registered successfully",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
