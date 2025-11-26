# chats/middleware.py
from datetime import datetime
from django.conf import settings
import os
import time
from django.http import JsonResponse
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





class OffensiveLanguageMiddleware:
    """
    Middleware to limit number of chat messages sent by an IP address
    within a defined time window (rate limiting).
    """

    # max messages per window
    MESSAGE_LIMIT = 5
    # window in seconds (1 minute)
    TIME_WINDOW = 60

    def __init__(self, get_response):
        self.get_response = get_response
        # store IP addresses with timestamps of POST requests
        self.ip_requests = {}

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/messages/"):
            ip = self.get_client_ip(request)
            now = time.time()
            # remove old requests outside the time window
            timestamps = self.ip_requests.get(ip, [])
            timestamps = [t for t in timestamps if now - t < self.TIME_WINDOW]

            if len(timestamps) >= self.MESSAGE_LIMIT:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Max 5 messages per minute."},
                    status=429,
                )

            timestamps.append(now)
            self.ip_requests[ip] = timestamps

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """
        Retrieve client IP address from request.
        Handles common reverse proxy headers.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip



class RolepermissionMiddleware:
    """
    Middleware to enforce role-based access control.
    Only users with 'admin' or 'moderator' role can proceed.
    """

    # roles allowed to access protected routes
    ALLOWED_ROLES = ["admin", "moderator"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure the user is authenticated first
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required."}, status=401
            )

        # Check role for protected actions
        if request.path.startswith("/api/protected/"):  # Adjust your endpoint
            user_role = getattr(user, "role", None)  # assuming user model has 'role' field
            if user_role not in self.ALLOWED_ROLES:
                return JsonResponse(
                    {"error": "Forbidden. Admin or moderator role required."}, status=403
                )

        response = self.get_response(request)
        return response