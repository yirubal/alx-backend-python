# chats/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    """
    Filter messages by:
    - user (sender)
    - timestamp range (start_time, end_time)
    """
    start_time = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    end_time = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")
    user = django_filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Message
        fields = ["user", "start_time", "end_time"]
