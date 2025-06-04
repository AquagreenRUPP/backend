from django.urls import path
from .otp import OTPRequestView, OTPVerifyView

urlpatterns = [
    path('request/', OTPRequestView.as_view(), name='otp-request'),
    path('verify/', OTPVerifyView.as_view(), name='otp-verify'),
]
