# src/telelog/management/commands/runbot.py
from django.core.management.base import BaseCommand
from src.telelog.auth.bot import TelegramAuthBot


class Command(BaseCommand):
    help = "Запускает Telegram бота"

    def handle(self, *args, **options):
        self.stdout.write("Запуск бота...")
        bot = TelegramAuthBot()
        bot.start()
