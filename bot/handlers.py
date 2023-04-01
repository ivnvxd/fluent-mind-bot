import openai
from asgiref.sync import sync_to_async

from django.utils import timezone
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

system = {"role": "system", "content": "You are a helpful assistant."}


@sync_to_async
def get_or_create_chat(telegram_id, create_new_chat=False):
    if create_new_chat:
        chat = Chat.objects.create(telegram_id=telegram_id)
    else:
        chat = Chat.objects.filter(telegram_id=telegram_id).order_by('-creation_date').first()
        if not chat:
            chat = Chat.objects.create(telegram_id=telegram_id)
    return chat


@sync_to_async
def get_messages_count(telegram_id, chat):
    return Text.objects.filter(telegram_id=telegram_id, chat=chat).count()


@sync_to_async
def create_message_entry(chat, **kwargs):
    text = Text.objects.create(chat=chat, **kwargs)
    return text


@sync_to_async
def get_conversation_history(telegram_id, chat):
    messages = Text.objects.filter(telegram_id=telegram_id, chat=chat).order_by('date')

    request = [system]
    for message in messages:
        request.extend([
            {"role": "user", "content": message.request},
            {"role": "assistant", "content": message.response}
        ])

    return request


@sync_to_async
def save_chat(chat):
    chat.save()


@sync_to_async
def delete_chat(chat):
    chat.delete()


async def get_first_sentence(response_text):
    first_sentence = response_text.split('.')[0].strip()
    return first_sentence


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


async def new(update: Update, context: CallbackContext):
    telegram_id = update.message.chat.id
    current_chat = await get_or_create_chat(telegram_id)

    messages_count = await get_messages_count(telegram_id, current_chat)

    if messages_count == 0:
        await delete_chat(current_chat)

    chat = await get_or_create_chat(telegram_id, create_new_chat=True)

    text = f"Let's start over.\n\nYou can always go back to previous conversations with the /history command."
    await update.message.reply_text(text)


async def unknown(update: Update, context: CallbackContext):
    """Return if wrong command entered."""

    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.message.chat_id, text=text)


@send_action(ChatAction.TYPING)
async def echo(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


@send_action(ChatAction.TYPING)
async def chat(update: Update, context: CallbackContext):

    text = update.message.text
    telegram_id = update.message.chat.id
    username = update.message.from_user.username

    chat = await get_or_create_chat(telegram_id)
    request = await get_conversation_history(telegram_id=telegram_id, chat=chat)

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

    if chat.topic == "" and chat.summary == "":
        first_sentence = await get_first_sentence(answer)
        chat.topic = first_sentence[:250]
        chat.summary = first_sentence[:1000]
        await save_chat(chat)

    text_entry = await create_message_entry(
        chat=chat,
        telegram_id=telegram_id,
        username=username,
        request=text,
        response=answer,
        completion_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
    )

    chat.last_update = timezone.now()  # Update the last_update field of the Chat model
    await save_chat(chat)

    print(update.message)

    await context.bot.send_message(
        chat_id=telegram_id,
        text=answer,
        parse_mode="Markdown",
    )
