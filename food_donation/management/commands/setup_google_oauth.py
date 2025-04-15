from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Sets up a temporary Google OAuth configuration for testing'

    def handle(self, *args, **options):
        # Get or create the current site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'localhost'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created site: localhost:8000'))
        else:
            # Update site if it exists
            site.domain = 'localhost:8000'
            site.name = 'localhost'
            site.save()
            self.stdout.write(self.style.SUCCESS('Updated site: localhost:8000'))
        
        # Create or update the Google social app
        social_app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': 'temporary-client-id-for-testing',
                'secret': 'temporary-secret-for-testing',
            }
        )
        
        if created:
            social_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('Created Google social app'))
        else:
            # Make sure the site is associated
            social_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('Updated Google social app'))
        
        self.stdout.write(self.style.SUCCESS(
            'Google OAuth configuration has been set up for testing. '
            'Replace with real credentials in the Django admin before deploying.'
        )) 