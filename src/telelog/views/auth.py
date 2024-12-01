# src/telelog/views/auth.py
import logging

from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from src.telelog.models import AuthenticationToken

logger = logging.getLogger(__name__)


class LoginView(View):
    template_name = "telelog/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("telelog:main"))

        token = AuthenticationToken.objects.create()
        if token:
            logger.info(f"Token {token.token} created successfully.")
        else:
            logger.error("Failed to create token.")
        logger.info(f"LoginView: Created AuthenticationToken: {token.token}, expires_at: {token.expires_at}")
        bot_link = f"https://t.me/telelog_auth_bot?start={token.token}"
        return render(request, self.template_name, {"bot_link": bot_link})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("telelog:main")




class CallbackView(View):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            logger.warning("CallbackView: No token provided.")
            return redirect(reverse('telelog:login'))

        try:
            auth_token = AuthenticationToken.objects.get(token=token)
            logger.info(f"CallbackView: Found token {auth_token.token}, is_used: {auth_token.is_used}, expires_at: {auth_token.expires_at}")
            if auth_token.is_valid() and auth_token.user and not auth_token.is_used:
                login(request, auth_token.user)
                # Помечаем токен как использованный
                auth_token.is_used = True
                auth_token.save()
                logger.info(f"CallbackView: User {auth_token.user} logged in with token {auth_token.token}")
                return redirect(reverse('telelog:main'))
            else:
                logger.warning(f"CallbackView: Invalid or used token {auth_token.token}")
        except AuthenticationToken.DoesNotExist:
            logger.error(f"CallbackView: Token {token} does not exist.")

        return redirect(reverse('telelog:login'))
