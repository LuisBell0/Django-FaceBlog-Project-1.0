# Generated by Django 5.0.2 on 2024-05-06 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_profile_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pictures/default', null=True, upload_to='profile_pictures'),
        ),
    ]
