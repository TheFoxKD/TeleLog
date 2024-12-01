# apps/authentication/services.py

import hashlib
import hmac
import secrets
import time

import redis
from django.conf import settings

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
        auth_date = int(data.get("auth_date", 0))
        if time.time() - auth_date > 86400:
            return False  # Данные устарели

        check_hash = data.pop("hash")
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data.items())])
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        hmac_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(hmac_hash, check_hash)

    def create_or_update_user(self, telegram_data: dict) -> User:
        """Создает или обновляет пользователя с данными из Telegram."""
        telegram_id = telegram_data["id"]
        telegram_username = telegram_data.get("username")
        first_name = telegram_data.get("first_name", "")
        last_name = telegram_data.get("last_name", "")

        # Если Telegram username отсутствует, генерируем его на основе ID
        if not telegram_username:
            telegram_username = f"tg_user_{telegram_id}"

        # Проверяем, существует ли пользователь с таким telegram_id
        try:
            user = User.objects.get(telegram_id=telegram_id)
            # Обновляем данные пользователя
            user.username = self.get_unique_username(telegram_username, user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.telegram_username = telegram_username
            user.save()
        except User.DoesNotExist:
            # Генерируем уникальное имя пользователя
            username = self.get_unique_username(telegram_username)
            # Создаём нового пользователя
            user = User.objects.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                telegram_username=telegram_username,
                password=User.objects.make_random_password(),  # Генерируем случайный пароль
            )
        return user

    def get_unique_username(self, base_username: str, user_id=None) -> str:
        """Генерирует уникальное имя пользователя, избегая коллизий."""
        max_length = User._meta.get_field("username").max_length
        base_username = base_username[: max_length - 10]  # Оставляем место для суффикса
        username = base_username
        index = 0
        while True:
            existing_user = (
                User.objects.filter(username=username).exclude(id=user_id).first()
            )
            if not existing_user:
                break
            index += 1
            suffix = f"_{index}"
            username = f"{base_username}{suffix}"
            if len(username) > max_length:
                # Обрезаем, чтобы уложиться в max_length
                username = f"{base_username[:max_length - len(suffix)]}{suffix}"
        return username
