"""
Validators for the Django Project Template.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

from utils.exceptions import (
    DigitMissingException,
    LowerCaseMissingException,
    SpecialCharMissingException,
    UpperCaseMissingException,
)


def validate_phone_number(value):
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", value)

    # Check if it's a valid phone number (7-15 digits)
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValidationError(_("Phone number must be between 7 and 15 digits."))

    # Check if it contains only valid characters
    if not re.match(r"^[\d\s\-\+\(\)]+$", value):
        raise ValidationError(_("Phone number contains invalid characters."))


def validate_username(value):
    """Validate username format."""
    if len(value) < 3:
        raise ValidationError(_("Username must be at least 3 characters long."))

    if len(value) > 30:
        raise ValidationError(_("Username must be no more than 30 characters long."))

    # Check for valid characters (letters, numbers, underscores, hyphens)
    if not re.match(r"^[a-zA-Z0-9_-]+$", value):
        raise ValidationError(
            _("Username can only contain letters, numbers, underscores, and hyphens.")
        )

    # Check if it starts with a letter or number
    if not re.match(r"^[a-zA-Z0-9]", value):
        raise ValidationError(_("Username must start with a letter or number."))


def validate_password_strength(value):
    """Validate password strength."""
    if len(value) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))

    if not re.search(r"[A-Z]", value):
        raise ValidationError(_("Password must contain at least one uppercase letter."))

    if not re.search(r"[a-z]", value):
        raise ValidationError(_("Password must contain at least one lowercase letter."))

    if not re.search(r"\d", value):
        raise ValidationError(_("Password must contain at least one digit."))

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            _("Password must contain at least one special character.")
        )


def validate_file_size(value, max_size_mb=10):
    """Validate file size."""
    max_size_bytes = max_size_mb * 1024 * 1024

    if value.size > max_size_bytes:
        raise ValidationError(
            _("File size must be no more than %(max_size)s MB."),
            params={"max_size": max_size_mb},
        )


def validate_file_extension(value, allowed_extensions):
    """Validate file extension."""
    import os

    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            _("File type not allowed. Allowed types: %(allowed_types)s."),
            params={"allowed_types": ", ".join(allowed_extensions)},
        )


def validate_image_file(value):
    """Validate image file."""
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    validate_file_extension(value, allowed_extensions)
    validate_file_size(value, max_size_mb=10)


def validate_document_file(value):
    """Validate document file."""
    allowed_extensions = [".pdf", ".doc", ".docx", ".txt", ".csv"]
    validate_file_extension(value, allowed_extensions)
    validate_file_size(value, max_size_mb=50)


def validate_url(value):
    """Validate URL format."""
    import re

    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(value):
        raise ValidationError(_("Enter a valid URL."))


def validate_postal_code(value):
    """Validate postal code format."""
    # Basic postal code validation (can be customized per country)
    if not re.match(r"^[A-Z0-9\s\-]{3,10}$", value.upper()):
        raise ValidationError(_("Enter a valid postal code."))


def validate_alpha_only(value):
    """Validate that value contains only alphabetic characters."""
    if not re.match(r"^[A-Za-z\s]+$", value):
        raise ValidationError(_("This field can only contain letters and spaces."))


def validate_alphanumeric(value):
    """Validate that value contains only alphanumeric characters."""
    if not re.match(r"^[A-Za-z0-9\s]+$", value):
        raise ValidationError(
            _("This field can only contain letters, numbers, and spaces.")
        )


def validate_no_special_chars(value):
    """Validate that value contains no special characters."""
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', value):
        raise ValidationError(_("This field cannot contain special characters."))


def validate_min_length(value, min_length):
    """Validate minimum length."""
    if len(value) < min_length:
        raise ValidationError(
            _("This field must be at least %(min_length)s characters long."),
            params={"min_length": min_length},
        )


def validate_max_length(value, max_length):
    """Validate maximum length."""
    if len(value) > max_length:
        raise ValidationError(
            _("This field must be no more than %(max_length)s characters long."),
            params={"max_length": max_length},
        )


class MustHaveUpperCaseCharacter:
    def validate(self, password, user=None):
        matched = re.search(r"[A-Z]", password)
        if not matched:
            raise UpperCaseMissingException

    def get_help_text(self):
        return _("Your password must contain at least one uppercase character.")


class MustHaveLowerCaseCharacter:
    def validate(self, password, user=None):
        matched = re.search(r"[a-z]", password)
        if not matched:
            raise LowerCaseMissingException

    def get_help_text(self):
        return _("Your password must contain at least one lowercase character.")


class MustHaveDigit:
    def validate(self, password, user=None):
        matched = re.search(r"\d", password)
        if not matched:
            raise DigitMissingException

    def get_help_text(self):
        return _("Your password must contain at least one number.")


class MustHaveSpecialCharacter:
    def validate(self, password, user=None):
        matched = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        if not matched:
            raise SpecialCharMissingException

    def get_help_text(self):
        return _("Your password must contain at least one special character.")


TimeRangeValidator = RegexValidator(
    regex=r"^(?:[01]\d|2[0-3]):[0-5]\d - (?:[01]\d|2[0-3]):[0-5]\d$",
    message=_("Enter a valid time range in HH:MM - HH:MM format (24-hour clock)."),
)


# def validate_time_range_within_bounds(value):
#     """Ensure the time range is between 00:00 and 23:59."""

#     start_time_str, end_time_str = value.split(" - ")
#     start_time = datetime.strptime(start_time_str, "%H:%M").time()
#     end_time = datetime.strptime(end_time_str, "%H:%M").time()

#     if not (
#         start_time <= end_time
#         and start_time >= datetime.strptime("00:00", "%H:%M").time()
#         and end_time <= datetime.strptime("23:59", "%H:%M").time()
#     ):
#         raise TimeRangeValidationException


@deconstructible
class AllowableUsernameValueValidator(RegexValidator):
    regex = r"^[a-zA-Z0-9]+$"
    message = _(
        "Enter a valid username. This value may contain only letters, " "numbers"
    )
    flags = 0
