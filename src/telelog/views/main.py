# src/telelog/views/main.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MainView(LoginRequiredMixin, TemplateView):
    template_name = "telelog/main.html"
