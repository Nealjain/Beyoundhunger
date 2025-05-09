# Generated by Django 5.1.7 on 2025-04-14 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_donation', '0014_marketplaceitem_allow_bidding_marketplacechat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplacechat',
            name='media_file',
            field=models.FileField(blank=True, null=True, upload_to='marketplace_chats/'),
        ),
        migrations.AddField(
            model_name='marketplacechat',
            name='media_type',
            field=models.CharField(blank=True, choices=[('', 'None'), ('image', 'Image'), ('video', 'Video'), ('audio', 'Audio'), ('file', 'Other File')], default='', max_length=10),
        ),
    ]
