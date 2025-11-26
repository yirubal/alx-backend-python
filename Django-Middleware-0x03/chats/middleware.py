# chats/middleware.py
from datetime import datetime


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_line = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        # Append to requests.log
        with open("requests.log", "a") as f:
            f.write(log_line)

        response = self.get_response(request)
        return response
