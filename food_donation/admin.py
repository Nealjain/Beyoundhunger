from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, FoodDonation, Volunteer, DeliveryAssignment, 
    MarketplaceLister, MarketplaceItem, MarketplaceItemImage, 
    FoodDonationImage, IDVerificationImage, MoneyDonation, ChatbotResponse
)

class FoodDonationImageInline(admin.TabularInline):
    model = FoodDonationImage
    extra = 0
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

class FoodDonationAdmin(admin.ModelAdmin):
    list_display = ['id', 'donor', 'food_type', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'food_type', 'created_at']
    search_fields = ['donor__username', 'food_type']
    actions = ['mark_as_collected', 'mark_as_delivered', 'hide_donation', 'delete_donation']
    inlines = [FoodDonationImageInline]
    
    def mark_as_collected(self, request, queryset):
        queryset.update(status='collected')
    mark_as_collected.short_description = "Mark selected donations as collected"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected donations as delivered"
    
    def hide_donation(self, request, queryset):
        queryset.update(is_hidden=True)
    hide_donation.short_description = "Hide selected donations"
    
    def delete_donation(self, request, queryset):
        queryset.delete()
    delete_donation.short_description = "Delete selected donations"

class IDVerificationImageInline(admin.TabularInline):
    model = IDVerificationImage
    extra = 0
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return "No ID Image"
    image_preview.short_description = 'ID Preview'

class MarketplaceListerAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']
    actions = ['approve_lister', 'reject_lister']
    inlines = [IDVerificationImageInline]
    
    def approve_lister(self, request, queryset):
        queryset.update(status='approved')
    approve_lister.short_description = "Approve selected marketplace applications"
    
    def reject_lister(self, request, queryset):
        queryset.update(status='rejected')
    reject_lister.short_description = "Reject selected marketplace applications"

class MarketplaceItemImageInline(admin.TabularInline):
    model = MarketplaceItemImage
    extra = 0
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

class MarketplaceItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'category', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'description', 'seller__username']
    inlines = [MarketplaceItemImageInline]

class ChatbotResponseAdmin(admin.ModelAdmin):
    list_display = ['category', 'question', 'keywords_short', 'priority', 'is_active']
    list_filter = ['category', 'is_active', 'priority']
    search_fields = ['question', 'response', 'keywords']
    list_editable = ['priority', 'is_active']
    actions = ['duplicate_response']
    
    def keywords_short(self, obj):
        return obj.keywords[:50] + '...' if len(obj.keywords) > 50 else obj.keywords
    keywords_short.short_description = 'Keywords'
    
    def duplicate_response(self, request, queryset):
        for obj in queryset:
            obj.pk = None
            obj.question = f"COPY - {obj.question}"
            obj.is_active = False
            obj.save()
        self.message_user(request, f"{queryset.count()} response(s) duplicated. Edit the copies as needed.")
    duplicate_response.short_description = "Duplicate selected responses"

# Register all models
admin.site.register(UserProfile)
admin.site.register(FoodDonation, FoodDonationAdmin)
admin.site.register(Volunteer)
admin.site.register(DeliveryAssignment)
admin.site.register(MarketplaceLister, MarketplaceListerAdmin)
admin.site.register(MarketplaceItem, MarketplaceItemAdmin)
admin.site.register(MoneyDonation)
admin.site.register(ChatbotResponse, ChatbotResponseAdmin) 