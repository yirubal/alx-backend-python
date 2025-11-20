import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model extending Django AbstractUser.
    Adds:
    - UUID primary key
    - phone_number
    - role
    - created_at
    - password_hash (as required by project spec)
    """

    USER_ROLES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Custom role field
    role = models.CharField(max_length=10, choices=USER_ROLES, default='guest')

    # Keep Django password but also store password_hash (as per spec)
    password_hash = models.CharField(max_length=255, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)

    # Enforce unique email
    email = models.EmailField(unique=True)

    # Required by Django when overriding email uniqueness
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username still required internally

    def __str__(self):
        return f"{self.email}"


class Conversation(models.Model):
    """
    Represents a chat conversation between multiple users.
    - UUID primary key
    - Many-to-many participants
    - created_at timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):
    """
    Represents a message inside a conversation.
    - sender → FK to User
    - conversation → FK to Conversation
    - message_body
    - sent_at timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')

    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.message_body[:30]}"
from django.db import models

# Create your models here.
