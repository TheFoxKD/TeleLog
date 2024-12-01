# src/telelog/auth/webhook.py
import asyncio

from django.conf import settings
from telegram import Bot


async def setup_webhook():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    webhook_url = f"{settings.TELEGRAM_LOGIN_REDIRECT_URL}/webhook"

    await bot.set_webhook(
        url=webhook_url, allowed_updates=["message", "callback_query"]
    )


def init_webhook():
    asyncio.run(setup_webhook())
