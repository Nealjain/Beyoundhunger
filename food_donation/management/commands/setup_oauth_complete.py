from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Set up Google OAuth with custom credentials'

    def add_arguments(self, parser):
        parser.add_argument('--client_id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--secret', type=str, help='Google OAuth Client Secret')
        parser.add_argument('--site_domain', type=str, default='localhost:8000', help='Site domain')
        parser.add_argument('--site_name', type=str, default='localhost', help='Site name')

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        secret = options.get('secret')
        site_domain = options.get('site_domain')
        site_name = options.get('site_name')
        
        # Use placeholder values if not provided
        if not client_id:
            client_id = 'temporary-client-id-for-testing'
            self.stdout.write(self.style.WARNING('Using placeholder Client ID. Replace with real value for production.'))
        
        if not secret:
            secret = 'temporary-secret-for-testing'
            self.stdout.write(self.style.WARNING('Using placeholder Client Secret. Replace with real value for production.'))
        
        # Configure site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': site_domain,
                'name': site_name
            }
        )
        
        if not created:
            site.domain = site_domain
            site.name = site_name
            site.save()
        
        self.stdout.write(self.style.SUCCESS(f'Site configured: {site_domain}'))
        
        # Delete any existing Google OAuth apps to avoid duplicates
        SocialApp.objects.filter(provider='google').delete()
        
        # Create new Google OAuth app
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret
        )
        
        # Associate with site
        social_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS('Google OAuth configured successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Client ID: {client_id}'))
        self.stdout.write(self.style.SUCCESS(f'Client Secret: {secret[:3]}{"*" * (len(secret) - 6)}{secret[-3:] if len(secret) > 6 else ""}'))
        
        # Show redirect URLs
        self.stdout.write(self.style.SUCCESS('\nFor Google OAuth setup, use these redirect URIs:'))
        self.stdout.write(f'http://{site_domain}/accounts/google/login/callback/')
        self.stdout.write(f'https://{site_domain}/accounts/google/login/callback/')
        
        self.stdout.write(self.style.SUCCESS('\nTo test if OAuth is working, visit:'))
        self.stdout.write(f'http://{site_domain}/accounts/google/login/') 