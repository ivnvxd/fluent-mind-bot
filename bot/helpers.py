import openai
import re
import html

from functools import wraps
from typing import Callable
from asgiref.sync import sync_to_async


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

    text = "Summarize your answer in one short title."
    request.append({"role": 'user', "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request[1:]
    )
    topic = response['choices'][0]['message']['content']

    return topic


async def get_summary(request):
    """
    Generates a summary of the conversation in one paragraph.

    :param request: A list of message dictionaries representing
    the conversation history.
    :return: A paragraph summarizing the conversation.
    """

    text = "Summarize the conversation in one paragraph."
    request.append({"role": 'user', "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request[1:]
    )
    summary = response['choices'][0]['message']['content']

    print(summary)

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
