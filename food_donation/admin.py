from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, FoodDonation, Volunteer, DeliveryAssignment, 
    MarketplaceLister, MarketplaceItem, MarketplaceItemImage, 
    FoodDonationImage, IDVerificationImage, MoneyDonation, ChatbotResponse,
    ChatbotMessage, ContactMessage, MarketplaceBid, MarketplaceChat, Notification
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
    list_display = ('title', 'seller', 'category', 'price', 'is_free', 'allow_bidding', 'status', 'created_at')
    list_filter = ('status', 'category', 'is_free', 'allow_bidding')
    search_fields = ('title', 'description', 'seller__username')
    inlines = [MarketplaceItemImageInline]
    actions = ['mark_as_available', 'mark_as_pending', 'mark_as_completed', 'mark_as_expired']
    
    def mark_as_available(self, request, queryset):
        queryset.update(status='available')
    mark_as_available.short_description = "Mark selected items as available"
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "Mark selected items as pending pickup"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected items as completed"
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
    mark_as_expired.short_description = "Mark selected items as expired"

class MarketplaceBidAdmin(admin.ModelAdmin):
    list_display = ('item', 'bidder', 'amount', 'is_accepted', 'is_rejected', 'created_at')
    list_filter = ('is_accepted', 'is_rejected', 'created_at')
    search_fields = ('item__title', 'bidder__username', 'message')
    actions = ['accept_bids', 'reject_bids']
    
    def accept_bids(self, request, queryset):
        for bid in queryset:
            bid.accept_bid()
    accept_bids.short_description = "Accept selected bids"
    
    def reject_bids(self, request, queryset):
        queryset.update(is_rejected=True, is_accepted=False)
    reject_bids.short_description = "Reject selected bids"

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

class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_preview', 'created_at']
    list_filter = ['created_at', 'is_user_message']
    search_fields = ['message', 'response', 'user__username']
    readonly_fields = ['user', 'message', 'response', 'is_user_message', 'created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    list_editable = ['status']
    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed']
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_as_in_progress.short_description = "Mark selected messages as In Progress"
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_as_resolved.short_description = "Mark selected messages as Resolved"
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = "Mark selected messages as Closed"

class MarketplaceChatAdmin(admin.ModelAdmin):
    list_display = ('item', 'sender', 'receiver', 'message_preview', 'include_phone', 'is_read', 'created_at')
    list_filter = ('is_read', 'include_phone', 'created_at')
    search_fields = ('item__title', 'sender__username', 'receiver__username', 'message')
    readonly_fields = ('item', 'sender', 'receiver', 'message', 'created_at')
    actions = ['mark_as_read']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('user', 'type', 'title', 'message', 'related_item', 'related_chat', 'related_bid', 'created_at')
    actions = ['mark_as_read', 'send_admin_notification']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def send_admin_notification(self, request, queryset):
        from django.contrib import messages
        from django.shortcuts import redirect
        
        # This will redirect to a custom view for sending admin notifications
        return redirect('food_donation:admin_send_notification')
    send_admin_notification.short_description = "Send a new admin notification to users"

class MoneyDonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'amount', 'payment_method', 'transaction_id', 'is_acknowledged', 'created_at']
    list_filter = ['payment_method', 'is_acknowledged', 'created_at']
    search_fields = ['donor__username', 'transaction_id']
    actions = ['mark_as_acknowledged', 'delete_selected']
    
    def mark_as_acknowledged(self, request, queryset):
        queryset.update(is_acknowledged=True)
    mark_as_acknowledged.short_description = "Mark selected donations as acknowledged"
    
    def delete_selected(self, request, queryset):
        queryset.delete()
    delete_selected.short_description = "Delete selected money donations"

# Register all models
admin.site.register(UserProfile)
admin.site.register(FoodDonation, FoodDonationAdmin)
admin.site.register(Volunteer)
admin.site.register(DeliveryAssignment)
admin.site.register(MarketplaceLister, MarketplaceListerAdmin)
admin.site.register(MarketplaceItem, MarketplaceItemAdmin)
admin.site.register(MarketplaceItemImage)
admin.site.register(MarketplaceBid, MarketplaceBidAdmin)
admin.site.register(MarketplaceChat, MarketplaceChatAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(MoneyDonation, MoneyDonationAdmin)
admin.site.register(ChatbotResponse, ChatbotResponseAdmin)
admin.site.register(ChatbotMessage, ChatbotMessageAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin) 