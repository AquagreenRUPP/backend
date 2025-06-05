from django.urls import path
from .password_reset_with_otp import (
    PasswordResetRequestOTPView, 
    VerifyResetCodeView,
    ResetPasswordWithCodeView
)

urlpatterns = [
    path('request-code/', PasswordResetRequestOTPView.as_view(), name='password_reset_request_otp'),
    path('verify-code/', VerifyResetCodeView.as_view(), name='verify_reset_code'),
    path('reset-with-code/', ResetPasswordWithCodeView.as_view(), name='reset_password_with_code'),
]
