import openai
import re
import html

from functools import wraps
from typing import Callable
from asgiref.sync import sync_to_async


def send_action(action: str) -> Callable:
    """Sends `action` while processing func command."""

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
    chat.save()


@sync_to_async
def delete_chat(chat):
    chat.delete()


async def get_topic(request):
    text = "Summarize your answer as briefly as possible in one short sentence."
    request.append({"role": 'user', "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=request[1:]
    )
    topic = response['choices'][0]['message']['content']

    return topic


def markdown_code_to_html(text):
    text = html.escape(text)

    triple_code_pattern = re.compile(r'```(.*?)```', re.DOTALL)
    text = triple_code_pattern.sub(r'<pre><code>\1</code></pre>', text)

    single_code_pattern = re.compile(r'`([^`]+)`')
    text = single_code_pattern.sub(r'<code>\1</code>', text)

    return text
