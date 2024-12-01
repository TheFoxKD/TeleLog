from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for TeleLog."""

    # Additional fields specific to our needs
    telegram_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_telegram_auth = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username or self.email or str(self.pk)
