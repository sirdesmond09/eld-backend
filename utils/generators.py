"""
Utility generators for the Django Project Template.
"""

import hashlib
import logging
import random
import re
import secrets
import string
import uuid
from string import ascii_lowercase, ascii_uppercase, digits

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def generate_md5_hash(input_string):
    """
    Generate an MD5 hash for the given input string.

    Args:
        input_string (str): The input string to hash.

    Returns:
        str: The resulting MD5 hash in hexadecimal format.
    """

    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode("utf-8"))
    return md5_hash.hexdigest()


def generate_random_password():
    """Generate a random valid password
    Valid Password:
        min length: 8
        contains at least one uppercase letter
        contains at least one lowercase letter
        contains at least one digit
        contains at least one special character
    """

    char_sets = {
        "upper": ascii_uppercase,
        "lower": ascii_lowercase,
        "digits": digits,
        "special": '[!@#$%^&*(),.?":{}|<>]',
    }
    attempts, max_attempts = 0, 5

    while attempts < max_attempts:
        mandatory_chars = [secrets.choice(chars) for chars in char_sets.values()]
        random_part = secrets.token_urlsafe(4)
        combined_string = random_part + "".join(mandatory_chars)

        # randomize password string
        password = "".join(random.sample(combined_string, len(combined_string)))
        match = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        if not match:
            continue  # Skip if no special character is found to avoid raising a 400 error

        try:
            validate_password(password)
            return password
        except ValidationError as e:
            logger.exception(f"Password validation error: {e}")
            attempts += 1

    raise ValueError("Failed to generate a valid password after multiple attempts.")


def generate_random_string(length: int = 10) -> str:
    """
    Generate a random string with specified length.

    Args:
        length: Length of the string (default: 10)

    Returns:
        Random string
    """
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def generate_random_token(length: int = 32) -> str:
    """
    Generate a random token with specified length.

    Args:
        length: Length of the token (default: 32)

    Returns:
        Random token string
    """
    return secrets.token_urlsafe(length)
