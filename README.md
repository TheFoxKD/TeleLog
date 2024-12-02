# TeleLog - Telegram Authentication System

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-5.1-green.svg)](https://www.djangoproject.com)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/TheFoxKD/TeleLog/actions/workflows/ci.yml/badge.svg)](https://github.com/TheFoxKD/TeleLog/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/TheFoxKD/TeleLog/badge.svg?branch=main)](https://coveralls.io/github/TheFoxKD/TeleLog?branch=main)

### 👨‍💻 Разработчик

**Денис 🦊**

[![GitHub](https://img.shields.io/badge/GitHub-TheFoxKD-181717?style=flat&logo=github)](https://github.com/TheFoxKD)
[![Telegram](https://img.shields.io/badge/Telegram-@TheFoxDK-2CA5E0?style=flat&logo=telegram)](https://t.me/TheFoxDK)
[![Email](https://img.shields.io/badge/Email-krishtopadenis@gmail.com-D14836?style=flat&logo=gmail)](mailto:krishtopadenis@gmail.com)

TeleLog - это система аутентификации через Telegram для Django проектов. Проект позволяет пользователям легко и
безопасно входить на сайт через свой Telegram аккаунт.

## 🎥 Демонстрация

https://github.com/user-attachments/assets/d4307ea9-315d-4978-8366-13712b688e5c

## 📸 Скриншоты

### Страница авторизации

![Auth Screen](https://raw.githubusercontent.com/TheFoxKD/TeleLog/main/assets/TeleLogScreenAuth.jpg)

### Telegram бот с токеном в URL

![Telegram Bot Screen with Token](https://raw.githubusercontent.com/TheFoxKD/TeleLog/main/assets/TeleLogScreenAuthBotWithStartComandAndTokenInUrl.jpg)

### Успешная авторизация в боте

![Telegram Success Screen](https://raw.githubusercontent.com/TheFoxKD/TeleLog/main/assets/TeleLogScreenTelegramSuccess.jpg)

### Неуспешная авторизация в боте

![Telegram Error Screen](https://raw.githubusercontent.com/TheFoxKD/TeleLog/main/assets/TeleLogScreenTelegramError.jpg)

### Панель управления

![Dashboard Screen](https://raw.githubusercontent.com/TheFoxKD/TeleLog/main/assets/TeleLogScreenDashboard.jpg)

## 🚀 Особенности

- 🔐 Безопасная аутентификация через Telegram
- ⚡ Асинхронная обработка запросов
- 🔄 Real-time обновление статуса авторизации
- 🎨 Современный UI с Tailwind CSS
- 🐳 Docker для разработки
- ✅ Полное тестовое покрытие

## 🛠 Технический стек

- Python 3.12+
- Django 5.0+
- python-telegram-bot 21.0+
- Redis (кэширование токенов)
- PostgreSQL
- Docker & Docker Compose
- uv (управление зависимостями)
- ruff (форматирование)
- Pytest (тестирование)

## 📦 Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/TheFoxKD/telelog.git
cd telelog
```

2. Создайте .env файлы:

```bash
mkdir -p .envs/dev
cp .envs/dev/.django.example .envs/dev/.django
```

3. Настройте Telegram бота:

- Создайте бота через [@BotFather](https://t.me/BotFather)
- Добавьте токен в `.envs/dev/.django`:

```bash
TELEGRAM_BOT_TOKEN='your-token'
TELEGRAM_BOT_USERNAME='your-bot-username'
```

4. Запустите через Docker:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

5. Запустите миграции:

```bash
docker-compose -f docker-compose.dev.yml run --rm django python manage.py migrate
```

## 🧪 Тестирование и покрытие кода

```bash
# Запуск тестов с покрытием
docker-compose -f docker-compose.dev.yml run --rm django pytest --cov=src

# Генерация HTML отчета
docker-compose -f docker-compose.dev.yml run --rm django pytest --cov=src --cov-report=html

# Отчет в консоли
docker-compose -f docker-compose.dev.yml run --rm django pytest --cov=src --cov-report=term-missing
```
