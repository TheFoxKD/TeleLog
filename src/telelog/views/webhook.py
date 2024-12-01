# src/telelog/views/webhook.py
import json

from django.http import HttpResponse
from django.views.generic import View
from telegram import Update


class TelegramWebhookView(View):
    async def post(self, request, *args, **kwargs):
        update = Update.de_json(json.loads(request.body), None)

        from src.telelog.apps import TelelogConfig

        app = TelelogConfig.bot.app
        await app.process_update(update)

        return HttpResponse("OK")
