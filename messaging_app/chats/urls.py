from django.urls import path
from chats import views

urlpatterns = [
    path('', views.ping, name='chats-ping'),  # GET /api/v1/chats/
]
