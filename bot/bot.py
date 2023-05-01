import logging

from django.conf import settings

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters

from bot import handlers


TOKEN = settings.TELEGRAM_BOT_TOKEN
API_KEY = settings.OPENAI_API_KEY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler('start', handlers.start))
application.add_handler(CommandHandler('help', handlers.help))
application.add_handler(CommandHandler('new', handlers.new))
application.add_handler(CommandHandler('save', handlers.save))
application.add_handler(CommandHandler('retry', handlers.retry))
application.add_handler(CommandHandler('img', handlers.img))
application.add_handler(MessageHandler(
    filters.TEXT & (~filters.COMMAND),
    handlers.chat)
                        )
application.add_handler(MessageHandler(filters.COMMAND, handlers.unknown))


async def run(data):
    async with application:
        await application.process_update(
            Update.de_json(data=data, bot=application.bot)
        )
