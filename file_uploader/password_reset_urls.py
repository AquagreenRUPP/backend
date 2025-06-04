from django.urls import path
from .password_reset import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
