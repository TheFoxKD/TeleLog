# config/urls.py
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("src.authentication.urls", namespace="authentication")),
    path("", include("src.core.urls", namespace="core")),
]
