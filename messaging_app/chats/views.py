from rest_framework import viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Conversation, Message
from .permissions import IsOwner
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Viewset to list, create, retrieve and update conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Viewset to list, create, retrieve messages within conversations.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        Must include conversation ID.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure conversation exists before saving
        conversation_id = serializer.validated_data.get("conversation").id
        try:
            Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)

        message = serializer.save()
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="by-conversation/(?P<conversation_id>[^/.]+)")
    def list_messages_for_conversation(self, request, conversation_id=None):
        """
        Custom endpoint:
        GET /messages/by-conversation/<conversation_id>/
        """
        messages = Message.objects.filter(conversation_id=conversation_id).order_by("timestamp")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)



class ConversationDetailView(RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsOwner]
    lookup_field = "id"  # optional if your URL uses <id>

