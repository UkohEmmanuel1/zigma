from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    ChangePasswordView,
    ForgotPasswordView,
    LoginView,
    RegisterView,
    ResetPasswordView,
    UserMeView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserMeView.as_view(), name="user-me"),
    path("change-password/", ChangePasswordView.as_view(), name="user-change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="user-forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="user-reset-password"),
]
