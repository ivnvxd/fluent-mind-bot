from django.utils import timezone

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode, ChatAction

# from bot import helpers
# from bot import database

from bot.helpers import send_action, get_topic, save_chat, delete_chat, \
    get_summary, get_conversation_history, save_text_entry, call_openai_api, \
    openai_image_create, logger
from bot.database import get_messages_count, get_or_create_chat, \
    create_message_entry, get_last_text_entry


HELP_MESSAGE = (
    "Available commands:\n"
    "🔄 /retry — Regenerate last answer\n"
    "✨ /new — Start new chat\n"
    "🏞️ /img _<prompt>_ — Generate image\n"
    "❓ /help — Show help\n"
)

# 💾 /save — Save current chat
# 📝 /history — Show previous chats 🚧

START_MESSAGE = (
    "🤖 Hi! I'm *ChatGPT* bot "
    "implemented with GPT-3.5 OpenAI API 🤖\n\n"
    f"{HELP_MESSAGE}\n"
    "And now... ask me anything!"
)


@send_action(ChatAction.TYPING)
async def start(update: Update, context: CallbackContext):
    """
    Sends a greeting message and help information when the bot is started.
    """

    logger.debug(
        "Bot started. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    # Reply to the user immediately
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=START_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )

    # Process chat data
    telegram_id = update.message.chat.id
    current_chat = await get_or_create_chat(telegram_id)

    messages_count = await get_messages_count(telegram_id, current_chat)
    if messages_count == 0:
        await delete_chat(current_chat)

    await get_or_create_chat(telegram_id, create_new_chat=True)


async def help(update: Update, context: CallbackContext):
    """
    Sends a message with a list of available commands.
    """

    logger.debug(
        "Help message. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )


@send_action(ChatAction.TYPING)
async def new(update: Update, context: CallbackContext):
    """
    Starts a new chat, saves the previous chat if there were any messages,
    and sets the new chat as the current one.
    """

    logger.debug(
        "New chat. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    # Reply to the user immediately
    text = "Let's start over."
    #    "\n\nYou can always go back to previous conversations " + \
    #    "with the /history command."
    await update.message.reply_text(text)

    # Process chat data
    telegram_id = update.message.chat.id
    current_chat = await get_or_create_chat(telegram_id)

    messages_count = await get_messages_count(telegram_id, current_chat)

    if messages_count == 0:
        await delete_chat(current_chat)

    await get_or_create_chat(telegram_id, create_new_chat=True)


@send_action(ChatAction.TYPING)
async def save(update: Update, context: CallbackContext):
    """
    Generates a new summary and title for the current chat,
    and stores it in the database.
    """

    logger.debug(
        "Chat saved. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    # Reply to the user immediately
    text = "Saving the chat..."
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

        request = [None, {"role": "assistant", "content": summary}]
        title = await get_topic(request)
        current_chat.topic = title[:250]

        await save_chat(current_chat)

        text = f"Chat saved: {title}"
    else:
        text = "There are no messages in the current chat to save."

    await update.message.reply_text(text)


async def unknown(update: Update, context: CallbackContext):
    """
    Sends a message when an unknown command is entered.
    """

    entered_command = update.message.text

    logger.warning(
        "Wrong command: %s. Chat ID: %s. Username: %s",
        entered_command,
        update.message.chat_id,
        update.message.from_user.username
    )

    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.message.chat_id, text=text)


@send_action(ChatAction.TYPING)
async def chat(update: Update, context: CallbackContext):
    """
    Processes user input, generates a response using GPT-3.5,
    and sends the response to the user.
    """

    logger.debug(
        "Message sent. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    text = update.message.text
    telegram_id = update.message.chat.id
    username = update.message.from_user.username

    chat = await get_or_create_chat(telegram_id)
    request = await get_conversation_history(telegram_id, chat, text)

    request.append({"role": 'user', "content": text})

    response = await call_openai_api(request)

    answer = response['choices'][0]['message']['content']
    completion_tokens = response['usage']['completion_tokens']
    prompt_tokens = response['usage']['prompt_tokens']
    # total_tokens = response['usage']['total_tokens']

    logger.info('request: %s', text)
    logger.info('answer: %s', answer)
    logger.debug('usage: %s', response['usage'])

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


@send_action(ChatAction.TYPING)
async def retry(update: Update, context: CallbackContext):
    """
    Retries the last user's request with the same conversation history.
    """

    logger.debug(
        "Retry. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    telegram_id = update.message.chat.id
    chat = await get_or_create_chat(telegram_id)

    messages_count = await get_messages_count(telegram_id, chat)
    if messages_count == 0:
        text = "There is nothing to retry."
        await update.message.reply_text(text)
        return

    request = await get_conversation_history(telegram_id, chat)

    # Find the last user message in the conversation history
    last_user_message = None
    for message in reversed(request):
        if message["role"] == "user":
            last_user_message = message
            break

    if last_user_message is None:
        text = "There is no user message to retry."
        await update.message.reply_text(text)
        return

    response = await call_openai_api(request)

    answer = response['choices'][0]['message']['content']
    completion_tokens = response['usage']['completion_tokens']
    prompt_tokens = response['usage']['prompt_tokens']
    # total_tokens = response['usage']['total_tokens']

    logger.info("response: %s", last_user_message['content'])
    logger.info("response: %s", answer)
    logger.debug('usage: %s', response['usage'])

    # Send the response message
    await context.bot.send_message(
        chat_id=telegram_id,
        text=answer,
        parse_mode="Markdown",
    )

    # Update the last message's response in the database
    last_text_entry = await get_last_text_entry(telegram_id, chat)
    last_text_entry.response = answer
    last_text_entry.completion_tokens = completion_tokens
    last_text_entry.prompt_tokens = prompt_tokens
    await save_text_entry(last_text_entry)


@send_action(ChatAction.TYPING)
async def img(update: Update, context: CallbackContext):

    logger.debug(
        "Image requested. Chat ID: %s. Username: %s",
        update.message.chat_id,
        update.message.from_user.username
        )

    text = ' '.join(context.args)
    telegram_id = update.message.chat.id
    username = update.message.from_user.username

    chat = await get_or_create_chat(telegram_id)

    if not text:
        answer = "Usage: /img <prompt>"
        logger.warning(answer)
        await update.message.reply_text(answer)
    else:
        request = text

        response = await openai_image_create(request)

        logger.info("response: %s", response)

        # created = response['created']
        # aware_datetime = datetime.fromtimestamp(unix_epoch_time, pytz.UTC)
        image_url = response['data'][0]['url']
        # answer = image_url
        await update.message.reply_photo(photo=image_url, caption=request)

        await create_message_entry(
            chat=chat,
            telegram_id=telegram_id,
            username=username,
            request=text,
            # response=answer,
            content_type="img",
        )


async def error_handler(update: Update, context: CallbackContext) -> None:

    logger.error('Update: "%s" \nError: "%s"', update, context.error)

    # await context.bot.send_message(
    #     chat_id=update.message.chat_id,
    #     text=context.error
    # )


# async def history(update: Update, context: CallbackContext) -> None:

#     logger.debug(
#         "History requested. Chat ID: %s. Username: %s",
#         update.message.chat_id,
#         update.message.from_user.username
#         )

#     telegram_id = update.message.chat.id
#     chat = await get_or_create_chat(telegram_id)


# Function that shows the conversation history in format "chat_id: topic"
# containing all the chats of the current user
# async def history(update: Update, context: CallbackContext) -> None:
#     pass
