from django.views.generic import ListView

from .models import User


class UsersListView(ListView):
    """
    Show all users.
    """
    template_name = 'index.html'
    model = User
    context_object_name = 'users'
    extra_context = {
        'title': 'Users'
    }
