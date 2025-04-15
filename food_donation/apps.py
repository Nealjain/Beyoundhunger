from django.apps import AppConfig


class FoodDonationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'food_donation'
    
    def ready(self):
        import food_donation.signals