from django.urls import path

from .views import MessagesListView, ChatsListView


urlpatterns = [
    path('messages/', MessagesListView.as_view(), name='messages'),
    path('', ChatsListView.as_view(), name='chats'),
]
