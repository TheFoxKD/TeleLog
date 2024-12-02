# tests/factories/users.py
from factory import Faker, LazyAttribute, LazyFunction, Sequence, post_generation
from factory.django import DjangoModelFactory

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


User = get_user_model()


class BaseUserFactory(DjangoModelFactory):
    """Базовая фабрика для создания пользователей."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = Sequence(lambda n: f"user_{n}")
    email = LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @post_generation
    def password(self, create: bool, extracted: str, **kwargs):
        """Хеширование пароля после создания пользователя."""
        self.raw_password = extracted or "password123"  # Сохраняем нехешированный пароль для тестов
        self.password = make_password(self.raw_password)


class TelegramUserFactory(BaseUserFactory):
    """Фабрика для создания пользователей с данными Telegram."""

    telegram_id = Sequence(lambda n: str(n + 100000))
    telegram_username = LazyAttribute(lambda obj: f"tg_{obj.username}")


class AdminUserFactory(BaseUserFactory):
    """Фабрика для создания администраторов."""

    username = Sequence(lambda n: f"admin_{n}")
    is_staff = True
    is_superuser = True


class SuperuserFactory(AdminUserFactory):
    """Фабрика для создания суперпользователей."""

    username = Sequence(lambda n: f"superuser_{n}")


class InactiveUserFactory(BaseUserFactory):
    """Фабрика для создания неактивных пользователей."""

    is_active = False


class RandomUserFactory(BaseUserFactory):
    """Фабрика для создания случайных пользователей с полными данными."""

    username = Faker("user_name")
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    telegram_id = LazyFunction(lambda: str(Faker("random_number", digits=10).generate()))
    telegram_username = Faker("user_name")
    date_joined = Faker("date_time_this_year", tzinfo=None)
