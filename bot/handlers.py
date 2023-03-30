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
❓ /help — Show help
"""

# system = {
#     "role": "system", "content": "As an advanced chatbot Assistant, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user."
# }

system = {"role": "system", "content": "You are a helpful assistant."}





# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)



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


# @send_action(ChatAction.TYPING)
# async def message(update: Update, context: CallbackContext):
#
#     text = update.message.text
#     user_id = update.message.chat.id
#     username = update.message.from_user.username
#
#     create_message_async = sync_to_async(Chat.objects.create)
#     await create_message_async(
#         role='user',
#         user_id=user_id,
#         username=username,
#         text=text,
#     )
#
#     get_messages_async = sync_to_async(Chat.objects.filter)
#     # messages = await get_messages_async(
#     #     user_id=user_id,
#     # )
#
#     if not context.user_data:
#         request = [system]
#     else:
#         request = context.user_data.get("chat")
#
#     request.append({"role": "user", "content": text})
#     context.user_data.update({"chat": request})
#
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=context.user_data.get("chat")
#     )
#
#     print(response)
#
#     answer = response['choices'][0]['message']['content']
#
#     request.append({"role": "assistant", "content": answer})
#
#     await create_message_async(
#         role='assistant',
#         user_id=user_id,
#         username=username,
#         text=answer,
#     )
#
#     print("user:", context.user_data)
#
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=answer,
#         parse_mode='Markdown'
#     )


@send_action(ChatAction.TYPING)
async def echo(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)









@sync_to_async
def create_text(**kwargs):
    text = Text.objects.create(**kwargs)
    return text


@sync_to_async
def get_user_messages(**kwargs):
    messages = Text.objects.filter(**kwargs).order_by('id')

    # Build the request list from the messages in the database
    request = [system]
    for message in messages:
        request.append({"role": message.role, "content": message.text})

    return request


@send_action(ChatAction.TYPING)
async def chat(update: Update, context: CallbackContext):

    text = update.message.text
    telegram_id = update.message.chat.id
    username = update.message.from_user.username

    # Get all the messages for this user from the database
    request = await get_user_messages(telegram_id=telegram_id)

    # Add current message to the request
    request.append({"role": 'user', "content": text})

    # Call OpenAI API to generate the response
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

    # Save the user message in the database
    chat = await create_text(
        role='user',
        telegram_id=telegram_id,
        username=username,
        text=text,
        tokens=prompt_tokens,
    )

    # Save the assistant message in the database
    chat = await create_text(
        role='assistant',
        telegram_id=telegram_id,
        username='ChatGPT',
        text=answer,
        tokens=completion_tokens,
    )

    # Send the assistant message to the user
    await context.bot.send_message(
        chat_id=telegram_id,
        text=answer,
        parse_mode="Markdown",
    )
