import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update)
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
from telegram.constants import (
    ParseMode,
    ChatAction
)

from os import getenv
from dotenv import load_dotenv
from functools import wraps

from gpt import gpt3_completion, gpt3_edit
from settings import (
    model_parameters,
    language_model,
    temperature,
    set_temperature,
    maximum_tokens,
    memory_settings,
    memory_enable,
    memory_size
)
from constants import (
    HELP_MESSAGE,
    SELECTING_SETTING,
    MODEL_PARAMETERS,
    MEMORY_SETTINGS,
    LANGUAGE_MODEL,
    TEMPERATURE,
    MAXIMUM_TOKENS,
    MEMORY_ENABLE,
    MEMORY_SIZE,
)
from gpt import request, memory


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
        CallbackQueryHandler(language_model, pattern="^" + str(LANGUAGE_MODEL) + "$"),
        CallbackQueryHandler(temperature, pattern="^" + str(TEMPERATURE) + "$"),
        CallbackQueryHandler(maximum_tokens, pattern="^" + str(MAXIMUM_TOKENS) + "$"),
        CallbackQueryHandler(settings, pattern="^" + str(SELECTING_SETTING) + "$"),
    ]

    memory_handlers = [
        CallbackQueryHandler(memory_enable, pattern="^" + str(MEMORY_ENABLE) + "$"),
        CallbackQueryHandler(memory_size, pattern="^" + str(MEMORY_SIZE) + "$"),
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
                # CallbackQueryHandler(temperature, pattern="^" + str(TEMPERATURE) + "$"),
                # CallbackQueryHandler(model_parameters, pattern="^" + str(MODEL_PARAMETERS) + "$"),
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
