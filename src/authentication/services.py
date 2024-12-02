# src/authentication/services.py
import hashlib
import hmac
import secrets
import time

import redis

from django.conf import settings
from django.db import transaction

from .models import User


class TelegramAuthService:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)

    def generate_auth_token(self) -> str:
        """Генерирует безопасный токен для Telegram auth."""
        token = secrets.token_urlsafe(32)
        self.redis_client.setex(token, settings.TELEGRAM_AUTH_TOKEN_EXPIRATION, "valid")
        return token

    def validate_telegram_data(self, data: dict) -> bool:
        """Проверяет данные от Telegram."""
        required_fields = ["auth_date", "hash"]
        if not all(field in data for field in required_fields):
            raise KeyError(f"Отсутствуют обязательные поля: {', '.join(required_fields)}")

        auth_date = int(data.get("auth_date", 0))
        if time.time() - auth_date > 86400:
            return False

        check_hash = data.pop("hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()) if v is not None)
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        return hmac.compare_digest(hmac_hash, check_hash)

    def create_or_update_user(self, telegram_data: dict) -> User:
        """Создает или обновляет пользователя с данными из Telegram."""
        telegram_id = telegram_data["id"]
        telegram_username = telegram_data.get("username")
        first_name = telegram_data.get("first_name", "")
        last_name = telegram_data.get("last_name", "")

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(telegram_id=telegram_id)
                # Обновляем данные пользователя
                user.first_name = first_name
                user.last_name = last_name
                user.telegram_username = telegram_username
                if telegram_username:
                    user.username = self.get_unique_username(telegram_username, user.id)
                user.save()
        except User.DoesNotExist:
            # Создаём нового пользователя
            base_username = telegram_username if telegram_username else f"tg_user_{telegram_id}"
            username = self.get_unique_username(base_username)

            user = User.objects.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                telegram_username=telegram_username,
                password=secrets.token_urlsafe(16),
            )

        return user

    def get_unique_username(self, base_username: str, user_id=None) -> str:
        """Генерирует уникальное имя пользователя, избегая коллизий."""
        max_length = User._meta.get_field("username").max_length

        # Если имя уже подходящей длины и уникально, возвращаем его
        if len(base_username) <= max_length:
            username = base_username
            existing_user = User.objects.filter(username=username)
            if user_id:
                existing_user = existing_user.exclude(id=user_id)
            if not existing_user.exists():
                return username

        # Если требуется модификация имени
        base_username = base_username[: max_length - 2]  # Оставляем место для '_n'
        username = base_username
        index = 0

        while True:
            if index > 0:
                suffix = f"_{index}"
                username_length = len(base_username) + len(suffix)
                if username_length > max_length:
                    base_username = base_username[: max_length - len(suffix)]
                username = f"{base_username}{suffix}"

            existing_user = User.objects.filter(username=username)
            if user_id:
                existing_user = existing_user.exclude(id=user_id)

            if not existing_user.exists():
                break

            index += 1

        return username
