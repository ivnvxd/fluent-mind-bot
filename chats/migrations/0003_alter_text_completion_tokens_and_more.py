# Generated by Django 4.2 on 2023-05-02 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0002_alter_text_completion_tokens_alter_text_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='completion_tokens',
            field=models.IntegerField(null=True, verbose_name='Completion tokens'),
        ),
        migrations.AlterField(
            model_name='text',
            name='prompt_tokens',
            field=models.IntegerField(null=True, verbose_name='Prompt tokens'),
        ),
    ]