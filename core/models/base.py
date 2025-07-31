"""
Base models for the Django Project Template.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampModel(models.Model):
    """
    Base model class with common fields.

    Fields:
        - created_at (datetime): Time at which the model instance was created.
        - updated_at (datetime): Time at which the model instance was last updated.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TimeStampUUIDModel(TimeStampModel):
    """
    Base model class with common fields.

    Fields:
        - uid (UUID): Unique identifier for the model.
    """

    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class BaseUserModel(models.Model):
    """
    Abstract base model for user-related models.
    """

    uid = models.UUIDField(
        _("Unique Identifier"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    is_active = models.BooleanField(_("Active"), default=True)
    is_deleted = models.BooleanField(_("Deleted"), default=False)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.__class__.__name__} - {self.uid}"


class BaseFile(TimeStampUUIDModel):
    """
    Base model class for files.
    """

    file = models.FileField(_("File"), blank=True, null=True)
    name = models.CharField(_("File Name"), max_length=255, blank=True, null=True)
    category = models.CharField(_("Category"), max_length=150, blank=True, null=True)
    key = models.CharField(_("AWS Upload Key"), max_length=255, blank=True, null=True)
    extension = models.CharField(
        _("File Extension"), max_length=10, blank=True, null=True
    )
    size = models.IntegerField(_("File Size"), blank=True, null=True)
    uploaded = models.BooleanField(_("Uploaded"), default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.file.name} - {self.created_at}"

    @property
    def request_id(self):
        return f"{self.category}.{self.uid}"


 