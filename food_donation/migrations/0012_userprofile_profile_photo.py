# Generated by Django 5.1.7 on 2025-04-14 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_donation', '0011_chatbotmessage_contactmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
    ]
