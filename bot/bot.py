import logging

from django.conf import settings

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, PicklePersistence

from .handlers import start, help, unknown, chat


TOKEN = settings.TELEGRAM_BOT_TOKEN
API_KEY = settings.OPENAI_API_KEY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# persistence = PicklePersistence(filepath="persistence")

# application = Application.builder().token(TOKEN).persistence(persistence=persistence).build()
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help))
# application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
application.add_handler(MessageHandler(filters.COMMAND, unknown))


async def run(data):
    async with application:
        await application.process_update(
            Update.de_json(data=data, bot=application.bot)
        )
