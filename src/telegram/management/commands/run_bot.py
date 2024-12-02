# src/telegram/management/commands/run_bot.py
from django.core.management.base import BaseCommand
from src.telegram.bot import TeleLogBot


class Command(BaseCommand):
    help = "Запускает Telegram бота"

    def handle(self, *args, **options):
        self.stdout.write("Запуск бота...")
        bot = TeleLogBot()
        bot.run()
