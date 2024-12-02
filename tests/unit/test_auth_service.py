# tests/unit/test_auth_service.py
import time
from unittest.mock import patch

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from src.authentication.services import TelegramAuthService


User = get_user_model()


@pytest.mark.django_db
class TestTelegramAuthService:
    """Тесты сервиса аутентификации через Telegram."""

    @pytest.fixture
    def auth_service(self):
        return TelegramAuthService()

    def test_init(self, auth_service):
        """Тест инициализации сервиса."""
        assert isinstance(auth_service, TelegramAuthService)
        assert auth_service.redis_client is not None

    def test_generate_auth_token(self, auth_service, redis_client):
        """Тест генерации токена аутентификации."""
        token = auth_service.generate_auth_token()

        assert isinstance(token, str)
        assert len(token) >= 32
        assert redis_client.exists(token)

        ttl = redis_client.ttl(token)
        assert 0 < ttl <= settings.TELEGRAM_AUTH_TOKEN_EXPIRATION

    @pytest.mark.parametrize(
        "auth_date,expected",
        [
            (int(time.time()), True),
            (int(time.time()) - 86400 + 1, True),
            (int(time.time()) - 86400 - 1, False),
        ],
    )
    def test_validate_telegram_data_auth_date(self, auth_service, telegram_auth_data, auth_date, expected):
        """Тест валидации времени аутентификации."""
        telegram_auth_data["auth_date"] = str(auth_date)

        with patch("hmac.compare_digest", return_value=True):
            assert auth_service.validate_telegram_data(telegram_auth_data) == expected

    def test_validate_telegram_data_invalid_hash(self, auth_service, telegram_auth_data):
        """Тест проверки невалидного хеша."""
        telegram_auth_data["hash"] = "invalid_hash"
        assert not auth_service.validate_telegram_data(telegram_auth_data)

    def test_validate_telegram_data_missing_fields(self, auth_service):
        """Тест валидации с отсутствующими полями."""
        invalid_data = {"id": "123456789"}
        with pytest.raises(KeyError):
            auth_service.validate_telegram_data(invalid_data)

    @patch(
        "src.authentication.services.secrets.token_urlsafe",
        return_value="test_password",
    )
    def test_create_new_user(self, mock_token, auth_service, telegram_data):
        """Тест создания нового пользователя."""
        user = auth_service.create_or_update_user(telegram_data)

        assert user.telegram_id == telegram_data["id"]
        assert user.telegram_username == telegram_data["username"]
        assert user.first_name == telegram_data["first_name"]
        assert user.last_name == telegram_data["last_name"]
        assert user.is_active

        saved_user = User.objects.get(telegram_id=telegram_data["id"])
        assert saved_user == user

    @patch(
        "src.authentication.services.secrets.token_urlsafe",
        return_value="test_password",
    )
    def test_update_existing_user(self, mock_token, auth_service, telegram_data, telegram_user_factory):
        """Тест обновления существующего пользователя."""
        existing_user = telegram_user_factory(
            telegram_id=telegram_data["id"],
            telegram_username="old_username",
            first_name="Old",
            last_name="Name",
        )

        updated_user = auth_service.create_or_update_user(telegram_data)

        assert updated_user.id == existing_user.id
        assert updated_user.telegram_username == telegram_data["username"]
        assert updated_user.first_name == telegram_data["first_name"]
        assert updated_user.last_name == telegram_data["last_name"]

    @patch(
        "src.authentication.services.secrets.token_urlsafe",
        return_value="test_password",
    )
    def test_create_user_without_username(self, mock_token, auth_service, telegram_data):
        """Тест создания пользователя без username в Telegram."""
        telegram_data_no_username = telegram_data.copy()
        del telegram_data_no_username["username"]

        user = auth_service.create_or_update_user(telegram_data_no_username)

        assert user.telegram_id == telegram_data["id"]
        assert user.username == f"tg_user_{telegram_data['id']}"
        assert user.telegram_username is None  # Теперь правильно проверяем telegram_username

    @pytest.mark.parametrize(
        "base_username,existing_usernames,expected",
        [
            ("test_user", [], "test_user"),
            ("test_user", ["test_user"], "test_user_1"),
            ("test_user", ["test_user", "test_user_1"], "test_user_2"),
            # Для длинного имени пользователя корректируем ожидаемое значение
            ("a" * 150, [], "a" * 150),  # Если имя первое, оно не будет изменено
        ],
    )
    def test_get_unique_username(
        self,
        auth_service,
        base_username,
        existing_usernames,
        expected,
        telegram_user_factory,
    ):
        """Тест генерации уникальных имен пользователей."""
        for username in existing_usernames:
            telegram_user_factory(username=username)

        result = auth_service.get_unique_username(base_username)

        assert result == expected
        assert len(result) <= 150

    @patch(
        "src.authentication.services.secrets.token_urlsafe",
        return_value="test_password",
    )
    def test_concurrent_user_creation(self, mock_token, auth_service, telegram_data):
        """Тест конкурентного создания пользователей."""
        # Создаем первого пользователя
        user1 = auth_service.create_or_update_user(telegram_data)

        # Пытаемся создать второго пользователя с тем же telegram_id
        telegram_data_2 = telegram_data.copy()
        telegram_data_2["username"] = "another_username"

        def create_duplicate_user():
            with transaction.atomic():
                return auth_service.create_or_update_user(telegram_data_2)

        # В этом случае не должно быть IntegrityError, так как метод обрабатывает это
        user2 = create_duplicate_user()

        # Проверяем, что получили того же пользователя
        assert user2.id == user1.id
        assert User.objects.filter(telegram_id=telegram_data["id"]).count() == 1
