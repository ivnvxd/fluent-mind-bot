from django.urls import path

from .views import ChatsListView


urlpatterns = [
    path('', ChatsListView.as_view(), name='chats'),
]
