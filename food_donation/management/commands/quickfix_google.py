from django.core.management.base import BaseCommand
import sqlite3
import os

class Command(BaseCommand):
    help = 'Set up Google OAuth with direct database access (bypassing Django admin)'

    def add_arguments(self, parser):
        parser.add_argument('--client_id', required=True, type=str, help='Google OAuth Client ID')
        parser.add_argument('--secret', required=True, type=str, help='Google OAuth Client Secret')

    def handle(self, *args, **options):
        client_id = options['client_id']
        secret = options['secret']
        
        # Direct database manipulation - bypassing Django ORM
        db_path = os.path.join(os.getcwd(), 'db.sqlite3')
        
        self.stdout.write(f"Connecting to database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update or create site
        cursor.execute("SELECT COUNT(*) FROM django_site WHERE id=1")
        if cursor.fetchone()[0] > 0:
            cursor.execute("UPDATE django_site SET domain=?, name=? WHERE id=1", 
                          ('localhost:8000', 'localhost'))
            self.stdout.write(self.style.SUCCESS("Updated site"))
        else:
            cursor.execute("INSERT INTO django_site (id, domain, name) VALUES (1, ?, ?)",
                          ('localhost:8000', 'localhost'))
            self.stdout.write(self.style.SUCCESS("Created site"))
        
        # Delete existing Google apps
        cursor.execute("DELETE FROM socialaccount_socialapp WHERE provider='google'")
        self.stdout.write(self.style.SUCCESS("Removed existing Google OAuth settings"))
        
        # Create new Google app
        cursor.execute("""
            INSERT INTO socialaccount_socialapp 
            (provider, name, client_id, secret, key, provider_id, settings) 
            VALUES ('google', 'Google', ?, ?, '', 'google', '{}')
        """, (client_id, secret))
        
        app_id = cursor.lastrowid
        self.stdout.write(self.style.SUCCESS(f"Created Google OAuth app with ID: {app_id}"))
        
        # Associate with site
        try:
            cursor.execute("DELETE FROM socialaccount_socialapp_sites WHERE socialapp_id=?", (app_id,))
        except:
            pass
            
        cursor.execute("""
            INSERT INTO socialaccount_socialapp_sites 
            (socialapp_id, site_id) 
            VALUES (?, 1)
        """, (app_id,))
        
        conn.commit()
        conn.close()
        
        self.stdout.write(self.style.SUCCESS("\nGoogle OAuth successfully configured!"))
        self.stdout.write(self.style.SUCCESS(f"Client ID: {client_id}"))
        self.stdout.write(self.style.SUCCESS(f"Client Secret: {secret[:3]}{'*' * (len(secret) - 6)}{secret[-3:] if len(secret) > 6 else ''}\n"))
        
        self.stdout.write(self.style.SUCCESS("Use these redirect URIs in Google Console:"))
        self.stdout.write("http://localhost:8000/accounts/google/login/callback/")
        self.stdout.write("https://localhost:8000/accounts/google/login/callback/\n")
        
        self.stdout.write(self.style.SUCCESS("Test your configuration at:"))
        self.stdout.write("http://localhost:8000/accounts/google/login/") 