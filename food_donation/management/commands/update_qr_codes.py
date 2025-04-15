from django.core.management.base import BaseCommand
from food_donation.models import MoneyDonation
from django.core.files.base import ContentFile
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates all existing MoneyDonation objects with a default QR code and bank details'

    def handle(self, *args, **options):
        # Update all donations with bank details
        bank_details = 'Account Name: Beyond Hunger Foundation\nAccount Number: 12345678901234\nIFSC Code: SBIN0012345\nBank Name: State Bank of India\nBranch: Main Branch, New Delhi\nAccount Type: Current Account'
        
        MoneyDonation.objects.update(
            bank_details=bank_details
        )

        self.stdout.write(self.style.SUCCESS('Successfully updated bank details for all donations'))

        # Add QR code to donations that don't have one
        qr_filename = 'bobqrcode.JPG'
        
        # Check in multiple locations
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', qr_filename),
            os.path.join(settings.BASE_DIR, qr_filename),
            os.path.join(settings.STATIC_ROOT, 'images', qr_filename) if hasattr(settings, 'STATIC_ROOT') else None,
            os.path.join(settings.MEDIA_ROOT, 'images', qr_filename) if hasattr(settings, 'MEDIA_ROOT') else None
        ]
        
        qr_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                qr_path = path
                self.stdout.write(f'Found QR code at: {qr_path}')
                break
        
        if qr_path:
            count = 0
            empty_qr_donations = MoneyDonation.objects.filter(qr_code='')
            self.stdout.write(f'Found {empty_qr_donations.count()} donations without QR code')
            
            for donation in empty_qr_donations:
                try:
                    with open(qr_path, 'rb') as f:
                        donation.qr_code.save('donation_qr_code.jpg', ContentFile(f.read()), save=True)
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating QR code for donation {donation.id}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully added QR code to {count} donations'))
        else:
            self.stdout.write(self.style.ERROR(f'QR code file {qr_filename} not found in any of the expected locations')) 