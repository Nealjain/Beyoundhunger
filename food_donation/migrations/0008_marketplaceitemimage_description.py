# Generated by Django 5.1.7 on 2025-04-13 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_donation', '0007_remove_chathistory_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplaceitemimage',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
