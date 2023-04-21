import asyncio
from django.test import TestCase
from unittest.mock import AsyncMock, patch
from telegram import Update, Chat, User, Message
from telegram.ext import CallbackContext

from bot.helpers import (
    send_action, get_topic, get_summary, save_chat, delete_chat,
    get_conversation_history, save_text_entry, call_openai_api
)
from bot.database import get_or_create_chat, create_message_entry
from bot.handlers import ChatAction


TELEGRAM_ID = 12345
USERNAME = "testuser"
CHAT_ID = 67890
TEXT = "test_text"
RESPONSE_TEXT = "test_response"
API_RESPONSE = {
    'choices': [
        {'message': {'content': RESPONSE_TEXT}}
    ],
    'usage': {'completion_tokens': 5, 'prompt_tokens': 10},
}

update = Update(
    update_id=1,
    message=Message(
        message_id=1,
        date=None,
        chat=Chat(
            id=CHAT_ID,
            type='private',
        ),
        text=TEXT,
        from_user=User(
            id=TELEGRAM_ID,
            first_name="Test",
            is_bot=False,
            username=USERNAME
        ),
    )
)
context = CallbackContext(None, None, None)


class TestHelpers(TestCase):
    async def test_get_topic(self):
        with patch("bot.helpers.call_openai_api", return_value=API_RESPONSE):
            request = [{'role': 'user', 'content': TEXT}]
            topic = await get_topic(request)
            self.assertEqual(topic, RESPONSE_TEXT)

    async def test_get_summary(self):
        with patch("bot.helpers.call_openai_api", return_value=API_RESPONSE):
            request = [{'role': 'user', 'content': TEXT}]
            summary = await get_summary(request)
            self.assertEqual(summary, RESPONSE_TEXT)

    async def test_save_delete_chat(self):
        chat = await get_or_create_chat(TELEGRAM_ID)
        self.assertIsNotNone(chat)
        await save_chat(chat)
        await delete_chat(chat)

    async def test_get_conversation_history(self):
        chat = await get_or_create_chat(TELEGRAM_ID)
        await create_message_entry(
            chat=chat,
            telegram_id=TELEGRAM_ID,
            username=USERNAME,
            request=TEXT,
            response=RESPONSE_TEXT,
            completion_tokens=5,
            prompt_tokens=10,
        )
        request = await get_conversation_history(TELEGRAM_ID, chat, TEXT)
        self.assertEqual(len(request), 3)
        self.assertEqual(request[1]['role'], 'user')
        self.assertEqual(request[1]['content'], TEXT)
        self.assertEqual(request[2]['role'], 'assistant')
        self.assertEqual(request[2]['content'], RESPONSE_TEXT)

    async def test_save_text_entry(self):
        chat = await get_or_create_chat(TELEGRAM_ID)
        message_entry = await create_message_entry(
            chat=chat,
            telegram_id=TELEGRAM_ID,
            username=USERNAME,
            request=TEXT,
            response=RESPONSE_TEXT,
            completion_tokens=5,
            prompt_tokens=10,
            )
        message_entry.response = "updated_response"
        await save_text_entry(message_entry)

    def test_send_action_decorator(self):
        mock_bot = AsyncMock()
        mock_update = AsyncMock()
        mock_update.effective_message.chat_id = CHAT_ID
        mock_context = AsyncMock()
        mock_context.bot = mock_bot

        @send_action(ChatAction.TYPING)
        async def dummy_handler(update, context):
            return "dummy response"

        result = asyncio.run(dummy_handler(mock_update, mock_context))

        mock_bot.send_chat_action.assert_called_with(
            chat_id=mock_update.effective_message.chat_id,
            action=ChatAction.TYPING
        )

        self.assertEqual(result, "dummy response")

    @patch("bot.helpers.openai.ChatCompletion.create")
    async def test_call_openai_api(self, mock_create):
        mocked_response = {
            'choices': [
                {'message': {'content': 'Sample response from the OpenAI API.'}}
            ],
        }
        mock_create.return_value = mocked_response

        request = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]

        response = await call_openai_api(request)

        mock_create.assert_called_with(model="gpt-3.5-turbo", messages=request)

        self.assertEqual(response, mocked_response)
