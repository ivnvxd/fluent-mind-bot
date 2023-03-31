from django.db import models


class Text(models.Model):
    telegram_id = models.CharField(
        max_length=25,
        verbose_name='Telegram user ID'
    )
    username = models.CharField(
        max_length=250,
        null=True,
        # blank=True,
        verbose_name='Username',

    )
    request = models.TextField(
        max_length=10000,
        verbose_name='Request'
    )
    response = models.TextField(
        max_length=10000,
        verbose_name='Response'
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date'
    )
    completion_tokens = models.IntegerField(
        verbose_name='Completion tokens'
    )
    prompt_tokens = models.IntegerField(
        verbose_name='Prompt tokens'
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Text'
        verbose_name_plural = 'Texts'


class Chat(models.Model):
    pass
