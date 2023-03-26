from django.views.generic import ListView

from .models import Chat


class ChatsListView(ListView):
    """
    Show all messages.
    """
    template_name = 'messages.html'
    model = Chat
    context_object_name = 'chats'
    extra_context = {
        'title': 'Messages'
    }
