from django.views.generic import ListView

from .models import Text, Chat


class MessagesListView(ListView):
    """
    Show all messages.
    """
    template_name = 'messages.html'
    model = Text
    context_object_name = 'texts'
    extra_context = {
        'title': 'Messages'
    }

class ChatsListView(ListView):
    template_name = 'chats.html'
    model = Chat
    context_object_name = 'chats'
    extra_context = {
        'title': 'Chats'
    }
