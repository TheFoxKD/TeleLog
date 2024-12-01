# apps/authentication/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.CharField(max_length=32, unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=32, null=True, blank=True)
    auth_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
