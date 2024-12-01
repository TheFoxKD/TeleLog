# src/telelog/auth/bot.py

import logging
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from src.telelog.models import AuthenticationToken, TelegramSession

logger = logging.getLogger(__name__)
User = get_user_model()


class TelegramAuthBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))

    @sync_to_async
    def get_auth_token(self, token):
        return AuthenticationToken.objects.get(token=token)

    @sync_to_async
    def get_or_create_user(self, telegram_id):
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={"username": f"tg_{telegram_id}", "is_telegram_auth": True},
        )
        if created:
            logger.info(f"TelegramAuthBot: Created new user {user.username} with telegram_id {telegram_id}")
        else:
            logger.info(f"TelegramAuthBot: Retrieved existing user {user.username} with telegram_id {telegram_id}")
        return user

    @sync_to_async
    def update_session(self, user, username, full_name):
        session, created = TelegramSession.objects.update_or_create(
            user=user,
            defaults={
                "telegram_username": username,
                "telegram_name": full_name,
                "is_active": True,
            },
        )
        if created:
            logger.info(f"TelegramAuthBot: Created new TelegramSession for user {user.username}")
        else:
            logger.info(f"TelegramAuthBot: Updated TelegramSession for user {user.username}")
        return session

    @sync_to_async
    def mark_token_used(self, auth_token, user):
        auth_token.user = user
        auth_token.is_used = True
        auth_token.save()
        logger.info(f"TelegramAuthBot: Marked token {auth_token.token} as used by user {user.username}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            logger.warning("TelegramAuthBot: No effective user in update.")
            return

        token = context.args[0] if context.args else None
        if not token:
            await update.message.reply_text(
                "Пожалуйста, используйте ссылку для входа с сайта."
            )
            logger.warning("TelegramAuthBot: No token provided in /start command.")
            return

        try:
            auth_token = await self.get_auth_token(token)
            logger.info(f"TelegramAuthBot: Retrieved token {auth_token.token}, is_used: {auth_token.is_used}, expires_at: {auth_token.expires_at}")
            if not auth_token.is_valid():
                await update.message.reply_text(
                    "⚠️ Срок действия ссылки истек. Попробуйте войти снова."
                )
                logger.warning(f"TelegramAuthBot: Token {auth_token.token} is invalid or expired.")
                return

            user = await self.get_or_create_user(update.effective_user.id)
            await self.update_session(
                user, update.effective_user.username, update.effective_user.full_name
            )
            await self.mark_token_used(auth_token, user)

            # Формируем сообщение в HTML
            callback_url = f"{settings.TELEGRAM_LOGIN_REDIRECT_URL}?token={token}"
            message_html = (
                '✅ <b>Успешная аутентификация!</b>\n\n'
                '📱 Для возврата на сайт нажмите на кнопку ниже:\n'
                f'<a href="{callback_url}">🔗 Вернуться на сайт</a>'
            )

            await update.message.reply_text(
                message_html,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

        except AuthenticationToken.DoesNotExist:
            await update.message.reply_text(
                "❌ Неверный токен аутентификации. Попробуйте войти снова."
            )
            logger.error(f"TelegramAuthBot: AuthenticationToken with token {token} does not exist.")
        except Exception as e:
            logger.error(f"Error during authentication: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Произошла ошибка при аутентификации. Попробуйте позже."
            )

    def start(self):
        self.app.run_polling()

    def stop(self):
        if self.app.is_running:
            self.app.stop()