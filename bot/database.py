from asgiref.sync import sync_to_async

from chats.models import Text, Chat


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

    count = Text.objects.filter(telegram_id=telegram_id, chat=chat).count()
    return count


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


def get_message_objects(telegram_id, chat):
    """
    Gets the message objects for a specific chat.

    :param telegram_id: The user's Telegram ID.
    :param chat: The Chat instance to get the message objects from.
    :return: A queryset containing the message objects.
    """

    messages = Text.objects.filter(
        telegram_id=telegram_id, chat=chat
    ).order_by('-date')

    return messages
