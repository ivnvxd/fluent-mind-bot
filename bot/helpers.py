from functools import wraps
from asgiref.sync import sync_to_async


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


@sync_to_async
def save_chat(chat):
    chat.save()


@sync_to_async
def delete_chat(chat):
    chat.delete()


async def get_first_sentence(response_text):
    first_sentence = response_text.split('.')[0].strip()
    return first_sentence
