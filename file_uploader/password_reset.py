from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist for security reasons
            return Response(
                {"success": "If your email is registered, you will receive a password reset link"},
                status=status.HTTP_200_OK
            )
        
        # Generate token and UID
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Create reset link
        # In production, this should be an actual frontend URL
        reset_link = f"http://localhost:8080/reset-password/{uid}/{token}/"
        
        # Email subject and message
        subject = "AquaGreen Monitoring - Password Reset"
        message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_link': reset_link,
            'site_name': 'AquaGreen Monitoring',
        })
        
        # Send email
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message,
            )
            return Response(
                {"success": "Password reset link has been sent to your email"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        # Check if this is a direct reset with email or token-based reset
        is_direct_reset = email is not None
        
        if not new_password:
            return Response(
                {"error": "New password is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not is_direct_reset and (not uid or not token):
            return Response(
                {"error": "UID and token are required for token-based reset"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password
        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response(
                {"error": " ".join(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if is_direct_reset:
                # Direct reset with email
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    # Don't reveal that the user doesn't exist for security reasons
                    return Response(
                        {"success": "Password has been reset successfully"},
                        status=status.HTTP_200_OK
                    )
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                return Response(
                    {"success": "Password has been reset successfully"},
                    status=status.HTTP_200_OK
                )
            else:
                # Token-based reset
                try:
                    # Decode the user ID
                    user_id = force_str(urlsafe_base64_decode(uid))
                    user = User.objects.get(pk=user_id)
                    
                    # Check if token is valid
                    if not default_token_generator.check_token(user, token):
                        return Response(
                            {"error": "Invalid or expired token"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Set new password
                    user.set_password(new_password)
                    user.save()
                    
                    return Response(
                        {"success": "Password has been reset successfully"},
                        status=status.HTTP_200_OK
                    )
                except (TypeError, ValueError, User.DoesNotExist):
                    return Response(
                        {"error": "Invalid reset link"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
