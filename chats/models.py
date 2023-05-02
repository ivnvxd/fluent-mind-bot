from django.db import models
from django.utils import timezone


class Chat(models.Model):
    telegram_id = models.CharField(
        max_length=25,
        verbose_name='Telegram user ID'
    )
    topic = models.CharField(
        max_length=250,
        verbose_name='Topic',
        blank=True
    )
    summary = models.CharField(
        max_length=1000,
        verbose_name='Summary',
        blank=True
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Creation date'
    )
    last_update = models.DateTimeField(
        default=timezone.now,
        verbose_name='Last update'
    )

    def __str__(self):
        return f"{self.topic}"

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'


class Text(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('img', 'Image'),
    ]
    
    telegram_id = models.CharField(
        max_length=25,
        verbose_name='Telegram user ID'
    )
    username = models.CharField(
        max_length=250,
        null=True,
        verbose_name='Username',

    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='texts',
        verbose_name='Chat'
    )
    request = models.TextField(
        max_length=10000,
        verbose_name='Request'
    )
    response = models.TextField(
        max_length=10000,
        verbose_name='Response'
    )
    content_type = models.CharField(
        max_length=4,
        choices=CONTENT_TYPE_CHOICES,
        default='text',
        verbose_name='Content Type'
    )
    date = models.DateTimeField(
        default=timezone.now,
        # auto_now_add=True,
        verbose_name='Date'
    )
    completion_tokens = models.IntegerField(
        verbose_name='Completion tokens',
        null=True
    )
    prompt_tokens = models.IntegerField(
        verbose_name='Prompt tokens',
        null=True
    )
    total_tokens = models.IntegerField(
        verbose_name='Total tokens',
        null=True
    )

    def __str__(self):
        return f"{self.request} - {self.response}"

    class Meta:
        verbose_name = 'Text'
        verbose_name_plural = 'Texts'
