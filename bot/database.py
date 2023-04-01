from asgiref.sync import sync_to_async

from chats.models import Text, Chat


system = {"role": "system", "content": "You are a helpful assistant."}


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
