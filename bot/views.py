import json
import asyncio

from django.http import JsonResponse
from django.views import View

from .bot import run


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        """
        Processes an incoming update from the Telegram webhook and runs the bot.

        :param request: The incoming HTTP request containing the update
        """

        data = json.loads(request.body)
        asyncio.run(run(data))

        return JsonResponse({'message': 'OK'}, status=200)
