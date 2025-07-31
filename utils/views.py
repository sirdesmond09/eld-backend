from functools import wraps
from django.utils.decorators import method_decorator
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from accounts.permissions import (
    IsEmailVerified,
)
from .exceptions import XSSDetectedException
from rest_framework_simplejwt.authentication import JWTAuthentication


def has_XSS(data):

    data = str(data).lower()
    FORBIDDEN_CHARS = (
        "<script",
        " javascript:",
        " onerror=",
        " onload=",
        " onclick=",
        " onmouseover=",
        " onfocus=",
        " onsubmit=",
    )

    for char in FORBIDDEN_CHARS:
        if char in data:
            return True

    return False


def check_for_XSS(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        data = request.GET or request.POST

        for data_chunk in data.values():
            if has_XSS(str(data_chunk)):
                raise XSSDetectedException

        response = view_func(request, *args, **kwargs)
        return response

    return wrapper


@method_decorator(check_for_XSS, name="dispatch")
class XSSPreventionMixinViewSet(GenericViewSet):
    """XXS attack prevention mixin"""


class CRUDMixinViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """CRUD mixin"""


class CRUDViewSet(CRUDMixinViewSet, XSSPreventionMixinViewSet):
    """Base CRUD Mixin"""


class BaseAuthenticatedViewSet(XSSPreventionMixinViewSet):

    permission_classes = [IsEmailVerified, IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class PubicViewSet(XSSPreventionMixinViewSet):

    permission_classes = [AllowAny]
