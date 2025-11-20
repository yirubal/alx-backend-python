from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Expose only safe fields
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'created_at'
        ]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'message_body',
            'sent_at',
            'conversation'
        ]
        read_only_fields = ['id', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'participants',
            'messages',
            'created_at'
        ]


# Optional: For creating conversations with participant IDs
class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = Conversation
        fields = ['participants']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participants')
        conversation = Conversation.objects.create()
        conversation.participants.set(participant_ids)
        return conversation
