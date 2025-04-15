from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create a new superuser admin account with predefined credentials'

    def handle(self, *args, **options):
        # Predefined credentials
        username = 'superadmin'
        email = 'admin@example.com'
        password = 'Admin123@'

        # First check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists. Updating password...'))
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Password updated for "{username}"'))
            self.stdout.write(self.style.SUCCESS(f'You can now login with:'))
            self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
            self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
            return

        # Create new superuser
        try:
            user = User.objects.create_superuser(username=username, email=email, password=password)
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" was created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'You can now login with:'))
            self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
            self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f'Error creating superuser. Username or email might be in use.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 