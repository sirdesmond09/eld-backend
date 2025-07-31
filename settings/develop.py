"""
Development settings for Django Project Template.
"""

import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Debug toolbar
# if DEBUG:
#     INSTALLED_APPS += ["debug_toolbar"]
#     MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
#     INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Celery settings for development
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

# Cache settings for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Static files for development
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Media files for development
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

