from django.contrib.auth import get_user_model, logout
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    AccountLoginSerializer,
    AccountProfileSerializer,
    AccountSignupSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PasswordTokenValidationSerializer,
    ResendEmailVerificationSerializer,
)
from .throttles import PasswordResetThrottle, ResendEmailTokenThrottle
from utils.views import (
    XSSPreventionMixinViewSet,
    BaseAuthenticatedViewSet
)
from rest_framework.mixins import CreateModelMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()


class AccountSignupViewSet(XSSPreventionMixinViewSet, CreateModelMixin):
    """
    Signup as a user
    """

    http_method_names = ["post"]
    serializer_class = AccountSignupSerializer
    queryset = User.objects.all()

    @extend_schema(
        request=AccountSignupSerializer,
        description="Signup as a user",
        responses={201: AccountSignupSerializer},
        methods=["POST"],
    )
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuthenticationViewSet(XSSPreventionMixinViewSet):
    """
    auth as a user
    """

    serializer_class = AccountLoginSerializer
    queryset = User.objects.all()

    @extend_schema(
        description="Login a user",
        responses={204: None},
        methods=["POST"],
    )
    @action(
        detail=False,
        methods=["POST"],
    )
    def login(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.perform_authentication(request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def logout(self, request, **kwargs):
        # request.user.auth_token.delete() TODO:
        logout(request)
        return Response(status=status.HTTP_200_OK)


class AccountVerificationViewSet(XSSPreventionMixinViewSet):

    serializer_class = EmailVerificationSerializer
    queryset = User.objects.filter(is_active=True)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EmailVerificationSerializer,
        description="verify user's email",
        responses={200: EmailVerificationSerializer},
        methods=["POST"],
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="email",
        serializer_class=EmailVerificationSerializer,
    )
    def verify_email(self, request, **kwargs):
        """Verify email with token"""
        serializer = self.get_serializer(request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        description="resend verification token for user's email",
        responses={200: ResendEmailVerificationSerializer},
        methods=["POST"],
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="resend-email-token",
        serializer_class=ResendEmailVerificationSerializer,
        throttle_classes=[ResendEmailTokenThrottle],
    )
    def resend_email_token(self, request, **kwargs):
        """Resend verification email"""
        serializer = self.serializer_class(request.user)
        serializer.resend_email_verification()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetViewSet(XSSPreventionMixinViewSet):
    serializer_class = PasswordResetRequestSerializer
    queryset = User.objects.all()
    lookup_field = "forgot_password_token"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        description="Request a token for password reset.",
        responses={200: None},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="request-token",
        serializer_class=PasswordResetRequestSerializer,
        throttle_classes=[PasswordResetThrottle],
    )
    def request_password_reset_token(self, request):
        """Handles password reset token generation and email sending."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.request_password_token()
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        description="Verify token and reset password.",
        responses={200: None},
        methods=["GET", "POST"],
    )
    @action(
        detail=True,
        methods=["GET", "POST"],
        url_path="reset",
        serializer_class=PasswordResetConfirmSerializer,
    )
    def reset_password(self, request, **kwargs):
        """Handles password reset using the token."""
        user = self.get_object()
        serializer = self.get_password_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def get_password_serializer(self, **kwargs):
        """Returns the appropriate serializer for password reset."""
        if self.request.method == "GET":
            return PasswordTokenValidationSerializer(**kwargs)
        return PasswordResetConfirmSerializer(**kwargs)


class AccountProfileViewSet(BaseAuthenticatedViewSet):
    """
    Update a User's profile
    """

    http_method_names = ["patch", "get"]
    queryset = User.objects.filter(is_active=True)
    serializer_class = AccountProfileSerializer

    @extend_schema(
        request=AccountProfileSerializer,
        description="Update a user's profile",
        responses={200: AccountProfileSerializer},
        methods=["PATCH", "GET"],
    )
    @action(
        detail=False,
        methods=["PATCH", "GET"],
        url_path="profile",
        serializer_class=AccountProfileSerializer,
    )
    def profile(self, request, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)




class ChangePasswordViewSet(BaseAuthenticatedViewSet):
    serializer_class = ChangePasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
