"""
Production settings for Django Project Template.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Session security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# Celery settings for production
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# Cache settings for production
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# # Logging for production
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
#             "style": "{",
#         },
#     },
#     "handlers": {
#         "file": {
#             "level": "INFO",
#             "class": "logging.FileHandler",
#             "filename": "/var/log/django/django.log",
#             "formatter": "verbose",
#         },
#         "console": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#     },
#     "root": {
#         "handlers": ["console", "file"],
#         "level": "INFO",
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console", "file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
# } 