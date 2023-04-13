import openai
import re
import html
import tiktoken

from functools import wraps
from typing import Callable
from asgiref.sync import sync_to_async

from .database import get_message_objects


MAX_TOKENS = 4096
TOKENS_BUFFER = 100

system = {"role": "system", "content": "You are a helpful assistant."}


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
                action=action
            )
            return await func(update, context, *args, **kwargs)
        return command_func
    return decorator


async def call_openai_api(request):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request
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


async def get_topic(request):
    """
    Generates a short sentence describing the topic of the answer.

    :param request: A list of message dictionaries representing
    the conversation history.
    :return: A short sentence summarizing the answer's topic.
    """

    text = "Summarize your answer in one very short title."
    request.append({"role": 'user', "content": text})

    response = call_openai_api(request[1:])
    topic = response['choices'][0]['message']['content']

    return topic


async def get_summary(request):
    """
    Generates a summary of the conversation in one paragraph.

    :param request: A list of message dictionaries representing
    the conversation history.
    :return: A paragraph summarizing the conversation.
    """

    text = "Summarize the conversation in one short paragraph."
    request.append({"role": 'user', "content": text})

    response = call_openai_api(request[1:])
    summary = response['choices'][0]['message']['content']

    return summary


def markdown_code_to_html(text):
    """
    Converts markdown code blocks to HTML.

    :param text: A string containing markdown code blocks.
    :return: A string with markdown code blocks replaced by HTML code blocks.
    """

    text = html.escape(text)

    triple_code_pattern = re.compile(r'```(.*?)```', re.DOTALL)
    text = triple_code_pattern.sub(r'<pre><code>\1</code></pre>', text)

    single_code_pattern = re.compile(r'`([^`]+)`')
    text = single_code_pattern.sub(r'<code>\1</code>', text)

    return text


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

    messages = get_message_objects(telegram_id, chat)
    truncated_messages = truncate_messages(messages, text)

    request = [system]
    for message in reversed(truncated_messages):
        request.extend([
            {"role": "user", "content": message.request},
            {"role": "assistant", "content": message.response}
        ])

    return request


@sync_to_async
def save_text_entry(text_entry):
    """
    Saves the provided text entry instance asynchronously.
    """

    text_entry.save()
