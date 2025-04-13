from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from food_donation.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile for users who don\'t have one'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            try:
                user.userprofile
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(
                    user=user,
                    phone='',
                    address='',
                    is_donor=False,
                    is_volunteer=False
                )
                created_count += 1
                self.stdout.write(f'Created UserProfile for user {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} UserProfile(s)')) 