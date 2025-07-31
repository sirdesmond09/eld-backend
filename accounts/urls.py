"""
URL configuration for accounts app.
"""

from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    AccountProfileViewSet,
    AccountSignupViewSet,
    AccountVerificationViewSet,
    AuthenticationViewSet,
    ChangePasswordViewSet,
    PasswordResetViewSet,
)

app_name = "accounts"

router = SimpleRouter()

# Account Signup
router.register("", AccountProfileViewSet, "profile")
router.register("signup", AccountSignupViewSet, "accounts")

# Account Profile

# Account Verifications
router.register("verifications", AccountVerificationViewSet, "verifications")

# Account Authentication
router.register("auth", AuthenticationViewSet, "auth")
router.register("auth/change-password", ChangePasswordViewSet, "change-password")
router.register("auth/password", PasswordResetViewSet, "passwords")


urlpatterns = router.urls
