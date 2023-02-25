import logging


from typing import Any, Dict, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from telegram.constants import ParseMode, ChatAction

from os import getenv
from dotenv import load_dotenv
from functools import wraps

from gpt import gpt3_request


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator


load_dotenv()

TOKEN = getenv('TELEGRAM_BOT_TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define the conversation states
CHOOSING, MODEL_PARAMETERS, LANGUAGE_MODEL, TEMPERATURE, MAX_TOKENS, OTHER, MEMORY_SETTINGS, ENABLE_CONTEXT, MEMORY_SIZE = range(9)

# Define the callback data constants
SELECTING_ACTION, SELECTING_PARAMETER = range(2)

# Define the model parameters dictionary to store the values
# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
request = {
    "engine": "text-davinci-003",
    "prompt": "",
    "temperature": 0.5,
    "max_tokens": 1024,
}

# Define the memory settings dictionary to store the values
memory_settings = {
    "enable_context": True,
    "memory_size": 1024,
}


HELP_MESSAGE = """Commands:
⚙️ /settings — Change GPT-3 settings
❓ /help — Show help
📈 /stat — Show usage statistics
💾 /memo — Show current context
🆕 /new — Start new dialog
🔄 /retry — Regenerate last bot answer
"""


# Top level conversation callbacks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    reply_text = "Hi! I'm <b>GPT-3</b> bot implemented with OpenAI API 🤖\n\n"
    reply_text += HELP_MESSAGE
    reply_text += "\nAnd now... ask me anything!"

    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "What do you want to change?"

    buttons = [
        [
            InlineKeyboardButton("Model parameters", callback_data=str(SELECTING_ACTION) + "_" + str(MODEL_PARAMETERS)),
            InlineKeyboardButton("Memory settings", callback_data=str(SELECTING_ACTION) + "_" + str(MEMORY_SETTINGS)),
        ]
    ]

    # buttons = [
    #     [
    #         InlineKeyboardButton(text="Model parameters", callback_data=str(1)),
    #         InlineKeyboardButton(text="Memory settings", callback_data=str(2)),
    #     ],
    #     [
    #         InlineKeyboardButton(text="Maximum tokens", callback_data=str(3)),
    #         InlineKeyboardButton(text="Other", callback_data=str(4)),
    #     ],
    #     [
    #         InlineKeyboardButton(text=" « Back ", callback_data=str(1)),
    #     ]
    # ]

    # buttons = [
    #     [
    #         InlineKeyboardButton(text="Language model", callback_data=str(1)),
    #         InlineKeyboardButton(text="Temperature", callback_data=str(2)),
    #     ],
    #     [
    #         InlineKeyboardButton(text="Maximum tokens", callback_data=str(3)),
    #         InlineKeyboardButton(text="Other", callback_data=str(4)),
    #     ],
    #     [
    #         InlineKeyboardButton(text=" « Back ", callback_data=str(1)),
    #     ]
    # ]

    # buttons = [
    #     [
    #         InlineKeyboardButton(text="Enable context", callback_data=str(1)),
    #         InlineKeyboardButton(text="Memory size", callback_data=str(2)),
    #     ],
    #     [
    #         InlineKeyboardButton(text=" « Back ", callback_data=str(1)),
    #     ]
    # ]



    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION


async def change_temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "What sampling temperature to use, between 0 and 2. Higher values like <code>0.8</code> will make the output more random, while lower values like 0.2 will make it more focused and deterministic.\n"
        f"Current temperature: {''}"
    )

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, parse_mode='HTML')


async def help(update: Update, context: CallbackContext):
    """Show available commands."""
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


@send_action(ChatAction.TYPING)
async def retry(update: Update, context: CallbackContext):
    """Repeat the last request to OpenAI API."""
    response = gpt3_request(request)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')


async def under_construction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stub function."""
    text = "This function is not implemented yet :("
    await update.message.reply_text(text=text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return if wrong command entered."""
    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


@send_action(ChatAction.TYPING)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send request to OpenAI API and return the response."""

    request['prompt'] = update.message.text
    response = gpt3_request(request)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('settings', settings))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('stat', under_construction))
    application.add_handler(CommandHandler('memo', under_construction))
    application.add_handler(CommandHandler('new', under_construction))
    application.add_handler(CommandHandler('retry', retry))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))


    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('settings', settings)]
    # )



    application.add_handler(conv_handler)

    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()


if __name__ == "__main__":
    main()
