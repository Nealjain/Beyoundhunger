from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    is_donor = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class FoodDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI Payment'),
        ('bank', 'Bank Transfer'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    food_type = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    expiry_date = models.DateField()
    pickup_address = models.TextField()
    pickup_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Payment fields
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_hidden = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_type} donation by {self.donor.username}"

class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    availability = models.BooleanField(default=True)
    vehicle_type = models.CharField(max_length=50, blank=True)
    service_area = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Volunteer"

class DeliveryAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    pickup_time = models.DateTimeField()
    delivery_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery by {self.volunteer.user.username} for {self.donation}"

class MarketplaceItem(models.Model):
    CATEGORY_CHOICES = [
        ('produce', 'Fresh Produce'),
        ('pantry', 'Pantry Items'),
        ('dairy', 'Dairy & Eggs'),
        ('bakery', 'Bakery Items'),
        ('prepared', 'Prepared Foods'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending Pickup'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    quantity = models.CharField(max_length=50)
    expiry_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='marketplace/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def is_expired(self):
        if not self.expiry_date:
            return False
            
        # If expiry_date is a string, convert it to a date object
        if isinstance(self.expiry_date, str):
            try:
                from datetime import datetime
                expiry_date = datetime.strptime(self.expiry_date, '%Y-%m-%d').date()
            except ValueError:
                # If conversion fails, return False
                return False
        else:
            expiry_date = self.expiry_date
            
        # Compare with current date
        if expiry_date < timezone.now().date():
            return True
        return False
    
    def save(self, *args, **kwargs):
        if self.is_expired() and self.status != 'expired':
            self.status = 'expired'
        super().save(*args, **kwargs)

class MarketplaceLister(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    id_verification = models.CharField(max_length=100, help_text="ID number for verification")
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Marketplace Lister"
        
    def is_approved(self):
        return self.status == 'approved'

class IDVerificationImage(models.Model):
    """Model to store multiple ID verification images for MarketplaceLister"""
    lister = models.ForeignKey(MarketplaceLister, on_delete=models.CASCADE, related_name='id_images')
    image = models.ImageField(upload_to='id_verification/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"ID Image for {self.lister.user.username}"

class FoodDonationImage(models.Model):
    """Model to store multiple images for food donations"""
    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='food_donations/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for donation by {self.donation.donor.username}"

class MarketplaceItemImage(models.Model):
    """Model to store multiple images for marketplace items"""
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='marketplace/multi/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Image for {self.item.title}"

class MoneyDonation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"${self.amount} by {self.donor.username}"
    
    class Meta:
        ordering = ['-created_at']
