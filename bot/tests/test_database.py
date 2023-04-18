from django.test import TestCase
from asgiref.sync import async_to_sync
from chats.models import Chat, Text
from bot.database import (
    get_or_create_chat,
    get_messages_count,
    create_message_entry,
    get_message_objects,
    get_last_text_entry
)


class BotDatabaseTestCase(TestCase):
    def setUp(self):
        self.telegram_id = '12345'
        self.chat = Chat.objects.create(telegram_id=self.telegram_id)

    def test_get_or_create_chat(self):
        chat = async_to_sync(get_or_create_chat)(self.telegram_id)
        self.assertIsNotNone(chat)
        self.assertEqual(chat.telegram_id, self.telegram_id)

    def test_get_messages_count(self):
        Text.objects.create(
            telegram_id=self.telegram_id,
            chat=self.chat,
            request="Test request",
            response="Test response",
            completion_tokens=5,
            prompt_tokens=5
        )

        count = async_to_sync(get_messages_count)(self.telegram_id, self.chat)
        self.assertEqual(count, 1)

    def test_create_message_entry(self):
        text = async_to_sync(create_message_entry)(
            self.chat,
            telegram_id=self.telegram_id,
            request="Test request",
            response="Test response",
            completion_tokens=5,
            prompt_tokens=5
        )
        self.assertIsNotNone(text)
        self.assertEqual(text.request, "Test request")
        self.assertEqual(text.response, "Test response")

    def test_get_message_objects(self):
        Text.objects.create(
            telegram_id=self.telegram_id,
            chat=self.chat,
            request="Test request",
            response="Test response",
            completion_tokens=5,
            prompt_tokens=5
        )

        messages = get_message_objects(self.telegram_id, self.chat)
        self.assertEqual(messages.count(), 1)

    def test_get_last_text_entry(self):
        text_entry = Text.objects.create(
            telegram_id=self.telegram_id,
            chat=self.chat,
            request="Test request",
            response="Test response",
            completion_tokens=5,
            prompt_tokens=5
        )

        last_text_entry = async_to_sync(get_last_text_entry)(
            self.telegram_id, self.chat
        )
        self.assertIsNotNone(last_text_entry)
        self.assertEqual(last_text_entry.id, text_entry.id)
