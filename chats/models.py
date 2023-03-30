from django.db import models


class Text(models.Model):
    role = models.CharField(
        max_length=25,
        verbose_name='Role'
    )
    telegram_id = models.CharField(
        max_length=25,
        verbose_name='Telegram user ID'
    )
    username = models.CharField(
        max_length=250,
        verbose_name='Username'
    )
    text = models.TextField(
        max_length=10000,
        verbose_name='Text'
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date'
    )
    tokens = models.IntegerField(
        verbose_name='Tokens'
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Text'
        verbose_name_plural = 'Texts'


class Chat(models.Model):
    pass
