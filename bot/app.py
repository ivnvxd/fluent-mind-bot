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

from gpt import gpt3_completion


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


# State definitions for top level conversation
SELECTING_SETTING, MODEL_PARAMETERS, MEMORY_SETTINGS = map(chr, range(3))

LANGUAGE_MODEL, TEMPERATURE, MAXIMUM_TOKENS = map(chr, range(3, 6))

MEMORY_ENABLE, MEMORY_SIZE = map(chr, range(6, 8))

# Meta states
BACK, S = map(chr, range(8, 10))


# Define the callback data constants

# Define the model parameters dictionary to store the values
# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
request = {
    "engine": "text-davinci-003",
    "prompt": "",
    "temperature": 0.5,
    "max_tokens": 1024,
}

# Define the memory settings dictionary to store the values
memory = {
    "enable_memory": True,
    "memory_size": 1024,
}


HELP_MESSAGE = """Available commands:
⚙️ /settings — Change GPT-3 settings
❓ /help — Show help
📈 /stat — Show usage statistics
💾 /memo — Show current context
🆕 /new — Start new dialog
🔄 /retry — Regenerate last bot answer
"""


@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request['prompt'] = "Say in free form that your name is FluentMind, you are a GPT-3 Chatbot implemented with OpenAI API and you are ready to answer any questions."

    text = "🤖: " + gpt3_completion(request)
    text += "\n\n" + HELP_MESSAGE

    request['prompt'] = ""

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):


    text = "What do you want to change?"

    buttons = [
        [
            InlineKeyboardButton("Model parameters", callback_data=str(MODEL_PARAMETERS)),
            InlineKeyboardButton("Memory settings", callback_data=str(MEMORY_SETTINGS)),
        ],
        [
            InlineKeyboardButton(text="Done", callback_data=str('/start')),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard, parse_mode='HTML')

    return SELECTING_SETTING


async def model_parameters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "What do you want to change?\n\n"
        "<i>Current settings:</i>\n"
        f"Language model: <b>{request['engine']}</b>\n"
        f"Temperature: <b>{request['temperature']}</b>\n"
        f"Maximum tokens: <b>{request['max_tokens']}</b>"
    )

    buttons = [
        [
            InlineKeyboardButton(text="Language model", callback_data=str(LANGUAGE_MODEL)),
            InlineKeyboardButton(text="Temperature", callback_data=str(TEMPERATURE)),
            InlineKeyboardButton(text="Maximum tokens", callback_data=str(MAXIMUM_TOKENS)),
        ],
        [
            InlineKeyboardButton(text="« Back", callback_data=str(SELECTING_SETTING)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')

    return MODEL_PARAMETERS


async def change_lang_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return LANGUAGE_MODEL


async def change_temp(update: Update, context: CallbackContext):
    text = (
        "What sampling temperature to use, between <b>0</b> and <b>2</b>. Higher values like <b>0.8</b> will make the output more random, while lower values like <b>0.2</b> will make it more focused and deterministic.\n\n"
        f"Current temperature: <b>{request['temperature']}</b>"
    )

    buttons = [
        [
            InlineKeyboardButton(text="« Back", callback_data=str(MODEL_PARAMETERS))
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')

    return TEMPERATURE


async def set_temperature(update: Update, context: CallbackContext):
    temperature = update.message.text

    request['temperature'] = temperature

    confirmation_text = f"Temperature set to {temperature}."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=confirmation_text, parse_mode='HTML')

    return await model_parameters(update, context)
    # return ConversationHandler.END


async def change_max_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return MAXIMUM_TOKENS


async def memory_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "What do you want to change?\n\n"
        "<i>Current settings:</i>\n"
        f"Memory enabled: <b>{memory['enable_memory']}</b>\n"
        f"Memory size (tokens): <b>{memory['memory_size']}</b>"
    )

    if memory['enable_memory']:
        memory_enable = "Disable memory"
    else:
        memory_enable = "Enable memory"

    buttons = [
        [
            InlineKeyboardButton(text=memory_enable, callback_data=str(MEMORY_ENABLE)),
            InlineKeyboardButton(text="Memory size", callback_data=str(MEMORY_SIZE)),
        ],
        [
            InlineKeyboardButton(text="« Back", callback_data=str(SELECTING_SETTING)),
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')

    return MEMORY_SETTINGS


async def enable_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return MEMORY_ENABLE


async def change_memory_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return MEMORY_SIZE


async def help(update: Update, context: CallbackContext):
    """Show available commands."""
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


@send_action(ChatAction.TYPING)
async def retry(update: Update, context: CallbackContext):
    """Repeat the last request to OpenAI API."""
    response = gpt3_completion(request)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')


async def under_construction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stub function."""
    text = f"This function is not implemented yet :("
    await update.message.reply_text(text=text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return if wrong command entered."""
    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


@send_action(ChatAction.TYPING)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send request to OpenAI API and return the response."""

    request['prompt'] = update.message.text
    response = gpt3_completion(request)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    model_handlers = [
        CallbackQueryHandler(change_lang_model, pattern="^" + str(LANGUAGE_MODEL) + "$"),
        CallbackQueryHandler(change_temp, pattern="^" + str(TEMPERATURE) + "$"),
        CallbackQueryHandler(change_max_tokens, pattern="^" + str(MAXIMUM_TOKENS) + "$"),
        CallbackQueryHandler(settings, pattern="^" + str(SELECTING_SETTING) + "$"),
    ]

    memory_handlers = [
        CallbackQueryHandler(enable_memory, pattern="^" + str(MEMORY_ENABLE) + "$"),
        CallbackQueryHandler(change_memory_size, pattern="^" + str(MEMORY_SIZE) + "$"),
        CallbackQueryHandler(settings, pattern="^" + str(SELECTING_SETTING) + "$"),
    ]

    settings_handler = ConversationHandler(
        entry_points=[CommandHandler('settings', settings)],
        states={
            SELECTING_SETTING: [
                CallbackQueryHandler(model_parameters, pattern="^" + str(MODEL_PARAMETERS) + "$"),
                CallbackQueryHandler(memory_settings, pattern="^" + str(MEMORY_SETTINGS) + "$"),
            ],
            MODEL_PARAMETERS: model_handlers,
            MEMORY_SETTINGS: memory_handlers,
            TEMPERATURE: [
                CallbackQueryHandler(change_temp, pattern="^" + str(TEMPERATURE) + "$"),
                CallbackQueryHandler(model_parameters, pattern="^" + str(MODEL_PARAMETERS) + "$"),
                MessageHandler(filters.TEXT & (~filters.COMMAND), set_temperature),
            ]
        },
        fallbacks=[
            CommandHandler('settings', settings),
            CallbackQueryHandler(model_parameters, pattern="^" + str(MODEL_PARAMETERS) + "$"),
                   ],
    )

    application.add_handler(settings_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('stat', under_construction))
    application.add_handler(CommandHandler('memo', under_construction))
    application.add_handler(CommandHandler('new', under_construction))
    application.add_handler(CommandHandler('retry', retry))
    # application.add_handler(CallbackQueryHandler(get_temperature))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()


if __name__ == "__main__":
    main()
