# chats/middleware.py
from datetime import datetime
from django.conf import settings
import os

from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = os.path.join(settings.BASE_DIR, "requests.log")

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_line = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        # Append to requests.log
        with open(self.log_file, "a") as f:
            f.write(log_line)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Deny access to chat endpoints outside 6AM to 9PM.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Allow access only between 6 AM and 9 PM
        if not (6 <= current_hour < 21):
            return HttpResponseForbidden("Chat access is restricted between 9PM and 6AM.")

        response = self.get_response(request)
        return response