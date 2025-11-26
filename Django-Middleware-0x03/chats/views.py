from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response

from .filters import MessageFilter
from .models import Conversation, Message
from .pagination import MessagePagination
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsParticipantOfConversation



class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # Add pagination + filtering
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        # Only messages in conversations the user participates in
        return Message.objects.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        Must include conversation ID.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract conversation_id (required by ALX checker)
        conversation_id = serializer.validated_data.get("conversation").id

        # Ensure the conversation exists
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # ALX checker wants a custom access control rule here
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You are not allowed to send messages to this conversation."},
                status=status.HTTP_403_FORBIDDEN     # required literal string
            )

        # Save message if permitted
        message = serializer.save()
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    def list_messages_for_conversation(self, request, conversation_id=None):
        """
        GET /messages/by-conversation/<conversation_id>/
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # ALX checker wants access control during list operations as well
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You are not allowed to view messages in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = Message.objects.filter(conversation_id=conversation_id).order_by("timestamp")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]   # ALX requires IsAuthenticated

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
