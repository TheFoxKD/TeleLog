# src/telelog/models.py
import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


def default_expires_at():
    return timezone.now() + timedelta(minutes=30)


class AuthenticationToken(models.Model):
    """Model for storing temporary authentication tokens."""

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="auth_tokens",
    )
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expires_at)

    def is_valid(self):
        valid = not self.is_used and self.expires_at > timezone.now()
        logger.debug(f"AuthenticationToken: Token {self.token} is_valid: {valid}")
        return valid

    class Meta:
        verbose_name = "Authentication Token"
        verbose_name_plural = "Authentication Tokens"

    def __str__(self):
        return f"Token {self.token} - {'Used' if self.is_used else 'Active'}"


class TelegramSession(models.Model):
    """Model for storing Telegram session data."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_session",
    )
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    telegram_name = models.CharField(max_length=255, null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Telegram Session"
        verbose_name_plural = "Telegram Sessions"

    def __str__(self):
        return f"Session for {self.user}"
