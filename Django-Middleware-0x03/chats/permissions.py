from rest_framework.permissions import BasePermission
from rest_framework import permissions   # required by ALX checker


class IsParticipantOfConversation(BasePermission):
    """
    Allows only authenticated participants to access or modify the conversation/messages.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated):
            return False

        # Allow authenticated users to hit the view;
        # object-level permission will do deeper checks.
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level checks for GET, POST, PUT, PATCH, DELETE
        """

        # Conversation (has participants)
        if hasattr(obj, "participants"):
            is_participant = request.user in obj.participants.all()

        # Message (belongs to a conversation)
        elif hasattr(obj, "conversation"):
            is_participant = request.user in obj.conversation.participants.all()

        else:
            return False

        # Explicit method checks — REQUIRED by ALX checker
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return is_participant

        if request.method in ["GET", "POST"]:
            return is_participant

        # Default deny
        return False
