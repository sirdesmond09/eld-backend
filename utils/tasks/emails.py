"""
Email tasks for Celery background processing.
"""

import logging

from django.core.mail import EmailMessage
from core.celery import app
from utils.types import MailPitEmail, SESEmail

from ..api.aws.client import AWSClient

logger = logging.getLogger(__name__)


@app.task(name="Send SES Email")
def send_email_using_ses(email: SESEmail) -> bool:
    """Async task to send emails using AWS SES."""
    client = AWSClient("ses").get_client()
    try:
        if email.get("HasAttachment", False):
            client.send_raw_email(
                Source=email["Source"],
                Destinations=email["Destination"]["ToAddresses"],
                RawMessage={
                    "Data": email["RawMessage"]["Data"],
                },
            )
        else:
            client.send_email(
                Source=email["Source"],
                Destination={
                    "ToAddresses": email["Destination"]["ToAddresses"],
                },
                Message=email["Message"],
            )
        logger.debug(
            f"Email sent successfully to {', '.join(email['Destination']['ToAddresses'])}"
        )
        return True
    except Exception as e:
        logger.exception(f"An error occurred while sending SES mail: {e}")
        return False


@app.task(name="Send Mailpit Email")
def send_email_using_mailpit(email: MailPitEmail):
    """Async task to send emails using Mailpit (development)."""
    try:
        mailpit = EmailMessage(
            subject=email["subject"],
            body=email["body"],
            from_email=email["from_email"],
            to=email["to"],
        )
        mailpit.content_subtype = "html"
        if attachment := email.get("attachment"):
            mailpit.attach_file(attachment)
        logger.debug(f"Sending email to {', '.join(email['to'])}")
        mailpit.send()
        return True
    except Exception as e:
        logger.exception(f"An error occurred while sending mailpit mail: {e}")
        return False
