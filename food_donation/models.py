from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from allauth.socialaccount.signals import social_account_added

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_donor = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
        
    def get_profile_photo_url(self):
        if self.profile_photo:
            return self.profile_photo.url
        else:
            # Try to get Google social account photo
            try:
                social_account = self.user.socialaccount_set.filter(provider='google').first()
                if social_account and 'picture' in social_account.extra_data:
                    return social_account.extra_data['picture']
            except:
                pass
            return None

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
    allow_bidding = models.BooleanField(default=True, help_text="Allow users to place bids on this item")
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
        
    def get_average_bid(self):
        """Returns the average bid amount for this item"""
        from django.db.models import Avg
        return self.bids.aggregate(Avg('amount'))['amount__avg'] or 0
        
    def get_bid_count(self):
        """Returns the number of bids for this item"""
        return self.bids.count()

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

class MarketplaceBid(models.Model):
    """Model to store bids on marketplace items"""
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-amount', '-created_at']
        
    def __str__(self):
        return f"${self.amount} bid on {self.item.title} by {self.bidder.username}"
        
    def accept_bid(self):
        """Accept this bid and reject all others"""
        # Set this bid as accepted
        self.is_accepted = True
        self.is_rejected = False
        self.save()
        
        # Reject all other bids for this item
        MarketplaceBid.objects.filter(item=self.item).exclude(pk=self.pk).update(is_rejected=True, is_accepted=False)
        
        # Update the item status to pending pickup
        self.item.status = 'pending'
        self.item.save()
        
        return True

class MoneyDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    is_acknowledged = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Additional information including tax certificate requests")
    pan_number = models.CharField(max_length=10, blank=True, null=True, help_text="PAN number for tax benefit certificates")
    bank_details = models.TextField(blank=True, null=True, help_text="Bank details for donation transfer")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="QR code for easy payment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"${self.amount} by {self.donor.username}"
    
    @property
    def can_cancel(self):
        """Check if the donation can be cancelled"""
        return self.status in ['pending'] and not self.is_acknowledged
    
    class Meta:
        ordering = ['-created_at']

# Add ChatbotResponse model to store all responses
class ChatbotResponse(models.Model):
    CATEGORY_CHOICES = [
        ('greeting', 'Greeting'),
        ('food_donation', 'Food Donation'),
        ('money_donation', 'Money Donation'),
        ('volunteer', 'Volunteer'),
        ('marketplace', 'Marketplace'),
        ('account', 'Account'),
        ('general', 'General Information'),
        ('technical', 'Technical'),
        ('fallback', 'Fallback'),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    keywords = models.TextField(help_text="Comma-separated keywords that trigger this response")
    question = models.TextField(help_text="Example question that would trigger this response")
    response = models.TextField(help_text="The chatbot's response")
    priority = models.IntegerField(default=0, help_text="Higher priority responses will be chosen over lower ones when multiple keywords match")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.category}: {self.question[:50]}..."
    
    class Meta:
        ordering = ['-priority', 'category']

# Model to track chatbot interactions with users
class ChatbotMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_messages', null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    is_user_message = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat with {self.user.username if self.user else 'Anonymous'}: {self.message[:30]}..."
    
    class Meta:
        ordering = ['-created_at']

# Model for contact form submissions
class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} from {self.name}"
    
    class Meta:
        ordering = ['-created_at']

# Add signals to create UserProfile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for newly created User instances"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    """Ensure UserProfile exists when user logs in"""
    UserProfile.objects.get_or_create(user=user)

@receiver(social_account_added)
def social_account_added_handler(request, sociallogin, **kwargs):
    """Ensure UserProfile exists when a social account is added"""
    UserProfile.objects.get_or_create(user=sociallogin.user)

# Add models for marketplace chat and notifications at the end of the file
class MarketplaceChat(models.Model):
    """Model to store chat messages between buyer and seller"""
    MEDIA_TYPE_CHOICES = [
        ('', 'None'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'Other File'),
    ]
    
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    include_phone = models.BooleanField(default=False, help_text="Include sender's phone number")
    media_file = models.FileField(upload_to='marketplace_chats/', null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} about {self.item.title}"
    
    @property
    def media_url(self):
        """Return the URL of the media file if it exists"""
        if self.media_file:
            return self.media_file.url
        return None
    
    def save(self, *args, **kwargs):
        """Override save to automatically detect media type"""
        if self.media_file and not self.media_type:
            file_ext = self.media_file.name.split('.')[-1].lower()
            if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                self.media_type = 'image'
            elif file_ext in ['mp4', 'mov', 'avi', 'webm']:
                self.media_type = 'video'
            elif file_ext in ['mp3', 'wav', 'ogg']:
                self.media_type = 'audio'
            else:
                self.media_type = 'file'
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['created_at']

class Notification(models.Model):
    """Model to store user notifications"""
    TYPE_CHOICES = [
        ('message', 'New Message'),
        ('bid', 'New Bid'),
        ('bid_accepted', 'Bid Accepted'),
        ('system', 'System Notification'),
        ('admin', 'Admin Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    related_item = models.ForeignKey(MarketplaceItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    related_chat = models.ForeignKey(MarketplaceChat, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    related_bid = models.ForeignKey(MarketplaceBid, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.type} notification for {self.user.username}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class Bhandara(models.Model):
    """Model for free food distribution events (Bhandara)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    organizer_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    organizer_email = models.EmailField(blank=True, null=True)
    organizer_type = models.CharField(max_length=50, blank=True, null=True, 
        help_text="E.g., Individual, Organization, Temple, etc.")
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    food_items = models.TextField(help_text="Description of the food items available")
    expected_attendees = models.PositiveIntegerField(blank=True, null=True, 
        help_text="Estimated number of people expected to attend")
    special_instructions = models.TextField(blank=True, null=True, 
        help_text="Any special instructions for attendees")
    volunteers_needed = models.BooleanField(default=False)
    volunteers_count = models.PositiveIntegerField(blank=True, null=True, 
        help_text="Number of volunteers needed for this event")
    volunteer_tasks = models.TextField(blank=True, null=True, 
        help_text="Description of tasks volunteers will perform")
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True, null=True, 
        help_text="Daily, Weekly, Monthly, etc.")
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='bhandara/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='created_bhandaras')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['start_datetime']
        
    def is_ongoing(self):
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime
    
    def get_google_maps_url(self):
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        else:
            address = f"{self.address}, {self.city}, {self.state}, {self.postal_code}"
            return f"https://www.google.com/maps/search/?api=1&query={address}"

class VisitorLog(models.Model):
    """Model for tracking website visitors"""
    ip_address = models.CharField(max_length=50)
    user_agent = models.TextField()
    page_visited = models.CharField(max_length=255)
    referrer = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='visit_logs')
    visit_timestamp = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.ip_address} - {self.page_visited} - {self.visit_timestamp}"
    
    class Meta:
        ordering = ['-visit_timestamp']
