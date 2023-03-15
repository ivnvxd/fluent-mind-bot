import json
import asyncio

from django.http import HttpResponse, JsonResponse
from django.views import View

from .bot import build, run


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)

        application = build()
        asyncio.run(run(application, data))

        # print(data)

        return JsonResponse({'message': 'OK'}, status=200)
