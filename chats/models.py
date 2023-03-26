from django.db import models


class Chat(models.Model):
    role = models.CharField(
        max_length=25,
        verbose_name='Role'
    )
    user_id = models.CharField(
        max_length=25,
        verbose_name='User ID'
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

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
