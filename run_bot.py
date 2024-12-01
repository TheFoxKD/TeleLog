# run_bot.py

import os
import django
from src.telegram.bot import TeleLogBot

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telelog.settings.local")
django.setup()

if __name__ == "__main__":
    bot = TeleLogBot()
    bot.run()
