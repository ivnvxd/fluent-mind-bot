import json
import asyncio

from django.http import HttpResponse, JsonResponse
from django.views import View

from .bot import run


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        asyncio.run(run(data))

        return JsonResponse({'message': 'OK'}, status=200)
