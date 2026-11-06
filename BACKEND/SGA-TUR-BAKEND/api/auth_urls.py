from django.urls import path
from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView,
    PasswordResetView,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import CustomUserDetailsView

urlpatterns = [
    # URLs que estamos sobrescribiendo
    path("user/", CustomUserDetailsView.as_view(), name="rest_user_details"),

    # URLs que mantenemos de dj_rest_auth
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="rest_password_change"),

    # JWT URLs
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
