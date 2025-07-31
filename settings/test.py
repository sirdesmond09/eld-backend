from .base import *

ALLOWED_HOSTS = ["testserver"]
TESTS = True
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
}

BASE_URL = "http://127.0.0.1:8000"

AWS_REGION = ""
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_STORAGE_BUCKET_NAME = ""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
DEBUG = True

CELERY_BROKER_URL = "memory://"

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]