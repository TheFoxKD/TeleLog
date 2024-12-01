# TeleLog - Telegram Authentication for Django

Django application for secure authentication via Telegram bot.

## Environment Setup

1. Update environment files:
```
.envs/
├── dev/
├──── .django         # Django core settings
└──── .postgres       # Database configuration
```

**`.django` configuration:**
- `DJANGO_ADMIN_URL`: Admin panel URL
- `APP_VERSION`: Application version
- `REDIS_URL`: Redis connection URL

**`.postgres` configuration:**
- Database credentials (host, port, name)
- Default user/password
- Connection settings

## Quick Start
```bash
docker compose -f docker-compose.dev.yml up -d
```

## Stack
- Python 3.12
- Django 5
- PostgreSQL 16
- Redis 6

## License
MIT
