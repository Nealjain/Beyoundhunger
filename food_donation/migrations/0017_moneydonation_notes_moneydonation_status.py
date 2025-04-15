# Generated by Django 5.0.14 on 2025-04-15 03:28

from django.db import migrations, models

def set_default_status(apps, schema_editor):
    MoneyDonation = apps.get_model('food_donation', 'MoneyDonation')
    # Set status based on acknowledgment
    for donation in MoneyDonation.objects.all():
        donation.status = 'approved' if donation.is_acknowledged else 'pending'
        donation.save(update_fields=['status'])

class Migration(migrations.Migration):

    dependencies = [
        ('food_donation', '0016_bhandara_visitorlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='moneydonation',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='moneydonation',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.RunPython(set_default_status, migrations.RunPython.noop),
    ]
