from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Allows access only to users who own the object (Conversation or Message)
    """

    def has_object_permission(self, request, view, obj):
        # If obj has a user attribute
        if hasattr(obj, "user"):
            return obj.user == request.user

        # If object is a Conversation with participants
        if hasattr(obj, "participants"):
            return request.user in obj.participants.all()

        return False
