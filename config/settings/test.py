# config/settings/test.py

from .base import *  # noqa: F403


# GENERAL
# ------------------------------------------------------------------------------
SECRET_KEY = "test-secret-key-123"
DEBUG = False
TEMPLATES[0]["OPTIONS"]["debug"] = False  # noqa: F405

# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa: F405

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# REDIS
# ------------------------------------------------------------------------------
REDIS_URL = "redis://redis:6379/1"  # Используем отдельную БД Redis для тестов

# TELEGRAM
# ------------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = "test-bot-token"
TELEGRAM_BOT_USERNAME = "test_bot"
