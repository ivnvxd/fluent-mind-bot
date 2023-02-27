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

from constants import (
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
            InlineKeyboardButton(text="Model", callback_data=str(LANGUAGE_MODEL)),
            InlineKeyboardButton(text="Temperature", callback_data=str(TEMPERATURE)),
            InlineKeyboardButton(text="Max. Tokens", callback_data=str(MAXIMUM_TOKENS)),
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


async def language_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Multiple models, each with different capabilities and price points. <b>Ada</b> is the fastest model, while <b>Davinci</b> is the most powerful.\n\n"
        f"Current model: <b>{request['engine']}</b>"
    )

    buttons = [
        [
            InlineKeyboardButton(text="text-davinci-003", callback_data=str(1)),
            InlineKeyboardButton(text="text-curie-001", callback_data=str(1))
        ],
        [
            InlineKeyboardButton(text="text-babbage-001", callback_data=str(1)),
            InlineKeyboardButton(text="text-ada-001", callback_data=str(1))
        ],
        [
            InlineKeyboardButton(text="« Back", callback_data=str(MODEL_PARAMETERS))
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')

    return LANGUAGE_MODEL


async def temperature(update: Update, context: CallbackContext):
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


async def maximum_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "The maximum number of <b>tokens</b> to generate in the completion.\n"
        "The token count of your prompt plus <i>max_tokens</i> cannot exceed the model's context length.\n\n"
        f"Current maximum tokens: <b>{request['max_tokens']}</b>"
    )

    buttons = [
        [
            InlineKeyboardButton(text="« Back", callback_data=str(MODEL_PARAMETERS))
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')

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


async def memory_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return MEMORY_ENABLE


async def memory_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return MEMORY_SIZE
