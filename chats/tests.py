from django.test import TestCase, Client
from django.urls import reverse_lazy


class TestListMessages(TestCase):
    def test_tasks_view(self) -> None:
        self.client = Client()

        response = self.client.get(reverse_lazy('chats'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            template_name='messages.html'
        )
