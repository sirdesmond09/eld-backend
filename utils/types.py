"""
Type definitions for the Django Project Template.
"""

from typing import IO, Any, Dict, List, TypedDict


class Email(TypedDict):
    """
    Represents an email structure with required and optional fields.
    """

    subject: str
    from_email: str
    to_email: List[str]
    template: str
    context: Dict[str, Any]
    attachment: IO = None


class SESEmail(TypedDict):
    """
    Represents an AWS SES email structure.
    """

    Source: str
    Destination: Dict[str, List[str]]
    Message: Dict[str, Any]
    RawMessage: Dict[str, str] = None
    HasAttachment: bool = False


class MailPitEmail(TypedDict):
    """
    Represents a Mailpit email structure for development.
    """

    subject: str
    from_email: str
    to: List[str]
    body: str
    attachment: tuple = None
