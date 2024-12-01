# src/core/middleware.py

import re

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware that ensures:
    - Authenticated users are redirected away from the login page to their profile.
    - Unauthenticated users are redirected to the login page when accessing protected pages.
    - Static and media files, admin, and exempt URLs are not affected.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # List of URL patterns to exempt from the middleware
        exempt_urls = [
            reverse("authentication:login"),
            reverse("authentication:logout"),
            reverse("authentication:auth_callback"),
        ]
        # Add static and media URLs
        exempt_urls += [settings.STATIC_URL, settings.MEDIA_URL]
        # Compile URL patterns into regex for performance
        self.exempt_urls = [re.compile(f"^{re.escape(url)}") for url in exempt_urls]

    def __call__(self, request):
        # Process the request
        response = self.process_request(request)
        if response:
            return response
        # Continue processing the response
        return self.get_response(request)

    def process_request(self, request):
        # Skip processing for exempt URLs
        if self.is_exempt(request.path):
            return None

        if request.user.is_authenticated:
            # Redirect authenticated users away from the login page
            if request.path == reverse("authentication:login"):
                return redirect("core:dashboard")
        else:
            # Redirect unauthenticated users to the login page
            return redirect("authentication:login")

        return None

    def is_exempt(self, path):
        # Check if the path is in the list of exempt URLs
        for url_pattern in self.exempt_urls:
            if url_pattern.match(path):
                return True
        # Also exclude admin URLs
        if path.startswith(reverse("admin:index")):
            return True
        return False
