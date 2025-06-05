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
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

# Store verification codes with expiration times in memory
# In production, consider using a database or cache (Redis)
reset_code_store = {}

def generate_reset_code(length=6):
    """Generate a random reset code with specified length"""
    return ''.join(random.choices(string.digits, k=length))

def store_reset_code(email, code, expiry_minutes=10):
    """Store reset code with expiration time"""
    expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
    reset_code_store[email] = {
        'code': code,
        'expiry_time': expiry_time
    }

def verify_reset_code(email, code):
    """Verify if reset code is valid and not expired"""
    if email not in reset_code_store:
        return False
    
    stored_data = reset_code_store[email]
    if stored_data['expiry_time'] < datetime.now():
        # Code expired, remove it
        del reset_code_store[email]
        return False
    
    if stored_data['code'] != code:
        return False
    
    # Code verified successfully, but don't remove it yet
    # We'll remove it after password is reset successfully
    return True

def clear_reset_code(email):
    """Remove reset code after successful password reset"""
    if email in reset_code_store:
        del reset_code_store[email]

class PasswordResetRequestOTPView(APIView):
    """API view for requesting a password reset verification code"""
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
                {'message': 'If your email is registered, you will receive a verification code shortly.'}, 
                status=status.HTTP_200_OK
            )
        
        # Generate reset code
        reset_code = generate_reset_code()
        store_reset_code(email, reset_code)
        
        # Send reset code via email
        subject = 'Password Reset Verification Code - AquaGreen Monitoring'
        html_message = render_to_string('reset_code_email.html', {
            'reset_code': reset_code,
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
            print(f"Error sending reset code email: {str(e)}")
        
        return Response(
            {'message': 'If your email is registered, you will receive a verification code shortly.'}, 
            status=status.HTTP_200_OK
        )

class VerifyResetCodeView(APIView):
    """API view for verifying a password reset code"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response(
                {'error': 'Email and verification code are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify reset code
        if verify_reset_code(email, code):
            return Response(
                {'verified': True, 'message': 'Verification code accepted'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'verified': False, 'error': 'Invalid or expired verification code'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class ResetPasswordWithCodeView(APIView):
    """API view for resetting password after code verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not email or not code or not new_password:
            return Response(
                {'error': 'Email, verification code, and new password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the reset code again
        if not verify_reset_code(email, code):
            return Response(
                {'error': 'Invalid or expired verification code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password
        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response(
                {'error': ' '.join(e.messages)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset password
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear the reset code after successful password reset
            clear_reset_code(email)
            
            return Response(
                {'success': True, 'message': 'Password reset successfully'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
