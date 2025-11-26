# chats/views.py
from rest_framework import viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Conversation, Message
from .permissions import IsParticipantOfConversation
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Viewset to list, create, retrieve and update conversations.
    Only conversations where the request.user is a participant are returned.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]

    def get_queryset(self):
        # Ensure user only sees conversations they participate in
        user = self.request.user
        return Conversation.objects.filter(participants=user)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        Expect participants (including the creator) provided in payload.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Viewset to list, create, retrieve messages within conversations.
    Only messages belonging to conversations the user participates in are returned.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]

    def get_queryset(self):
        # Only messages in conversations the user is part of
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        Must include conversation ID in payload (e.g., {"conversation": 1, "body": "hi"})
        Also enforces that the request.user is a participant of that conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Resolve conversation instance (support either id in data or validated_data)
        conversation = serializer.validated_data.get("conversation", None)
        if conversation is None:
            # Fallback: try out of request.data
            conversation_id = request.data.get("conversation")
            if not conversation_id:
                return Response({"error": "Conversation id required."},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({"error": "Conversation not found."},
                                status=status.HTTP_404_NOT_FOUND)

        # Ensure the sender is a participant
        if request.user not in conversation.participants.all():
            return Response({"error": "You are not a participant of this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        # Save message with validated data
        message = serializer.save()
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="by-conversation/(?P<conversation_id>[^/.]+)")
    def list_messages_for_conversation(self, request, conversation_id=None):
        """
        GET /messages/by-conversation/<conversation_id>/
        Only allowed if requester is a participant in the conversation.
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

        # Permission check: must be participant
        if request.user not in conversation.participants.all():
            return Response({"error": "You are not a participant of this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        messages = Message.objects.filter(conversation_id=conversation_id).order_by("timestamp")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class ConversationDetailView(RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]
    lookup_field = "id"  # adjust to your URL pattern; default is 'pk'
