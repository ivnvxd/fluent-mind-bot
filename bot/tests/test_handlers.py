from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message, Bot
from telegram.ext import CallbackContext
from bot import handlers


class AsyncMagicMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMagicMock, self).__call__(*args, **kwargs)


class TestMessage(Message):
    async def reply_text(self, *args, **kwargs):
        pass


class CallbackContextProxy:
    def __init__(self, bot: Bot, *args, **kwargs):
        self._callback_context = CallbackContext(*args, **kwargs)
        self._bot = bot

    def __getattr__(self, name):
        if name == 'bot':
            return self._bot
        return getattr(self._callback_context, name)


class TestHandlers(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        message_data = {
            'message_id': 1,
            'from': {'id': 1, 'first_name': 'Test', 'is_bot': False},
            'chat': {'id': 1, 'type': 'private'},
            'text': None,
            'date': None,
        }
        message = TestMessage.de_json(message_data, None)
        self.update = Update(update_id=1, message=message)
        bot_instance = AsyncMagicMock(spec=Bot)
        self.context = CallbackContextProxy(
            bot_instance, AsyncMock(), MagicMock()
        )

        handlers.call_openai_api = AsyncMock(
            return_value={
                'choices': [{'message': {'content': 'Test answer'}}],
                'usage': {'completion_tokens': 5, 'prompt_tokens': 10},
            }
        )
        handlers.get_conversation_topic = AsyncMock(
            return_value="Test topic"
        )
        handlers.get_conversation_summary = AsyncMock(
            return_value="Test summary"
        )
        handlers.get_or_create_chat = AsyncMock(
            return_value=AsyncMock()
        )
        handlers.get_messages_count = AsyncMock(return_value=5)
        handlers.get_conversation_history = AsyncMock(return_value=[])
        handlers.save_chat = AsyncMock()
        handlers.delete_chat = AsyncMock()
        handlers.create_message_entry = AsyncMock()
        handlers.save_text_entry = AsyncMock()
        handlers.get_last_text_entry = AsyncMock(
            return_value=AsyncMock()
        )

    async def test_start(self):
        await handlers.start(self.update, self.context)
        # self.context.bot.send_message.assert_called_once()

    async def test_help(self):
        await handlers.help(self.update, self.context)
        self.context.bot.send_message.assert_called_once()

    async def test_new(self):
        await handlers.new(self.update, self.context)
        # self.context.bot.send_message.assert_called()
        handlers.get_or_create_chat.assert_called()
        handlers.get_messages_count.assert_called()

    async def test_save(self):
        await handlers.save(self.update, self.context)
        # self.context.bot.send_message.assert_called()
        handlers.get_or_create_chat.assert_called()
        handlers.get_messages_count.assert_called()
        handlers.get_conversation_history.assert_called()
        handlers.save_chat.assert_called()

    async def test_unknown(self):
        await handlers.unknown(self.update, self.context)
        self.context.bot.send_message.assert_called_once()

    async def test_chat(self):
        await handlers.chat(self.update, self.context)
        self.context.bot.send_message.assert_called()
        handlers.get_or_create_chat.assert_called()
        handlers.get_conversation_history.assert_called()
        handlers.call_openai_api.assert_called()
        handlers.create_message_entry.assert_called()
        handlers.save_chat.assert_called()
