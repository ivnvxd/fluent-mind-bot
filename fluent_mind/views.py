from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'
    extra_context = {'title': 'Fluent Mind'}
