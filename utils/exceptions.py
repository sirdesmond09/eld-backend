import logging
from typing import Any, Dict

from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class CustomAPIException(ValidationError):
    """
    Custom API exception class for handling specific error scenarios.

    Attributes:
        error_code (str): A string representing the error code.
        status_code (int): The HTTP status code for the exception.
        default_bad_request_message (str): Default message for bad requests.
        default_message (str): Default message for general processing errors.
        default_does_not_exists_message (str): Default message for non-existent resources.

    Methods:
        __init__(detail=None, code=None): Initializes the exception with a custom
        detail message and status code, defaulting to predefined messages and codes
        if not provided.
    """

    error_code = "UNKNOWN"
    status_code = status.HTTP_400_BAD_REQUEST
    default_bad_request_message = _("Bad request")
    default_message = _(
        "We are unable to process your request at this time. Please try again."
    )
    default_does_not_exists_message = _("Requested resource does not exist")

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_message
        if code is None:
            code = self.status_code
        super().__init__(detail, code)

    def get_custom_exception_message_for_auth(self):
        return self.default_message


def api_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Custom exception handler for API views.

    Args:
        exc: The exception instance.
        context: Additional context about the exception.

    Returns:
        Response: A DRF Response object with appropriate error details.
    """
    response = exception_handler(exc, context)
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return response

    if isinstance(exc, ValidationError):
        error_detail = (
            exc.detail
            if isinstance(exc.detail, dict)
            else {getattr(exc, "error_code", "error"): exc.detail}
        )
        return Response(error_detail, status=response.status_code)

    return response


# ############################### Api Exceptions ##############################


class AuthFailureException(CustomAPIException):
    """Raised for authentication failures."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTH_FAILURE"
    default_message = "Invalid email or password."


class UserMissingException(CustomAPIException):
    """Raised when a user is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "USER_MISSING"
    default_message = "User does not exist."


class UpperCaseMissingException(CustomAPIException):
    """Raised when password lacks an uppercase character."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "UPPERCASE_MISSING"
    default_message = "Password needs an uppercase character."


class LowerCaseMissingException(CustomAPIException):
    """Raised when password lacks a lowercase character."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "LOWERCASE_MISSING"
    default_message = "Password needs a lowercase character."


class DigitMissingException(CustomAPIException):
    """Raised when password lacks a digit."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "DIGIT_MISSING"
    default_message = "Password needs a digit."


class SpecialCharMissingException(CustomAPIException):
    """Raised when password lacks a special character."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "SPECIAL_CHAR_MISSING"
    default_message = "Password needs a special character."


class TokenInvalidException(CustomAPIException):
    """Raised for invalid tokens."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "TOKEN_INVALID"
    default_message = "Token is invalid or expired."


class PreconditionException(CustomAPIException):
    """Raised when a precondition is unmet."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "PRECONDITION_UNMET"
    default_message = "Precondition unmet for this action."





class PasswordErrorException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "PASSWORD_ERROR"
    default_message = "Incorrect password."


class RateFormatException(CustomAPIException):
    """Raised for rate format errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "RATE_FORMAT_ERROR"
    default_message = "Rate format is invalid."


class EndpointThrottledException(CustomAPIException):
    """Raised when an endpoint is throttled."""

    status_code = 429
    error_code = "ENDPOINT_THROTTLED"
    default_message = "Please wait before retrying."


class EmptyStringException(CustomAPIException):
    """Raised when an empty string is not allowed."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "EMPTY_STRING_NOT_ALLOWED"
    default_message = "Field cannot be empty."


class XSSDetectedException(CustomAPIException):
    """Raised when a potential XSS attack is detected."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "XSS_DETECTED"
    default_message = "Remove scripts or javascript code."


class BooleanValueException(CustomAPIException):
    """Raised when a value is not boolean."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "BOOLEAN_VALUE_ERROR"
    default_message = "Value must be true or false."


class DictionaryValueException(CustomAPIException):
    """Raised when a value must be a dictionary."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "DICTIONARY_VALUE_ERROR"
    default_message = "Value must be a dictionary."





class NullFieldsException(CustomAPIException):
    """Raised when all fields are null."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "NULL_FIELDS_ERROR"
    default_message = "All fields cannot be null."


class ValueErrorException(CustomAPIException):
    """Raised for custom value errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "VALUE_ERROR"
    default_message = "A custom value error occurred."


class ValidationErrorException(CustomAPIException):
    """Raised for custom validation errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "VALIDATION_ERROR"
    default_message = "A custom validation error occurred."


class PaymentAmountException(CustomAPIException):
    """Raised for invalid payment amounts."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "PAYMENT_AMOUNT_ERROR"
    default_message = "Payment amount is invalid."


class ExternalRequestException(CustomAPIException):
    """Raised when an external request fails."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "EXTERNAL_REQUEST_ERROR"
    default_message = "External request failed."


class UserPermissionException(CustomAPIException):
    """Raised when a user lacks permission."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "USER_PERMISSION_ERROR"
    default_message = "You do not permission for this action." 