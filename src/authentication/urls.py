# apps/authentication/urls.py
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import AuthView, TelegramAuthCallbackView


app_name = "authentication"
urlpatterns = [
    path("login/", AuthView.as_view(), name="login"),
    path("auth/callback/", TelegramAuthCallbackView.as_view(), name="auth_callback"),
    path("logout/", LogoutView.as_view(next_page="authentication:login"), name="logout"),
]
