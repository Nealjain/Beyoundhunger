from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reset password for a given user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username whose password should be reset')
        parser.add_argument('password', type=str, help='New password')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Password reset for user "{username}"'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            # List available users
            users = User.objects.all()
            if users:
                self.stdout.write(self.style.WARNING('Available users:'))
                for user in users:
                    self.stdout.write(f' - {user.username}')
            else:
                self.stdout.write(self.style.WARNING('No users found in the database')) 