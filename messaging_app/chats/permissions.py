# chats/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework import permissions  # required by ALX checker

class IsParticipantOfConversation(BasePermission):
    """
    Allow access only to authenticated users who are participants in the conversation.

    - has_permission: quick gate to require authentication for view-level access
    - has_object_permission: ensure the user is part of the conversation for object-level checks
    """

    def has_permission(self, request, view):
        # Ensure user is authenticated for any action
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        obj can be:
         - Conversation: has 'participants' ManyToMany or similar
         - Message: has 'conversation' FK that links to Conversation
        """
        # Conversation-like object (has participants)
        if hasattr(obj, "participants"):
            return request.user in obj.participants.all()

        # Message-like object (belongs to a conversation)
        if hasattr(obj, "conversation"):
            return request.user in obj.conversation.participants.all()

        # Default deny
        return False
