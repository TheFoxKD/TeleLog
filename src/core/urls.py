# apps/core/urls.py

from django.urls import path

from .views import DashboardView


app_name = "core"
urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]
