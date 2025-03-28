# Generated by Django 5.1.7 on 2025-03-14 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_donation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooddonation',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='fooddonation',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('upi', 'UPI Payment'), ('bank', 'Bank Transfer')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='fooddonation',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=10),
        ),
        migrations.AddField(
            model_name='fooddonation',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='FoodRequest',
        ),
    ]
