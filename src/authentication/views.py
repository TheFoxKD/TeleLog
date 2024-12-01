# apps/authentication/views.py

from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .models import User
from .services import TelegramAuthService


class AuthView(View):
    def get(self, request):
        """Генерирует токен и отображает страницу с инструкциями."""
        auth_service = TelegramAuthService()
        token = auth_service.generate_auth_token()
        telegram_bot_username = settings.TELEGRAM_BOT_USERNAME
        context = {
            "telegram_link": f"https://t.me/{telegram_bot_username}?start={token}",
            "token": token,
        }
        return render(request, "authentication/login.html", context)

    def post(self, request):
        """Проверяет, подтвердил ли пользователь аутентификацию в Telegram."""
        token = request.POST.get("token")
        auth_service = TelegramAuthService()
        user_id = auth_service.redis_client.get(f"auth_{token}")
        if user_id:
            user_id = int(user_id.decode("utf-8"))
            user = User.objects.get(id=user_id)
            login(request, user)
            return JsonResponse(
                {"authenticated": True, "redirect_url": reverse("core:dashboard")}
            )
        else:
            return JsonResponse({"authenticated": False})


class TelegramAuthCallbackView(View):
    def get(self, request):
        """Обрабатывает колбэк от Telegram после успешной аутентификации."""
        telegram_data = request.GET.dict()
        auth_service = TelegramAuthService()
        if auth_service.validate_telegram_data(telegram_data):
            user = auth_service.create_or_update_user(telegram_data)
            login(request, user)
            return redirect("core:dashboard")  # Перенаправляем на защищенную страницу
        else:
            return render(request, "authentication/login_failed.html")
