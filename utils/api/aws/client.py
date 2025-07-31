"""
AWS client utilities for the Django Project Template.
"""

import boto3
from django.conf import settings


class AWSClient:
    """AWS client for interacting with AWS services."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.client = None

    def get_client(self):
        """Get AWS client instance."""
        if not self.client:
            self.client = boto3.client(
                self.service_name,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
        return self.client