from django.views.generic import ListView

from .models import Text


class ChatsListView(ListView):
    """
    Show all messages.
    """
    template_name = 'messages.html'
    model = Text
    context_object_name = 'texts'
    extra_context = {
        'title': 'Messages'
    }
