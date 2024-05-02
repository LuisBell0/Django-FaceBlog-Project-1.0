# Generated by Django 5.0.2 on 2024-05-01 18:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_post_posted_hour_client_alter_post_posted_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='posted_date',
            field=models.DateField(blank=True, default=datetime.date(2024, 5, 1), null=True),
        ),
    ]
