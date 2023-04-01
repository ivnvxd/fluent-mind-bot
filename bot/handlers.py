import openai

from django.utils import timezone

from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from telegram.constants import ParseMode, ChatAction

from .helpers import send_action, get_messages_count, get_or_create_chat, \
    get_first_sentence, get_conversation_history, create_message_entry, \
    save_chat, delete_chat


HELP_MESSAGE = """Available commands:
🔄 /retry — Regenerate last answer (🚧)
✨ /new — Start new chat
📝 /history — Show previous chats (🚧)
💾 /save — Save current chat (🚧)
❓ /help — Show help
"""


@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot."""

    text = "🤖 Hi! I'm <b>ChatGPT</b> bot " + \
           "implemented with GPT-3.5 OpenAI API 🤖\n\n" + \
           HELP_MESSAGE + \
           "\nAnd now... ask me anything!"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def help(update: Update, context: CallbackContext):
    """Show available commands."""

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=HELP_MESSAGE,
        parse_mode=ParseMode.HTML
    )


async def new(update: Update, context: CallbackContext):
    telegram_id = update.message.chat.id
    current_chat = await get_or_create_chat(telegram_id)

    messages_count = await get_messages_count(telegram_id, current_chat)

    if messages_count == 0:
        await delete_chat(current_chat)

    await get_or_create_chat(telegram_id, create_new_chat=True)

    text = "Let's start over.\n\n" + \
           "You can always go back to previous conversations" + \
           "with the /history command."

    await update.message.reply_text(text)


async def unknown(update: Update, context: CallbackContext):
    """Return if wrong command entered."""

    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.message.chat_id, text=text)


@send_action(ChatAction.TYPING)
async def echo(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text
    )


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

    await create_message_entry(
        chat=chat,
        telegram_id=telegram_id,
        username=username,
        request=text,
        response=answer,
        completion_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
    )

    chat.last_update = timezone.now()
    await save_chat(chat)

    print(update.message)

    await context.bot.send_message(
        chat_id=telegram_id,
        text=answer,
        parse_mode="Markdown",
    )
