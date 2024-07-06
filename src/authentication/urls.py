"""
File that contains the urls of the authentication app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from authentication.views import LoginOTPView, LoginView, LogoutAllView, LogoutView, SendOTPView

APP_NAME = "user"

urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logout_all/", LogoutAllView.as_view(), name="logout_all"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("otp/send/", SendOTPView.as_view(), name="send_otp"),
    path("otp/login/", LoginOTPView.as_view(), name="login_otp"),
]
