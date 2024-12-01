# src/telelog/urls.py
from django.urls import path
from .views import MainView, LoginView, LogoutView, CallbackView

app_name = "telelog"
urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("callback/", CallbackView.as_view(), name="callback"),
]
