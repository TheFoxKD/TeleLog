# src/telelog/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class TelegramAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Разрешаем доступ к статическим файлам и медиа
        if request.path.startswith(("/static/", "/media/")):
            return None

        # Разрешаем доступ к URL-ам авторизации и вебхукам Telegram
        allowed_paths = [
            reverse("telelog:login"),
            reverse("telelog:callback"),
            reverse("telelog:logout"),
            reverse("admin:index"),
        ]
        if any(request.path.startswith(path) for path in allowed_paths):
            return None

        # Если пользователь не аутентифицирован, перенаправляем на страницу входа
        if not request.user.is_authenticated:
            return redirect(reverse("telelog:login"))

        # Если пользователь аутентифицирован, продолжаем обработку запроса
        return None
