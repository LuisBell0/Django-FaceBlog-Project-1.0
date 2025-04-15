# Generated by Django 5.0.2 on 2024-06-14 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0028_comment_posted_hour_client_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='posted_hour_client',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='posted_hour_server',
        ),
        migrations.AlterField(
            model_name='comment',
            name='posted_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
