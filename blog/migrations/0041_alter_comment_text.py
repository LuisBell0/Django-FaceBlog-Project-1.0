# Generated by Django 5.0.2 on 2025-04-02 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0040_notification_content_type_notification_object_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=255),
        ),
    ]
