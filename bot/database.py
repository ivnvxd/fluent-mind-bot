from asgiref.sync import sync_to_async

from chats.models import Text, Chat


system = {"role": "system", "content": "You are a helpful assistant."}


@sync_to_async
def get_or_create_chat(telegram_id, create_new_chat=False):
    """
    Gets or creates a chat instance.

    :param telegram_id: The user's Telegram ID.
    :param create_new_chat: A boolean indicating whether to create
    a new chat instance.
    :return: A Chat instance.
    """

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
    """
    Gets the number of messages in the specified chat.
    """
    return Text.objects.filter(telegram_id=telegram_id, chat=chat).count()


@sync_to_async
def create_message_entry(chat, **kwargs):
    """
    Creates a new Text instance with the provided kwargs.

    :param chat: The Chat instance the message belongs to.
    :param kwargs: The keyword arguments to create the Text instance.
    :return: The created Text instance.
    """

    text = Text.objects.create(chat=chat, **kwargs)
    return text


@sync_to_async
def get_conversation_history(telegram_id, chat):
    """
    Gets the conversation history of a specific chat.

    :param telegram_id: The user's Telegram ID.
    :param chat: The Chat instance to get the conversation history from.
    :return: A list of message dictionaries representing
    the conversation history.
    """

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
