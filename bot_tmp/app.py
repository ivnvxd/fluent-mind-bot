import logging
import openai

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
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


load_dotenv()

TOKEN = getenv('TELEGRAM_BOT_TOKEN')
API_KEY = getenv('OPENAI_API_KEY')
openai.api_key = API_KEY

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

HELP_MESSAGE = """Available commands:
❓ /help — Show help
"""


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id,
                action=action
            )
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator


@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot."""

    text = "Hi! I'm <b>ChatGPT</b> bot implemented with GPT-3.5 OpenAI API 🤖\n\n"
    text += HELP_MESSAGE
    text += "\nAnd now... ask me anything!"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def help(update: Update, context: CallbackContext):
    """Show available commands."""

    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return if wrong command entered."""

    text = "Sorry, I didn't understand that command."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


@send_action(ChatAction.TYPING)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send request to OpenAI API and return the response."""

    request = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": request}
        ]
    )

    print(response)

    answer = response['choices'][0]['message']['content']

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer,
        parse_mode='HTML'
    )


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        echo
    ))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()


if __name__ == "__main__":
    main()
