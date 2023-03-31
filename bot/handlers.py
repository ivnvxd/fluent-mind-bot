import logging
import openai
from asgiref.sync import sync_to_async

from django.conf import settings
from chats.models import Text, Chat

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext, ContextTypes, PicklePersistence
from telegram.constants import ParseMode, ChatAction

from .helpers import send_action


HELP_MESSAGE = """Available commands:
🔄 /retry — Regenerate last answer (🚧)
✨ /new — Start new chat (🚧)
📝 /history — Show previous chats (🚧)
💾 /save — Save current chat (🚧)
❓ /help — Show help
"""

# system = {
#     "role": "system", "content": "As an advanced chatbot Assistant, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user."
# }

system = {"role": "system", "content": "You are a helpful assistant."}


@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot."""

    text = "🤖 Hi! I'm <b>ChatGPT</b> bot implemented with GPT-3.5 OpenAI API 🤖\n\n"
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
async def echo(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


@sync_to_async
def add_entry(**kwargs):
    text = Text.objects.create(**kwargs)
    return text


@sync_to_async
def get_messages(**kwargs):
    messages = Text.objects.filter(**kwargs).order_by('id')

    request = [system]
    for message in messages:
        request.extend([
            {"role": "user", "content": message.request},
            {"role": "assistant", "content": message.response}
        ])

    return request


@send_action(ChatAction.TYPING)
async def chat(update: Update, context: CallbackContext):

    text = update.message.text
    telegram_id = update.message.chat.id
    username = update.message.from_user.username

    request = await get_messages(telegram_id=telegram_id)

    request.append({"role": 'user', "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request
    )

    answer = response['choices'][0]['message']['content']
    usage = response['usage']
    completion_tokens = response['usage']['completion_tokens']
    prompt_tokens = response['usage']['prompt_tokens']

    print(request)
    print(usage)
    print(answer)

    await add_entry(
        telegram_id=telegram_id,
        username=username,
        request=text,
        response=answer,
        completion_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
    )

    print(update.message)

    await context.bot.send_message(
        chat_id=telegram_id,
        text=answer,
        parse_mode="Markdown",
    )
