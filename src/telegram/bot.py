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
        start_handler = CommandHandler("start", self.handle_start)
        self.application.add_handler(start_handler)

    async def handle_start(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /start с токеном."""
        args = context.args
        if not args:
            await update.message.reply_text(
                "Токен не предоставлен. Пожалуйста, получите токен на сайте."
            )
            return

        token = args[0]
        if self.validate_token(token):
            telegram_data = update.effective_user.to_dict()
            user = await sync_to_async(self.auth_service.create_or_update_user)(
                telegram_data
            )
            # Сохраняем информацию о том, что пользователь подтвердил вход
            await sync_to_async(self.auth_service.redis_client.setex)(
                f"auth_{token}", 300, user.id
            )
            await update.message.reply_text(
                "Вы успешно аутентифицированы! Можете вернуться на сайт."
            )
        else:
            await update.message.reply_text("Неверный или истекший токен.")

    async def validate_token(self, token: str) -> bool:
        """Проверяет валидность токена."""
        exists = await sync_to_async(self.auth_service.redis_client.exists)(token)
        return exists

    def run(self):
        asyncio.run(self.application.run_polling())
