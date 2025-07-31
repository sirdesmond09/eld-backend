from abc import ABC, abstractmethod
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class BaseEmail(ABC):
    """Base class for sending HTML emails with optional attachments."""

    def __init__(self, instance, attachment=None):
        self.instance = instance
        self.attachment = attachment

    @property
    @abstractmethod
    def subject(self):
        """Subject of the email."""
        pass

    @property
    @abstractmethod
    def template_name(self):
        """Template name for the email."""
        pass

    @property
    @abstractmethod
    def to_email(self):
        """Recipient email address."""
        pass

    @property
    @abstractmethod
    def context(self):
        """Context data for rendering the email template."""
        pass

    def render_template(self):
        """Render the email template with context data."""
        return render_to_string(self.template_name, self.context)

    def send_email(self):
        """Send the email with optional attachment."""
        email_content = self.render_template()
        email = EmailMessage(
            subject=self.subject,
            body=email_content,
            to=self.to_email,
        )
        email.content_subtype = "html"

        if self.attachment:
            email.attach_file(self.attachment)

        email.send()
