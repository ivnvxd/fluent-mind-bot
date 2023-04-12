import openai

from django.utils import timezone

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode, ChatAction

from .helpers import send_action, get_topic, save_chat, delete_chat, \
    get_summary, get_conversation_history
from .database import get_messages_count, get_or_create_chat, \
    create_message_entry


HELP_MESSAGE = """Available commands:
🔄 /retry — Regenerate last answer 🚧
✨ /new — Start new chat
📝 /history — Show previous chats 🚧
💾 /save — Save current chat 🚧
❓ /help — Show help
"""


@send_action(ChatAction.TYPING)
async def start(update: Update, context: CallbackContext):
    """
    Sends a greeting message and help information when the bot is started.
    """

    text = (
        "🤖 Hi! I'm <b>ChatGPT</b> bot "
        "implemented with GPT-3.5 OpenAI API 🤖\n\n"
        f"{HELP_MESSAGE}\n"
        "And now... ask me anything!"
    )

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def help(update: Update, context: CallbackContext):
    """
    Sends a message with a list of available commands.
    """

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=HELP_MESSAGE,
        parse_mode=ParseMode.HTML
    )


async def new(update: Update, context: CallbackContext):
    """
    Starts a new chat, saves the previous chat if there were any messages,
    and sets the new chat as the current one.
    """

    # Reply to the user immediately
    text = "Let's start over.\n\n" + \
           "You can always go back to previous conversations" + \
           "with the /history command."
    await update.message.reply_text(text)

    # Process chat data
    telegram_id = update.message.chat.id
    current_chat = await get_or_create_chat(telegram_id)

    messages_count = await get_messages_count(telegram_id, current_chat)

    if messages_count > 0:
        request = await get_conversation_history(
            telegram_id=telegram_id,
            chat=current_chat
        )
        summary = await get_summary(request)
        current_chat.summary = summary[:1000]
        await save_chat(current_chat)
    else:
        await delete_chat(current_chat)

    await get_or_create_chat(telegram_id, create_new_chat=True)


async def unknown(update: Update, context: CallbackContext):
    """
    Sends a message when an unknown command is entered.
    """

    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.message.chat_id, text=text)


@send_action(ChatAction.TYPING)
async def chat(update: Update, context: CallbackContext):
    """
    Processes user input, generates a response using GPT-3.5,
    and sends the response to the user.
    """

    text = update.message.text
    telegram_id = update.message.chat.id
    username = update.message.from_user.username

    chat = await get_or_create_chat(telegram_id)
    request = await get_conversation_history(telegram_id, chat, text)

    request.append({"role": 'user', "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request
    )

    answer = response['choices'][0]['message']['content']
    completion_tokens = response['usage']['completion_tokens']
    prompt_tokens = response['usage']['prompt_tokens']

    print('request:', text)
    print()
    print('answer:', answer)

    # Send the response message as early as possible
    await context.bot.send_message(
        chat_id=telegram_id,
        text=answer,
        parse_mode="Markdown",
    )

    # Process the remaining data
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

    if chat.topic == "":
        request.append({"role": 'assistant', "content": answer})
        topic = await get_topic(request)
        chat.topic = topic[:250]

        await save_chat(chat)
