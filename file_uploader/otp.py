import random
import string
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

User = get_user_model()

# Store OTP codes with expiration times in memory
# In production, consider using a database or cache (Redis)
otp_store = {}

def generate_otp(length=6):
    """Generate a random OTP code with specified length"""
    return ''.join(random.choices(string.digits, k=length))

def store_otp(email, otp, expiry_minutes=10):
    """Store OTP with expiration time"""
    expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
    otp_store[email] = {
        'otp': otp,
        'expiry_time': expiry_time
    }

def verify_otp(email, otp):
    """Verify if OTP is valid and not expired"""
    if email not in otp_store:
        return False
    
    stored_data = otp_store[email]
    if stored_data['expiry_time'] < datetime.now():
        # OTP expired, remove it
        del otp_store[email]
        return False
    
    if stored_data['otp'] != otp:
        return False
    
    # OTP verified successfully, remove it to prevent reuse
    del otp_store[email]
    return True

class OTPRequestView(APIView):
    """API view for requesting an OTP code"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not (security best practice)
            return Response(
                {'message': 'If your email is registered, you will receive an OTP code shortly.'}, 
                status=status.HTTP_200_OK
            )
        
        # Generate OTP
        otp = generate_otp()
        store_otp(email, otp)
        
        # Send OTP via email
        subject = 'Your OTP Code for AquaGreen Monitoring'
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
        
        return Response(
            {'message': 'If your email is registered, you will receive an OTP code shortly.'}, 
            status=status.HTTP_200_OK
        )

class OTPVerifyView(APIView):
    """API view for verifying an OTP code"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        registration = request.data.get('registration', False)  # Flag to indicate if this is for account registration
        
        if not email or not otp:
            return Response(
                {'error': 'Email and OTP are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify OTP
        if verify_otp(email, otp):
            try:
                user = User.objects.get(email=email)
                
                # If this is for registration and user is inactive, activate the account
                if registration and not user.is_active:
                    user.is_active = True
                    user.save()
                    
                    # Generate tokens for the now-verified user
                    from rest_framework_simplejwt.tokens import RefreshToken
                    from .serializers import UserSerializer
                    
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'verified': True, 
                        'message': 'Account verified successfully',
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                else:
                    # For non-registration OTP verification
                    user.is_verified = True  # Assuming you have this field for other verifications
                    user.save()
                    
                    return Response(
                        {'verified': True, 'message': 'OTP verified successfully'}, 
                        status=status.HTTP_200_OK
                    )
            except User.DoesNotExist:
                # Don't reveal if user exists or not
                return Response(
                    {'verified': False, 'error': 'Verification failed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {'verified': False, 'error': 'Invalid or expired OTP'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
