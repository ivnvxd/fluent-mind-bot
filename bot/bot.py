import logging
import openai
from asgiref.sync import sync_to_async

from django.conf import settings
from chats.models import Chat

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext, ContextTypes, PicklePersistence
from telegram.constants import ParseMode, ChatAction

from .helpers import send_action

TOKEN = settings.TELEGRAM_BOT_TOKEN
API_KEY = settings.OPENAI_API_KEY
# WEBHOOK_URL = settings.TELEGRAM_WEBHOOK_URL


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

HELP_MESSAGE = """Available commands:
❓ /help — Show help
"""

# messages = [
#         {"role": "system", "content": "You are an English teacher. You will write a sentence in Russian and wait for the translation. Do not answer by yourself. Write only one sentence in Russian. After you get the answer, tell me whether my answer was correct or not, and write an explanation if I was wrong. Then go on to the next question."}
#     ]

messages = [
    {"role": "system", "content": "As an advanced chatbot Assistant, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user."}
]

create_message_async = sync_to_async(Chat.objects.create)


@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot."""

    text = "Hi! I'm <b>ChatGPT</b> bot implemented with GPT-3.5 OpenAI API 🤖\n\n"
    text += HELP_MESSAGE
    text += "\nAnd now... ask me anything!"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def help(update: Update, context: CallbackContext):
    """Show available commands."""

    await context.bot.send_message(chat_id=update.message.chat_id, text=HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def unknown(update: Update, context: CallbackContext):
    """Return if wrong command entered."""

    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.message.chat_id, text=text)


@send_action(ChatAction.TYPING)
async def message(update: Update, context: CallbackContext):

    if "messages" not in context.chat_data:
        context.chat_data["messages"] = messages

    request = update.message.text
    user_id = update.message.chat.id
    username = update.message.from_user.username

    await create_message_async(
        role='user',
        user_id=user_id,
        username=username,
        text=request,
    )

    context.chat_data["messages"].append({"role": "user", "content": request})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context.chat_data["messages"]
    )

    answer = response['choices'][0]['message']['content']
    context.chat_data["messages"].append({"role": "assistant", "content": answer})

    await create_message_async(
        role='assistant',
        user_id=user_id,
        username=username,
        text=answer,
    )

    print(context.chat_data)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer,
        parse_mode='HTML'
    )

@send_action(ChatAction.TYPING)
async def echo(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


# persistence = PicklePersistence(filepath="conversationbot")

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))
application.add_handler(MessageHandler(filters.COMMAND, unknown))


async def run(data):
    async with application:
        # await application.initialize()
        await application.process_update(
            Update.de_json(data=data, bot=application.bot)
        )
