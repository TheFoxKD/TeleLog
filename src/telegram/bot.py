# apps/telegram/bot.py

import asyncio

from asgiref.sync import sync_to_async
from django.conf import settings

from src.authentication.services import TelegramAuthService
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler


class TeleLogBot:
    def __init__(self):
        self.auth_service = TelegramAuthService()
        self.application = (
            ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        )
        self.site_url = settings.SITE_URL
        start_handler = CommandHandler("start", self.handle_start)
        self.application.add_handler(start_handler)

    async def handle_start(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /start с токеном."""
        args = context.args
        if not args:
            await update.message.reply_text(
                "👋 Привет! Похоже, вы запустили бота без токена авторизации.\n\n"
                "Чтобы начать работу:\n"
                f"1. Перейдите на сайт {self.site_url}\n"
                "2. Нажмите 'Войти через Telegram'\n"
                "3. Используйте полученный токен с командой /start\n\n"
                "Пример: /start your_token"
            )
            return

        token = args[0]
        if self.validate_token(token):
            telegram_data = update.effective_user.to_dict()
            user = await sync_to_async(self.auth_service.create_or_update_user)(
                telegram_data
            )
            await sync_to_async(self.auth_service.redis_client.setex)(
                f"auth_{token}", 300, user.id
            )
            await update.message.reply_text(
                "✅ Отлично! Вы успешно авторизованы в системе TeleLog!\n\n"
                "Теперь вы можете:\n"
                f"• Вернуться на сайт {self.site_url}\n\n"
                "Приятного использования! 🚀"
            )
        else:
            await update.message.reply_text(
                "❌ Упс! Токен недействителен или устарел.\n\n"
                "Возможные причины:\n"
                "• Истек срок действия токена\n"
                "• Токен уже был использован\n"
                "• Опечатка при вводе токена\n\n"
                f"Пожалуйста, вернитесь на сайт {self.site_url} и получите новый токен."
            )

    async def validate_token(self, token: str) -> bool:
        """Проверяет валидность токена."""
        exists = await sync_to_async(self.auth_service.redis_client.exists)(token)
        return exists

    def run(self):
        asyncio.run(self.application.run_polling())
