# tests/conftest.py
import pytest
import redis
from pytest_factoryboy import register

from django.conf import settings
from django.contrib.auth import get_user_model
from src.authentication.services import TelegramAuthService
from tests.factories.users import TelegramUserFactory


register(TelegramUserFactory)

User = get_user_model()


@pytest.fixture
def redis_client():
    """Фикстура для клиента Redis."""
    client = redis.Redis.from_url(settings.REDIS_URL)
    yield client
    client.flushall()


@pytest.fixture
def auth_service(redis_client):
    """Фикстура для сервиса аутентификации."""
    return TelegramAuthService()


@pytest.fixture
def telegram_data():
    """Тестовые данные от Telegram."""
    return {
        "id": "123456789",
        "first_name": "Test",
        "last_name": "User",
        "username": "test_user",
        "auth_date": "1609459200",
    }


@pytest.fixture
def telegram_auth_data(telegram_data):
    """Тестовые данные для аутентификации через Telegram с хешем."""
    data = telegram_data.copy()
    data["hash"] = "valid_hash"
    return data


@pytest.fixture
def mock_telegram_bot_api(monkeypatch):
    """Мокает API Telegram бота."""

    class MockBot:
        def get_me(self):
            return {"username": "test_bot"}

    monkeypatch.setattr("telegram.Bot", lambda *args, **kwargs: MockBot())


@pytest.fixture
def auth_token(auth_service):
    """Создает валидный токен аутентификации."""
    return auth_service.generate_auth_token()
