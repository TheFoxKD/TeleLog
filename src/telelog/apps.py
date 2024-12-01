import logging
import threading
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class TelelogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.telelog"
    verbose_name = "Telegram Authentication"
    bot = None

    def ready(self):
        if threading.current_thread().name == "main_thread":
            from src.telelog.auth.bot import TelegramAuthBot

            logger.info("Initializing Telegram bot")
            self.bot = TelegramAuthBot()
            threading.Thread(target=self.bot.start, daemon=True).start()
