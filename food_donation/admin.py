from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import (
    UserProfile, FoodDonation, Volunteer, DeliveryAssignment, 
    MarketplaceLister, MarketplaceItem, MarketplaceItemImage, 
    FoodDonationImage, IDVerificationImage, MoneyDonation, ChatbotResponse,
    ChatbotMessage, ContactMessage, MarketplaceBid, MarketplaceChat, Notification,
    Bhandara, VisitorLog
)
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from django.core.files.base import ContentFile
import os
from decimal import Decimal, InvalidOperation
from .utils import send_money_donation_confirmation
import uuid

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
    actions = ['mark_as_collected', 'mark_as_delivered', 'hide_donation', 'delete_donation', 'delete_with_reason']
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
    
    def delete_with_reason(self, request, queryset):
        """Delete selected food donations and send an explanation to the donors"""
        if 'apply' in request.POST:
            reason = request.POST.get('reason', '')
            if not reason:
                self.message_user(request, "Please provide a reason for deletion.", level=messages.ERROR)
                return
                
            deleted_count = 0
            email_sent_count = 0
            
            for donation in queryset:
                try:
                    # Send email with reason if donor has email
                    if donation.donor.email:
                        from django.core.mail import send_mail
                        from django.conf import settings
                        
                        subject = "Your food donation request has been removed"
                        message = f"""Dear {donation.donor.first_name or donation.donor.username},

We regret to inform you that your food donation request for "{donation.food_type}" made on {donation.created_at.strftime('%Y-%m-%d')} has been removed from our system.

Reason: {reason}

If you have any questions or concerns, please contact our support team.

Thank you for your understanding.

BeyoundHunger Team
"""
                        try:
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[donation.donor.email],
                                fail_silently=False,
                            )
                            email_sent_count += 1
                        except Exception as e:
                            self.message_user(request, f"Error sending email to {donation.donor.email}: {str(e)}", level=messages.WARNING)
                    
                    # Delete the donation
                    donation.delete()
                    deleted_count += 1
                    
                except Exception as e:
                    self.message_user(request, f"Error processing donation {donation.id}: {str(e)}", level=messages.ERROR)
            
            self.message_user(request, f"{deleted_count} food donations deleted successfully. Notification emails sent to {email_sent_count} donors.")
            return None
            
        # Display a confirmation page with a form to enter the reason
        from django.shortcuts import render
        
        context = {
            'title': "Delete food donations with reason",
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/food_donation/fooddonation/delete_with_reason.html', context)
    delete_with_reason.short_description = "Delete with reason (notifies donor)"

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
    list_display = ('donor_info', 'amount', 'created_at', 'is_acknowledged', 'status')
    list_filter = ('is_acknowledged', 'status', 'created_at')
    search_fields = ('donor__username', 'donor__email', 'transaction_id', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_preview')
    actions = ['mark_acknowledged', 'approve_payment', 'send_thank_you', 'export_as_csv', 'delete_selected']
    
    def donor_info(self, obj):
        return f"{obj.donor.username} ({obj.donor.email})"
    donor_info.short_description = 'Donor'
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="300" />', obj.qr_code.url)
        return "No QR Code uploaded"
    qr_code_preview.short_description = 'QR Code Preview'
    
    fieldsets = (
        ('Donor Information', {
            'fields': ('donor',)
        }),
        ('Donation Details', {
            'fields': ('amount', 'payment_method', 'transaction_id', 'status', 'is_acknowledged')
        }),
        ('Bank Details & QR Code', {
            'fields': ('bank_details', 'qr_code', 'qr_code_preview'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add_manual_donation/',
                self.admin_site.admin_view(self.add_manual_donation_view),
                name='add_manual_donation'),
            path('check_user_exists/',
                self.admin_site.admin_view(self.check_user_exists_view),
                name='check_user_exists'),
        ]
        return custom_urls + urls
    
    def check_user_exists_view(self, request):
        """Check if a user with the given email exists"""
        email = request.GET.get('email', '')
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            return JsonResponse({
                'exists': True,
                'username': user.username,
                'user_id': user.id
            })
        except User.DoesNotExist:
            return JsonResponse({'exists': False})
    
    def add_manual_donation_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.contrib.auth.models import User
        from .models import MoneyDonation, Volunteer, FoodDonation
        from decimal import Decimal, InvalidOperation
        from .utils import send_money_donation_confirmation
        import uuid

        if request.method == 'POST':
            try:
                email = request.POST.get('email')
                amount = request.POST.get('amount')
                payment_method = request.POST.get('payment_method')
                transaction_id = request.POST.get('transaction_id', '')
                status = request.POST.get('status', 'approved')
                notes = request.POST.get('notes', '')
                pan_number = request.POST.get('pan_number', '')
                send_thank_you = request.POST.get('send_thank_you') == 'on'

                # Validate the amount
                if not amount:
                    messages.error(request, "Amount is required.")
                    return redirect('admin:food_donation_moneydonation_add_manual_donation')
                try:
                    amount = Decimal(amount)
                    if amount <= 0:
                        messages.error(request, "Amount must be greater than zero.")
                        return redirect('admin:food_donation_moneydonation_add_manual_donation')
                except InvalidOperation:
                    messages.error(request, "Amount must be a valid number.")
                    return redirect('admin:food_donation_moneydonation_add_manual_donation')

                # Find the user by email
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    messages.error(request, f"No user found with email {email}")
                    return redirect('admin:food_donation_moneydonation_add_manual_donation')

                # Create the donation
                donation = MoneyDonation.objects.create(
                    donor=user,
                    amount=amount,
                    payment_method=payment_method,
                    transaction_id=transaction_id or f"MANUAL-{str(uuid.uuid4())[:8]}",
                    notes=notes,
                    pan_number=pan_number,
                    status=status,
                    is_acknowledged=True,
                )

                # Send thank you email if requested
                if send_thank_you:
                    # Send thank you email
                    send_money_donation_confirmation(user, donation)
                    messages.success(request, f"Donation of ${amount} by {email} created successfully. Thank you email sent.")
                else:
                    messages.success(request, f"Donation of ${amount} by {email} created successfully.")

                return redirect('admin:food_donation_moneydonation_changelist')
            except Exception as e:
                messages.error(request, f"Error adding donation: {str(e)}")
                return redirect('admin:food_donation_moneydonation_add_manual_donation')

        # Get statistics for dashboard
        money_donations_count = MoneyDonation.objects.count()
        active_volunteers = Volunteer.objects.filter(availability=True).count()
        
        # Estimate lives impacted (each donation impacts approximately 3 people)
        total_donations = MoneyDonation.objects.count() + FoodDonation.objects.filter(status='delivered').count()
        lives_impacted = total_donations * 3
        
        # Prepare payment method choices for the template
        payment_methods = [
            ('bank', 'Bank Transfer'),
            ('upi', 'UPI Payment'),
            ('cash', 'Cash'),
            ('check', 'Check'),
            ('card', 'Credit/Debit Card'),
            ('paypal', 'PayPal'),
            ('other', 'Other')
        ]

        # Getting all stats
        all_money_donations = MoneyDonation.objects.all()
        total_money_donated = sum(donation.amount for donation in all_money_donations)
        total_approved_money_donated = sum(donation.amount for donation in all_money_donations if donation.status == 'approved')
        
        # Render the template with all statistics
        context = {
            'title': 'Add Manual Donation',
            'opts': self.model._meta,
            'payment_methods': payment_methods,
            'money_donations_count': money_donations_count,
            'active_volunteers': active_volunteers,
            'lives_impacted': lives_impacted,
            'total_money_donated': total_money_donated,
            'total_approved_money_donated': total_approved_money_donated,
            'has_view_permission': self.has_view_permission(request),
            'has_add_permission': self.has_add_permission(request),
            'app_label': self.model._meta.app_label,
            'media': self.media,
        }
        return render(request, 'admin/food_donation/moneydonation/add_manual_donation.html', context)

    def mark_acknowledged(self, request, queryset):
        updated = queryset.update(is_acknowledged=True)
        self.message_user(request, f"{updated} donations marked as acknowledged.")
    mark_acknowledged.short_description = "Mark selected donations as acknowledged"
    
    def approve_payment(self, request, queryset):
        from .utils import send_money_donation_confirmation
        count = 0
        for donation in queryset:
            if donation.donor.email:
                try:
                    # Mark as acknowledged and approved
                    donation.is_acknowledged = True
                    donation.status = 'approved'
                    donation.save()
                    
                    # Send receipt email
                    send_money_donation_confirmation(donation.donor, donation, is_receipt=True)
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Error processing donation for {donation.donor.email}: {str(e)}", level=messages.ERROR)
        
        self.message_user(request, f"{count} payments approved and receipts sent successfully.")
    approve_payment.short_description = "Approve payments and send receipts"
    
    def send_thank_you(self, request, queryset):
        from .utils import send_money_donation_confirmation
        count = 0
        for donation in queryset:
            if donation.donor.email:
                try:
                    send_money_donation_confirmation(donation.donor, donation)
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Error sending email to {donation.donor.email}: {str(e)}", level=messages.ERROR)
        self.message_user(request, f"Thank you emails sent to {count} donors.")
    send_thank_you.short_description = "Send thank you emails to selected donors"
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from io import StringIO
        
        f = StringIO()
        writer = csv.writer(f)
        
        # Write header row
        writer.writerow(['Donor', 'Email', 'Amount', 'Payment Method', 'Transaction ID', 'Status', 'Acknowledged', 'PAN Number', 'Date'])
        
        # Write data rows
        for obj in queryset:
            writer.writerow([
                obj.donor.username,
                obj.donor.email,
                obj.amount,
                obj.payment_method,
                obj.transaction_id,
                obj.status,
                'Yes' if obj.is_acknowledged else 'No',
                obj.pan_number or '',
                obj.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        # Create the HTTP response
        response = HttpResponse(f.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=money_donations.csv'
        
        return response
    export_as_csv.short_description = "Export selected donations as CSV"
    
    def delete_selected(self, request, queryset):
        count = queryset.count()
        result = queryset.delete()
        self.message_user(request, f"{count} donations deleted successfully.")
    delete_selected.short_description = "Delete selected donations"

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