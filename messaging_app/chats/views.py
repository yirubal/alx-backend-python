# chats/views.py
from rest_framework import viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .permissions import IsParticipantOfConversation


from .models import Conversation, Message
from .permissions import IsParticipantOfConversation
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]   # ALX requires IsAuthenticated

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)



class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]   # ALX requires IsAuthenticated

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)



class ConversationDetailView(RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]
    lookup_field = "id"  # adjust to your URL pattern; default is 'pk'
