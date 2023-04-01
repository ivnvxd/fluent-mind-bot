from functools import wraps
from asgiref.sync import sync_to_async

from chats.models import Text, Chat


system = {"role": "system", "content": "You are a helpful assistant."}


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
def get_or_create_chat(telegram_id, create_new_chat=False):
    if create_new_chat:
        chat = Chat.objects.create(telegram_id=telegram_id)
    else:
        chat = Chat.objects.filter(
            telegram_id=telegram_id
        ).order_by('-creation_date').first()
        if not chat:
            chat = Chat.objects.create(telegram_id=telegram_id)
    return chat


@sync_to_async
def get_messages_count(telegram_id, chat):
    return Text.objects.filter(telegram_id=telegram_id, chat=chat).count()


@sync_to_async
def create_message_entry(chat, **kwargs):
    text = Text.objects.create(chat=chat, **kwargs)
    return text


@sync_to_async
def get_conversation_history(telegram_id, chat):
    messages = Text.objects.filter(
        telegram_id=telegram_id, chat=chat
    ).order_by('date')

    request = [system]
    for message in messages:
        request.extend([
            {"role": "user", "content": message.request},
            {"role": "assistant", "content": message.response}
        ])

    return request


@sync_to_async
def save_chat(chat):
    chat.save()


@sync_to_async
def delete_chat(chat):
    chat.delete()


async def get_first_sentence(response_text):
    first_sentence = response_text.split('.')[0].strip()
    return first_sentence
