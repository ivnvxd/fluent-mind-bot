import openai
import tiktoken
import logging

from colorlog import ColoredFormatter
from functools import wraps
from typing import Callable
from asgiref.sync import sync_to_async

from bot import database


MAX_TOKENS = 4096
TOKENS_BUFFER = 200

system = {"role": "system", "content": "You are a helpful assistant."}


def setup_colored_logging(level=logging.DEBUG):
    """
    Set up colored logging with the given logging level.

    :param level: The logging level to set up. Default is logging.DEBUG.
    :return: The logger object.
    """

    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    logger.addHandler(console_handler)
    # logger.propagate = False

    return logger


logger = setup_colored_logging()


def send_action(action: str) -> Callable:
    """
    A decorator that sends a specified chat action while processing
    the wrapped function.

    :param action: The chat action to send.
    :return: A decorator for the function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id,
                # chat_id=update.message.chat_id,
                action=action
            )
            return await func(update, context, *args, **kwargs)
        return command_func
    return decorator


async def call_openai_api(request):
    """
    Calls the OpenAI API for chat completion using the provided `request`.

    :param request: A list of strings representing the chat history.
    return: A dictionary containing the response from the OpenAI API.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request
    )
    return response


async def openai_image_create(request):
    """
    Creates an image using OpenAI's API.

    :param request: The prompt to generate the image from.
    return: The response from OpenAI's API, containing the generated image.
    """

    response = openai.Image.create(
        prompt=request,
        n=1,
        size="1024x1024"
    )
    return response


@sync_to_async
def save_chat(chat):
    """
    Saves the provided chat instance asynchronously.
    """

    chat.save()


@sync_to_async
def delete_chat(chat):
    """
    Deletes the provided chat instance asynchronously.
    """

    chat.delete()


@sync_to_async
def save_text_entry(text_entry):
    """
    Saves the provided text entry instance asynchronously.
    """

    text_entry.save()


async def get_topic(request):
    """
    Generates a short sentence describing the topic of the answer.

    :param request: A list of message dictionaries representing
    the conversation history.
    :return: A short sentence summarizing the answer's topic.
    """

    # text = "Summarize the conversation in one very short title."
    text = "Title the conversation in one short sentence."
    request.append({"role": 'user', "content": text})

    response = await call_openai_api(request[1:])
    topic = response['choices'][0]['message']['content']

    logger.info('topic: %s', topic)
    logger.debug('usage: %s', response['usage'])

    return topic


async def get_summary(request):
    """
    Generates a summary of the conversation in one paragraph.

    :param request: A list of message dictionaries representing
    the conversation history.
    :return: A paragraph summarizing the conversation.
    """

    text = (
        "Summarize the conversation in one short paragraph. "
        "Don't use introductory words, just convey the meaning."
    )
    request.append({"role": 'user', "content": text})

    response = await call_openai_api(request[1:])
    summary = response['choices'][0]['message']['content']

    logger.info('summary: %s', summary)
    logger.debug('usage: %s', response['usage'])

    return summary


def num_tokens_from_string(string: str) -> int:
    """
    Returns the number of tokens in a text string.

    :param string: A string to be tokenized.
    :return: Number of tokens in the string.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))

    return num_tokens


def truncate_messages(messages, text):
    """
    Truncates the messages based on the token limit.

    :param messages: A list of message objects to truncate.
    :param text: The last message from the user.
    :return: A list of truncated message objects.
    """

    truncated_messages = []
    total_tokens = 0

    for message in messages:
        system_tokens = num_tokens_from_string(system['content'])
        request_tokens = num_tokens_from_string(message.request)
        response_tokens = num_tokens_from_string(message.response)
        text_tokens = num_tokens_from_string(text)

        temp_tokens = system_tokens + text_tokens + TOKENS_BUFFER
        message_tokens = request_tokens + response_tokens

        if total_tokens + temp_tokens + message_tokens <= MAX_TOKENS:
            truncated_messages.append(message)
            total_tokens += message_tokens
        else:
            logger.debug('Truncated messages from: %s', message)
            break

    return truncated_messages


@sync_to_async
def get_conversation_history(telegram_id, chat, text=""):
    """
    Gets the conversation history of a specific chat.

    :param telegram_id: The user's Telegram ID.
    :param chat: The Chat instance to get the conversation history from.
    :param text: The last message from the user.
    :return: A list of message dictionaries representing
    the conversation history.
    """

    messages = database.get_message_objects(telegram_id, chat)
    truncated_messages = truncate_messages(messages, text)

    request = [system]
    for message in reversed(truncated_messages):
        request.extend([
            {"role": "user", "content": message.request},
            {"role": "assistant", "content": message.response}
        ])

    return request
