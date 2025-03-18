from django.contrib import admin
from .models import UserProfile, FoodDonation, Volunteer, DeliveryAssignment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_donor', 'is_volunteer', 'created_at')
    list_filter = ('is_donor', 'is_volunteer')
    search_fields = ('user__username', 'phone', 'address')

@admin.register(FoodDonation)
class FoodDonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'food_type', 'quantity', 'status', 'payment_status', 'pickup_date', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'pickup_date')
    search_fields = ('donor__username', 'food_type', 'pickup_address', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability', 'vehicle_type', 'service_area', 'created_at')
    list_filter = ('availability', 'vehicle_type')
    search_fields = ('user__username', 'service_area')

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('donation', 'volunteer', 'status', 'pickup_time', 'delivery_time', 'created_at')
    list_filter = ('status', 'pickup_time', 'delivery_time')
    search_fields = ('donation__food_type', 'volunteer__user__username') 