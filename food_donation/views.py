from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import (
    UserProfile, FoodDonation, Volunteer, DeliveryAssignment, 
    MarketplaceLister, MarketplaceItem, MarketplaceItemImage, 
    FoodDonationImage, IDVerificationImage, MoneyDonation, ContactMessage, MarketplaceBid, MarketplaceChat, Notification
)
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q
from django.core.paginator import Paginator
import os
from django.db import connection
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, FileResponse, JsonResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from PIL import Image
from django.contrib.auth.decorators import user_passes_test
import csv
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.views.decorators.http import require_POST
import uuid
from .utils import send_money_donation_confirmation

def home(request):
    # Get 5 most recent donations for the recent donations section
    recent_donations = FoodDonation.objects.order_by('-created_at')[:5]
    
    # Get recent donations with profile photos for donor showcase (up to 3)
    donor_showcase = []
    processed_donors = set()  # To track which donors we've already processed
    
    # Get all recent donations
    all_recent_donations = FoodDonation.objects.select_related('donor__userprofile').order_by('-created_at')[:20]
    
    # Process each donation to find unique donors with photos
    for donation in all_recent_donations:
        # Skip if we already have 3 donors or if we've already processed this donor
        if len(donor_showcase) >= 3 or donation.donor.id in processed_donors:
            continue
            
        try:
            donor = donation.donor
            profile = donor.userprofile
            
            # Get donor's photo URL
            photo_url = profile.get_profile_photo_url()
            
            if photo_url:  # Only include donors with photos
                donor_showcase.append({
                    'name': donor.get_full_name() or donor.username,
                    'photo_url': photo_url,
                    'food_type': donation.food_type,
                    'quantity': donation.quantity,
                    'date': donation.created_at,
                })
                processed_donors.add(donor.id)  # Mark this donor as processed
        except Exception as e:
            # If there's an error getting profile info, skip this donor
            print(f"Error getting donor showcase info: {str(e)}")
            continue
    
    context = {
        'total_donations': FoodDonation.objects.count(),
        'total_volunteers': Volunteer.objects.count(),
        'total_requests': FoodDonation.objects.filter(status='delivered').count(),
        'recent_donations': recent_donations,
        'donor_showcase': donor_showcase,  # Add the donor showcase data
    }
    return render(request, 'food_donation/home.html', context)

def money_donate(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        transaction_id = request.POST.get('transaction_id', '')
        payment_method = request.POST.get('payment_method', 'other')
        
        if amount and request.user.is_authenticated:
            money_donation = MoneyDonation.objects.create(
                donor=request.user,
                amount=float(amount),
                transaction_id=transaction_id,
                payment_method=payment_method,
                is_acknowledged=True
            )
            # Send email confirmation if email is configured
            try:
                send_money_donation_confirmation(request.user, money_donation)
            except:
                pass  # Handle silently if email sending fails
            messages.success(request, "Thank you for your donation! It has been recorded.")
            return redirect('food_donation:money_donation_history')
        elif amount and not request.user.is_authenticated:
            messages.error(request, "Please log in to make a donation.")
            return redirect('food_donation:login')
        else:
            messages.error(request, "Please enter a valid amount.")
    return render(request, 'food_donation/money_donate.html')

@login_required
def donate(request):
    # Get current date for minimum date fields
    current_date = timezone.now().date().isoformat()
    
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': ''
        }
    )
    
    # Pre-populate data from user profile
    initial_data = {
        'pickup_address': user_profile.address,
    }
    
    if request.method == 'POST':
        # Create the donation
        donation = FoodDonation(
            donor=request.user,
            food_type=request.POST['food_type'],
            quantity=request.POST['quantity'],
            expiry_date=request.POST['expiry_date'],
            pickup_address=request.POST['pickup_address'],
            pickup_date=request.POST['pickup_date'],
            notes=request.POST.get('notes', '')
        )
        
        # Handle payment information if provided
        if 'payment_method' in request.POST and request.POST['payment_method']:
            donation.payment_method = request.POST['payment_method']
            donation.payment_status = 'pending'
            
            if 'amount' in request.POST and request.POST['amount']:
                donation.amount = Decimal(request.POST['amount'])
                
            # Generate a simple transaction ID (in a real app, this would be from a payment processor)
            donation.transaction_id = str(uuid.uuid4())[:10]
            
            payment_method_display = 'UPI' if donation.payment_method == 'upi' else 'Bank Transfer'
            messages.info(request, f'Your payment of ₹{donation.amount} via {payment_method_display} is being processed. Transaction ID: {donation.transaction_id}')
        
        # Save the donation to get an ID
        donation.save()
        
        # Handle food images
        if 'food_images' in request.FILES:
            for image in request.FILES.getlist('food_images'):
                FoodDonationImage.objects.create(
                    donation=donation,
                    image=image
                )
        
        messages.success(request, 'Thank you for your donation! A receipt has been generated and is available for download from your profile page.')
        return redirect('food_donation:profile')
    
    context = {
        'initial_data': initial_data,
        'current_date': current_date
    }
    return render(request, 'food_donation/donate.html', context)

def about(request):
    return render(request, 'food_donation/about.html')

def contact(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Create contact message
        contact_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )
        
        # Associate with user if logged in
        if request.user.is_authenticated:
            contact_msg.user = request.user
        
        contact_msg.save()
        
        # Optional: Send email notification to admin
        try:
            admin_subject = f"New Contact Form Submission: {subject}"
            admin_message = fr"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
            admin_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 10px; }}
                    .content {{ padding: 20px; border: 1px solid #ddd; }}
                    .field {{ margin-bottom: 10px; }}
                    .label {{ font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>New Contact Form Submission</h2>
                    </div>
                    <div class="content">
                        <div class="field">
                            <span class="label">Name:</span> {name}
                        </div>
                        <div class="field">
                            <span class="label">Email:</span> {email}
                        </div>
                        <div class="field">
                            <span class="label">Phone:</span> {phone or 'Not provided'}
                        </div>
                        <div class="field">
                            <span class="label">Subject:</span> {subject}
                        </div>
                        <div class="field">
                            <span class="label">Message:</span><br>
                            {message.replace('\n', '<br>')}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email to admin
            from_email = 'Beyond Hunger <beyoundhunger1@gmail.com>'
            to_email = 'beyoundhunger1@gmail.com'  # Admin email
            
            email = EmailMultiAlternatives(admin_subject, admin_message, from_email, [to_email])
            email.attach_alternative(admin_html, "text/html")
            email.send()
            
        except Exception as e:
            # Log error but don't show to user
            print(f"Error sending admin notification: {str(e)}")
        
        messages.success(request, 'Thank you for your message. We will get back to you soon.')
        return redirect('food_donation:contact')
    
    return render(request, 'food_donation/contact.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('food_donation:register')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile(
            user=user,
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            is_donor='is_donor' in request.POST,
            is_volunteer='is_volunteer' in request.POST
        )
        profile.save()
        
        if profile.is_volunteer:
            volunteer = Volunteer(
                user=user,
                vehicle_type=request.POST.get('vehicle_type', ''),
                service_area=request.POST.get('service_area', '')
            )
            volunteer.save()
            
        login(request, user, backend='food_donation.auth.EmailOrUsernameModelBackend')
        messages.success(request, 'Registration successful!')
        return redirect('food_donation:profile')
    return render(request, 'food_donation/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('food_donation:profile')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'food_donation/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('food_donation:home')

@login_required
def profile(request):
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': ''
        }
    )
    
    food_donations = FoodDonation.objects.filter(donor=request.user)
    money_donations = MoneyDonation.objects.filter(donor=request.user)
    
    # Get all food donation images
    food_images = {}
    for donation in food_donations:
        food_images[donation.id] = FoodDonationImage.objects.filter(donation=donation)
    
    context = {
        'user_profile': user_profile,
        'food_donations': food_donations,
        'money_donations': money_donations,
        'food_images': food_images,
    }
    if user_profile.is_volunteer:
        volunteer = Volunteer.objects.get(user=request.user)
        context['volunteer'] = volunteer
        context['assignments'] = DeliveryAssignment.objects.filter(volunteer=volunteer).order_by('-created_at')
    return render(request, 'food_donation/profile.html', context)

@login_required
def custom_admin_dashboard(request):
    """Custom admin dashboard view"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('food_donation:home')
    
    # Get all donations
    donations = FoodDonation.objects.all().order_by('-created_at')
    
    # Get all assignments
    assignments = DeliveryAssignment.objects.all().order_by('-created_at')
    
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # Get all volunteers
    volunteers = Volunteer.objects.all().order_by('-created_at')
    
    # Get pending marketplace listers
    marketplace_listers = MarketplaceLister.objects.filter(status='pending').order_by('-created_at')
    
    # Calculate statistics
    total_users = User.objects.count()
    total_donors = UserProfile.objects.filter(is_donor=True).count()
    total_volunteers = Volunteer.objects.count()
    total_donations = FoodDonation.objects.count()
    pending_donations = FoodDonation.objects.filter(status='pending').count()
    completed_donations = FoodDonation.objects.filter(status='delivered').count()
    cancelled_donations = FoodDonation.objects.filter(status='cancelled').count()
    active_assignments = DeliveryAssignment.objects.filter(status__in=['assigned', 'in_progress']).count()
    
    stats = {
        'total_users': total_users,
        'total_donors': total_donors,
        'total_volunteers': total_volunteers,
        'total_donations': total_donations,
        'pending_donations': pending_donations,
        'completed_donations': completed_donations,
        'cancelled_donations': cancelled_donations,
        'active_assignments': active_assignments,
    }
    
    # Get status choices for dropdowns
    donation_status_choices = FoodDonation.STATUS_CHOICES
    assignment_status_choices = DeliveryAssignment.STATUS_CHOICES
    
    context = {
        'donations': donations,
        'assignments': assignments,
        'users': users,
        'volunteers': volunteers,
        'marketplace_listers': marketplace_listers,
        'stats': stats,
        'donation_status_choices': donation_status_choices,
        'assignment_status_choices': assignment_status_choices,
    }
    
    return render(request, 'food_donation/admin_dashboard.html', context)

@login_required
def update_donation_status(request, donation_id):
    # Check if user is a superuser (admin)
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to update donation status.')
        return redirect('food_donation:home')
    
    if request.method == 'POST':
        donation = FoodDonation.objects.get(id=donation_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(FoodDonation.STATUS_CHOICES).keys():
            donation.status = new_status
            donation.save()
            messages.success(request, f'Donation status updated to {dict(FoodDonation.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status.')
            
    return redirect('food_donation:admin_dashboard')

@login_required
def update_assignment_status(request, assignment_id):
    # Check if user is a superuser (admin)
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to update assignment status.')
        return redirect('food_donation:home')
    
    if request.method == 'POST':
        assignment = DeliveryAssignment.objects.get(id=assignment_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(DeliveryAssignment.STATUS_CHOICES).keys():
            assignment.status = new_status
            assignment.save()
            
            # If status is delivered, update the delivery time
            if new_status == 'delivered':
                assignment.delivery_time = timezone.now()
                assignment.save()
                
                # Also update the donation status
                if assignment.donation.status != 'delivered':
                    assignment.donation.status = 'delivered'
                    assignment.donation.save()
            
            messages.success(request, f'Assignment status updated to {dict(DeliveryAssignment.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status.')
            
    return redirect('food_donation:admin_dashboard')

# Marketplace views
def marketplace(request):
    """View for the marketplace homepage with filtering"""
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    show_free = request.GET.get('free', '') == 'on'
    
    # Use select_related and prefetch_related for efficient loading
    items = MarketplaceItem.objects.filter(status='available')\
        .select_related('seller')\
        .prefetch_related('bids')\
        .order_by('-created_at')
    
    # Apply filters
    if category:
        items = items.filter(category=category)
    if search_query:
        items = items.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    if show_free:
        items = items.filter(is_free=True)
    
    # Paginate results
    paginator = Paginator(items, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = dict(MarketplaceItem.CATEGORY_CHOICES)
    
    # Check if user is already a lister
    is_lister = False
    lister_status = None
    if request.user.is_authenticated:
        try:
            lister = MarketplaceLister.objects.get(user=request.user)
            is_lister = True
            lister_status = lister.status
        except MarketplaceLister.DoesNotExist:
            pass
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query,
        'show_free': show_free,
        'total_items': items.count(),
        'is_lister': is_lister,
        'lister_status': lister_status,
    }
    return render(request, 'food_donation/marketplace.html', context)

@login_required
def marketplace_item_detail(request, pk):
    """View details of a marketplace item"""
    item = get_object_or_404(MarketplaceItem, pk=pk)
    is_owner = request.user == item.seller
    
    # Get all additional images
    additional_images = MarketplaceItemImage.objects.filter(item=item)
    
    # Check if item is expired and update if needed
    if item.is_expired() and item.status != 'expired':
        item.status = 'expired'
        item.save()
    
    # Get bids for this item
    bids = []
    user_bid = None
    highest_bid = None
    
    if not item.is_free:
        # Get all bids for this item, ordered by amount (highest first)
        all_bids = MarketplaceBid.objects.filter(item=item).order_by('-amount')
        
        if is_owner:
            # If owner, show all bids
            bids = all_bids
        
        # Get current user's bid
        if request.user.is_authenticated and not is_owner:
            user_bid = MarketplaceBid.objects.filter(item=item, bidder=request.user).first()
        
        # Get the highest bid
        highest_bid = all_bids.first()
    
    # Get bid statistics
    bid_count = item.get_bid_count()
    avg_bid = item.get_average_bid()
    
    # Check for existing conversations between seller and current user
    has_conversation = False
    if request.user.is_authenticated and not is_owner:
        has_conversation = MarketplaceChat.objects.filter(
            item=item,
            sender=request.user,
            receiver=item.seller
        ).exists() or MarketplaceChat.objects.filter(
            item=item,
            sender=item.seller,
            receiver=request.user
        ).exists()
    
    context = {
        'item': item,
        'is_owner': is_owner,
        'additional_images': additional_images,
        'bids': bids,
        'user_bid': user_bid,
        'highest_bid': highest_bid,
        'total_bids': bid_count,
        'average_bid': avg_bid,
        'has_conversation': has_conversation
    }
    return render(request, 'food_donation/marketplace_item_detail.html', context)

@login_required
def apply_marketplace_lister(request):
    """View for users to apply to become marketplace listers"""
    # Check if user already has an application
    try:
        existing_application = MarketplaceLister.objects.get(user=request.user)
        messages.warning(request, 'You have already applied to become a marketplace lister.')
        return redirect('food_donation:marketplace_lister_status')
    except MarketplaceLister.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Create lister application
        lister = MarketplaceLister(
            user=request.user,
            business_name=request.POST.get('business_name', ''),
            id_verification=request.POST.get('id_verification', ''),
            contact_phone=request.POST.get('contact_phone', ''),
            address=request.POST.get('address', '')
        )
        # Save the lister to get an ID
        lister.save()
        
        # Handle ID verification images
        if 'id_images' in request.FILES:
            for image in request.FILES.getlist('id_images'):
                IDVerificationImage.objects.create(
                    lister=lister,
                    image=image
                )
        
        messages.success(request, 'Your application to become a marketplace lister has been submitted. We will review your details shortly.')
        return redirect('food_donation:marketplace_lister_status')
    
    # Pre-fill form with user profile data if available
    try:
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'phone': '',
                'address': ''
            }
        )
        initial_data = {
            'contact_phone': user_profile.phone,
            'address': user_profile.address,
        }
    except:
        initial_data = {}
    
    return render(request, 'food_donation/apply_marketplace_lister.html', {'initial_data': initial_data})

@login_required
def marketplace_lister_status(request):
    """View for users to check their marketplace lister application status"""
    try:
        lister = MarketplaceLister.objects.get(user=request.user)
        id_images = IDVerificationImage.objects.filter(lister=lister)
        return render(request, 'food_donation/marketplace_lister_status.html', {
            'lister': lister,
            'id_images': id_images
        })
    except MarketplaceLister.DoesNotExist:
        messages.error(request, 'You have not applied to become a marketplace lister yet.')
        return redirect('food_donation:apply_marketplace_lister')

@login_required
def create_marketplace_item(request):
    """Create a new marketplace item - requires approved lister status"""
    # Check if user is an approved marketplace lister
    try:
        lister = MarketplaceLister.objects.get(user=request.user)
        if not lister.is_approved():
            messages.error(request, 'Your marketplace lister application has not been approved yet. You cannot create listings until approved.')
            return redirect('food_donation:marketplace_lister_status')
    except MarketplaceLister.DoesNotExist:
        messages.error(request, 'You need to be a verified marketplace lister to create listings.')
        return redirect('food_donation:apply_marketplace_lister')
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        location = request.POST.get('location')
        expiry_date = request.POST.get('expiry_date') or None
        is_free = 'is_free' in request.POST
        allow_bidding = 'allow_bidding' in request.POST
        
        # Create item
        item = MarketplaceItem(
            seller=request.user,
            title=title,
            description=description,
            category=category,
            quantity=quantity,
            location=location,
            is_free=is_free,
            allow_bidding=allow_bidding,
        )
        
        # Handle expiry date
        if expiry_date:
            try:
                from datetime import datetime
                item.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                # If date format is incorrect, set to None
                item.expiry_date = None
        else:
            item.expiry_date = None
        
        # Handle price (only if not free)
        if not is_free:
            price = request.POST.get('price')
            if price:
                item.price = Decimal(price)
        
        # Handle main image if provided
        if 'main_image' in request.FILES:
            item.image = request.FILES['main_image']
        
        # Save the item first to get an ID
        item.save()
        
        # Handle multiple additional images
        if 'additional_images' in request.FILES:
            for image in request.FILES.getlist('additional_images'):
                MarketplaceItemImage.objects.create(
                    item=item,
                    image=image
                )
        
        messages.success(request, 'Your item has been listed on the marketplace!')
        return redirect('food_donation:marketplace_item_detail', pk=item.pk)
    
    context = {
        'categories': MarketplaceItem.CATEGORY_CHOICES,
        'current_date': timezone.now().date().isoformat(),
    }
    return render(request, 'food_donation/create_marketplace_item.html', context)

@login_required
def edit_marketplace_item(request, pk):
    """Edit an existing marketplace item"""
    item = get_object_or_404(MarketplaceItem, pk=pk)
    
    # Check if the current user is the owner
    if request.user != item.seller:
        messages.error(request, 'You do not have permission to edit this listing.')
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    if request.method == 'POST':
        # Update item details
        item.title = request.POST.get('title')
        item.description = request.POST.get('description')
        item.category = request.POST.get('category')
        item.quantity = request.POST.get('quantity')
        item.location = request.POST.get('location')
        
        # Handle expiry date
        expiry_date = request.POST.get('expiry_date')
        if expiry_date:
            try:
                from datetime import datetime
                item.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                # If date format is incorrect, set to None
                item.expiry_date = None
        else:
            item.expiry_date = None
        
        # Handle free/price
        item.is_free = 'is_free' in request.POST
        if item.is_free:
            item.price = None
        else:
            price = request.POST.get('price')
            if price:
                item.price = Decimal(price)
                
        # Handle bidding option
        item.allow_bidding = 'allow_bidding' in request.POST
        
        # Handle main image if new one provided
        if 'main_image' in request.FILES:
            item.image = request.FILES['main_image']
        
        # Save the item
        item.save()
        
        # Handle multiple additional images
        if 'additional_images' in request.FILES:
            for image in request.FILES.getlist('additional_images'):
                MarketplaceItemImage.objects.create(
                    item=item,
                    image=image
                )
                
        # Handle deleting existing additional images
        images_to_delete = request.POST.getlist('delete_images')
        if images_to_delete:
            MarketplaceItemImage.objects.filter(id__in=images_to_delete).delete()
        
        messages.success(request, 'Your marketplace listing has been updated.')
        return redirect('food_donation:marketplace_item_detail', pk=item.pk)
    
    context = {
        'item': item,
        'categories': MarketplaceItem.CATEGORY_CHOICES,
        'current_date': timezone.now().date().isoformat(),
    }
    return render(request, 'food_donation/edit_marketplace_item.html', context)

@login_required
def delete_marketplace_item(request, pk):
    """Delete a marketplace item"""
    item = get_object_or_404(MarketplaceItem, pk=pk)
    
    # Check if the current user is the owner
    if request.user != item.seller:
        messages.error(request, 'You do not have permission to delete this listing.')
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            # Before deleting the item, check if we can delete related images
            try:
                # Get related images
                related_images = MarketplaceItemImage.objects.filter(item=item)
                
                # Delete images one by one
                for image in related_images:
                    # Delete the actual image file
                    if image.image:
                        if os.path.isfile(image.image.path):
                            os.remove(image.image.path)
                    # Delete the database record
                    image.delete()
            except Exception as img_error:
                # Log the error but continue with item deletion
                print(f"Error deleting image: {str(img_error)}")
                
                # Try direct SQL deletion as fallback
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM food_donation_marketplaceitemimage WHERE item_id = ?", [item.id])
                except Exception as sql_error:
                    print(f"SQL Error: {str(sql_error)}")
                    # Continue anyway
            
            # If main image exists, delete the file
            if item.image:
                if os.path.isfile(item.image.path):
                    os.remove(item.image.path)
                
            # Now delete the marketplace item
            item.delete()
            messages.success(request, 'Your marketplace listing has been deleted.')
        except Exception as e:
            messages.error(request, f'Error deleting listing: {str(e)}')
        
        return redirect('food_donation:marketplace')
    
    context = {'item': item}
    return render(request, 'food_donation/delete_marketplace_item.html', context)

@login_required
def update_marketplace_status(request, pk):
    """Update marketplace item status"""
    item = get_object_or_404(MarketplaceItem, pk=pk)
    
    # Check if the current user is the owner
    if request.user != item.seller:
        messages.error(request, 'You do not have permission to update this listing.')
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(MarketplaceItem.STATUS_CHOICES).keys():
            item.status = new_status
            item.save()
            messages.success(request, f'Listing status updated to {dict(MarketplaceItem.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('food_donation:marketplace_item_detail', pk=pk)

@login_required
def my_marketplace_items(request):
    """View all marketplace items for the current user - requires being a lister"""
    # Check if user is a marketplace lister
    try:
        lister = MarketplaceLister.objects.get(user=request.user)
        if not lister.is_approved():
            messages.warning(request, 'Your marketplace lister application is still pending approval.')
    except MarketplaceLister.DoesNotExist:
        messages.error(request, 'You need to be a marketplace lister to view your listings.')
        return redirect('food_donation:apply_marketplace_lister')
    
    items = MarketplaceItem.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter:
        items = items.filter(status=status_filter)
    
    context = {
        'items': items,
        'status_choices': MarketplaceItem.STATUS_CHOICES,
        'current_status': status_filter,
        'lister': lister
    }
    return render(request, 'food_donation/my_marketplace_items.html', context)

# Admin approval view for marketplace listers
@login_required
def admin_marketplace_listers(request):
    """Admin view to manage marketplace lister applications"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('food_donation:home')
    
    listers = MarketplaceLister.objects.all().order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter:
        listers = listers.filter(status=status_filter)
    
    # Get all ID verification images
    id_images = {}
    for lister in listers:
        id_images[lister.id] = IDVerificationImage.objects.filter(lister=lister)
    
    context = {
        'listers': listers,
        'status_choices': MarketplaceLister.STATUS_CHOICES,
        'current_status': status_filter,
        'id_images': id_images,
    }
    return render(request, 'food_donation/admin_marketplace_listers.html', context)

@login_required
def update_marketplace_lister_status(request, pk):
    """Admin action to update marketplace lister status"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('food_donation:home')
    
    if request.method == 'POST':
        lister = get_object_or_404(MarketplaceLister, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(MarketplaceLister.STATUS_CHOICES).keys():
            lister.status = new_status
            
            # If approving, set approved_at timestamp
            if new_status == 'approved':
                lister.approved_at = timezone.now()
            
            lister.save()
            
            # Notify the user (in a real app, you would send an email)
            messages.success(request, f'Marketplace lister status for {lister.user.username} updated to {dict(MarketplaceLister.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status.')
            
    return redirect('food_donation:admin_marketplace_listers')

@login_required
def report_marketplace_item(request, pk):
    item = get_object_or_404(MarketplaceItem, pk=pk)
    
    # Prevent owners from reporting their own listings
    if request.user == item.seller:
        messages.error(request, "You cannot report your own listing.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    if request.method == 'POST':
        report_reason = request.POST.get('report_reason')
        report_details = request.POST.get('report_details', '')
        
        # For now, just send a message to admins (in a real app, you'd save to a model)
        try:
            admin_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            if admin_emails:
                from_email = 'Beyond Hunger <beyoundhunger1@gmail.com>'
                subject = f'Item Reported: {item.title}'
                message = f"""
                An item has been reported:
                
                Item: {item.title} (ID: {item.id})
                Reporter: {request.user.username} (ID: {request.user.id})
                Reason: {report_reason}
                Details: {report_details}
                
                Please review this listing and take appropriate action.
                """
                
                from django.core.mail import send_mail
                send_mail(subject, message, from_email, list(admin_emails))
        except Exception as e:
            print(f"Error sending report email: {str(e)}")
        
        messages.success(request, "Thank you for your report. Our team will review it shortly.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    # If not a POST request, redirect back to the item detail page
    return redirect('food_donation:marketplace_item_detail', pk=pk)

@login_required
def place_bid(request, pk):
    """View to place a bid on a marketplace item"""
    item = get_object_or_404(MarketplaceItem, pk=pk)
    
    # Can't bid on your own items
    if request.user == item.seller:
        messages.error(request, "You cannot bid on your own listing.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    # Can't bid on items that aren't available
    if item.status != 'available':
        messages.error(request, "This item is not available for bidding.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    # Can't bid on free items
    if item.is_free:
        messages.error(request, "Free items don't accept bids. Please use the contact button instead.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    # Check if bidding is allowed for this item
    if not item.allow_bidding:
        messages.error(request, "This item does not accept bids. Please contact the seller directly.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    if request.method == 'POST':
        amount = request.POST.get('bid_amount')
        message = request.POST.get('bid_message', '')
        
        try:
            amount = Decimal(amount)
            
            # Validate bid amount
            if amount <= 0:
                messages.error(request, "Bid amount must be greater than zero.")
                return redirect('food_donation:marketplace_item_detail', pk=pk)
            
            # Check if there's a minimum price
            if item.price and amount < item.price:
                messages.error(request, f"Bid amount must be at least ${item.price}.")
                return redirect('food_donation:marketplace_item_detail', pk=pk)
            
            # Check for existing bid from this user
            existing_bid = MarketplaceBid.objects.filter(item=item, bidder=request.user).first()
            
            if existing_bid:
                # Update existing bid
                existing_bid.amount = amount
                existing_bid.message = message
                existing_bid.is_rejected = False  # Reset rejected status if re-bidding
                existing_bid.save()
                bid = existing_bid
                messages.success(request, "Your bid has been updated.")
            else:
                # Create new bid
                bid = MarketplaceBid.objects.create(
                    item=item,
                    bidder=request.user,
                    amount=amount,
                    message=message
                )
                messages.success(request, "Your bid has been placed successfully.")
            
            # Create notification for the seller
            Notification.objects.create(
                user=item.seller,
                type='bid',
                title=f'New bid on {item.title}',
                message=f'{request.user.username} placed a bid of ${amount} on your listing "{item.title}"',
                related_item=item,
                related_bid=bid
            )
            
            # Notify seller (in a real app, you'd send an email)
            try:
                from_email = 'Beyond Hunger <beyoundhunger1@gmail.com>'
                subject = f'New Bid on Your Listing: {item.title}'
                message_body = f"""
                You have received a new bid:
                
                Item: {item.title}
                Bidder: {request.user.username}
                Amount: ${amount}
                Message: {message}
                
                Log in to your account to view and respond to this bid.
                """
                
                from django.core.mail import send_mail
                send_mail(subject, message_body, from_email, [item.seller.email])
            except Exception as e:
                print(f"Error sending bid notification email: {str(e)}")
                
            return redirect('food_donation:marketplace_item_detail', pk=pk)
            
        except (ValueError, InvalidOperation):
            messages.error(request, "Please enter a valid amount.")
            return redirect('food_donation:marketplace_item_detail', pk=pk)
            
    return redirect('food_donation:marketplace_item_detail', pk=pk)

@login_required
def accept_bid(request, item_pk, bid_pk):
    """View to accept a bid"""
    item = get_object_or_404(MarketplaceItem, pk=item_pk)
    bid = get_object_or_404(MarketplaceBid, pk=bid_pk, item=item)
    
    # Only the seller can accept bids
    if request.user != item.seller:
        messages.error(request, "You don't have permission to accept bids on this item.")
        return redirect('food_donation:marketplace_item_detail', pk=item_pk)
    
    # Can only accept bids on available items
    if item.status != 'available':
        messages.error(request, "This item is no longer available.")
        return redirect('food_donation:marketplace_item_detail', pk=item_pk)
    
    if request.method == 'POST':
        # Accept the bid
        bid.accept_bid()
        
        # Create notification for the bidder
        Notification.objects.create(
            user=bid.bidder,
            type='bid_accepted',
            title=f'Your bid was accepted!',
            message=f'Your bid of ${bid.amount} for "{item.title}" has been accepted by the seller.',
            related_item=item,
            related_bid=bid
        )
        
        # Notify the bidder
        try:
            from_email = 'Beyond Hunger <beyoundhunger1@gmail.com>'
            subject = f'Your Bid on {item.title} Has Been Accepted!'
            message_body = f"""
            Congratulations! Your bid has been accepted:
            
            Item: {item.title}
            Bid Amount: ${bid.amount}
            
            Please contact the seller to arrange pickup/delivery.
            Seller: {item.seller.username}
            Email: {item.seller.email}
            
            Thank you for using our marketplace!
            """
            
            from django.core.mail import send_mail
            send_mail(subject, message_body, from_email, [bid.bidder.email])
        except Exception as e:
            print(f"Error sending bid acceptance email: {str(e)}")
        
        messages.success(request, f"You have accepted the bid from {bid.bidder.username} for ${bid.amount}.")
        return redirect('food_donation:marketplace_item_detail', pk=item_pk)
    
    return redirect('food_donation:marketplace_item_detail', pk=item_pk)

@login_required
@require_POST
def confirm_money_donation(request):
    amount = request.POST.get('amount')
    payment_method = request.POST.get('payment_method', 'other')
    transaction_id = request.POST.get('transaction_id', '')
    
    try:
        amount = float(amount)
        if amount <= 0:
            return JsonResponse({'status': 'error', 'message': 'Amount must be positive'})
            
        # Create the money donation record
        donation = MoneyDonation.objects.create(
            donor=request.user,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id or str(uuid.uuid4())[:10]
        )
        
        # Send confirmation email
        send_money_donation_confirmation(request.user, donation)
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Thank you for your donation! A confirmation email has been sent.'
        })
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid amount'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

def chatbot(request):
    """View for the chatbot interface"""
    return render(request, 'food_donation/chatbot.html')

@login_required
def admin_contact_messages(request):
    """Admin view to manage contact messages"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('food_donation:home')
    
    # Get all contact messages
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter:
        contact_messages = contact_messages.filter(status=status_filter)
    
    context = {
        'contact_messages': contact_messages,
        'status_choices': ContactMessage.STATUS_CHOICES,
        'current_status': status_filter,
    }
    
    return render(request, 'food_donation/admin_contact_messages.html', context)

@login_required
def update_contact_message_status(request, pk):
    """Admin action to update contact message status"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('food_donation:home')
    
    if request.method == 'POST':
        contact_message = get_object_or_404(ContactMessage, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(ContactMessage.STATUS_CHOICES).keys():
            contact_message.status = new_status
            contact_message.save()
            
            messages.success(request, f'Message status updated to {dict(ContactMessage.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status.')
            
    return redirect('food_donation:admin_contact_messages')

@login_required
def complete_profile(request):
    """View for completing user profile after social login"""
    # If user doesn't need profile completion, redirect to home
    if not request.session.get('needs_profile_completion', False):
        return redirect('food_donation:home')
    
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': ''
        }
    )
    
    # Check if user has Google account with profile picture
    google_picture_url = None
    try:
        social_account = request.user.socialaccount_set.filter(provider='google').first()
        if social_account and 'picture' in social_account.extra_data:
            google_picture_url = social_account.extra_data['picture']
    except:
        pass
    
    if request.method == 'POST':
        # Update user profile with submitted data
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        use_google_photo = request.POST.get('use_google_photo') == 'on'
        
        if phone and address:
            user_profile.phone = phone
            user_profile.address = address
            
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                user_profile.profile_photo = request.FILES['profile_photo']
            elif use_google_photo and google_picture_url:
                # No need to download, we'll use the URL directly via the get_profile_photo_url method
                pass
            
            user_profile.save()
            
            # Clear the flag from session
            if 'needs_profile_completion' in request.session:
                del request.session['needs_profile_completion']
            
            messages.success(request, 'Thank you for completing your profile!')
            return redirect('food_donation:profile')
        else:
            messages.error(request, 'Please provide both phone number and address.')
    
    return render(request, 'food_donation/complete_profile.html', {
        'user_profile': user_profile,
        'google_picture_url': google_picture_url
    })

@login_required
def download_donation_receipt(request, donation_id):
    """Generate and download a PDF receipt for a food donation"""
    # If user is admin, allow downloading any donation receipt
    if request.user.is_superuser:
        donation = get_object_or_404(FoodDonation, id=donation_id)
    else:
        # Otherwise, only allow user to download their own donation receipts
        donation = get_object_or_404(FoodDonation, id=donation_id, donor=request.user)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object using ReportLab
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add the receipt header
    elements.append(Paragraph("Beyond Hunger - Donation Receipt", styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Add receipt details
    elements.append(Paragraph(f"Receipt #: {donation.id}", styles['Heading2']))
    elements.append(Paragraph(f"Date: {donation.created_at.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Add donor information
    elements.append(Paragraph("Donor Information:", styles['Heading3']))
    elements.append(Paragraph(f"Name: {donation.donor.get_full_name() or donation.donor.username}", styles['Normal']))
    try:
        profile = donation.donor.userprofile
        elements.append(Paragraph(f"Phone: {profile.phone}", styles['Normal']))
        elements.append(Paragraph(f"Address: {profile.address}", styles['Normal']))
    except:
        pass
    elements.append(Spacer(1, 20))
    
    # Add donation details
    elements.append(Paragraph("Donation Details:", styles['Heading3']))
    
    data = [
        ['Food Type', 'Quantity', 'Expiry Date', 'Status'],
        [donation.food_type, donation.quantity, donation.expiry_date.strftime('%B %d, %Y'), donation.get_status_display()]
    ]
    
    # If there's payment info, add it
    if donation.amount:
        elements.append(Paragraph(f"Amount: ${donation.amount}", styles['Normal']))
        elements.append(Paragraph(f"Payment Method: {donation.get_payment_method_display()}", styles['Normal']))
        elements.append(Paragraph(f"Transaction ID: {donation.transaction_id}", styles['Normal']))
    
    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Add pick-up information
    elements.append(Paragraph("Pick-up Information:", styles['Heading3']))
    elements.append(Paragraph(f"Address: {donation.pickup_address}", styles['Normal']))
    elements.append(Paragraph(f"Date: {donation.pickup_date.strftime('%B %d, %Y')}", styles['Normal']))
    
    if donation.notes:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Notes:", styles['Heading3']))
        elements.append(Paragraph(donation.notes, styles['Normal']))
    
    # Add thank you message
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for your generous donation to Beyond Hunger!", styles['Heading3']))
    elements.append(Paragraph("Your contribution helps us fight hunger in our community.", styles['Normal']))
    
    # Build the PDF
    pdf.build(elements)
    
    # Get the value of the buffer
    pdf_value = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(pdf_value, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="donation_receipt_{donation.id}.pdf"'
    
    return response

@login_required
def update_profile_photo(request):
    """View for updating user profile photo with validation"""
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        profile = request.user.userprofile
        
        # Get the uploaded file
        photo = request.FILES['profile_photo']
        
        # Validate file size (max 5MB)
        if photo.size > 5 * 1024 * 1024:
            messages.error(request, "Profile photo must be less than 5MB")
            return redirect('food_donation:profile')
        
        # Validate file type
        if not photo.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            messages.error(request, "Profile photo must be a JPG or PNG image")
            return redirect('food_donation:profile')
        
        try:
            # Additional validation for proper profile photo
            # Open the image
            img = Image.open(photo)
            
            # Check dimensions - profile photos should be reasonably square
            width, height = img.size
            aspect_ratio = width / height
            
            if aspect_ratio < 0.7 or aspect_ratio > 1.5:
                messages.error(request, "Photo must be reasonably square (like a portrait). Please crop your image appropriately.")
                return redirect('food_donation:profile')
            
            # Check minimum size
            if width < 200 or height < 200:
                messages.error(request, "Profile photo must be at least 200x200 pixels")
                return redirect('food_donation:profile')
            
            # Optional: Use face detection if you have additional libraries
            # This is a simple message - proper face detection would require
            # libraries like opencv-python or face_recognition
            messages.info(request, "Please ensure your photo shows your face clearly for identification purposes.")
            
            # Save the profile photo
            profile.profile_photo = photo
            profile.save()
            
            messages.success(request, "Profile photo updated successfully")
        except Exception as e:
            messages.error(request, f"Error processing image: {str(e)}")
        
        return redirect('food_donation:profile')
    
    return redirect('food_donation:profile')

@login_required
def notifications(request):
    """View for user to see their notifications"""
    # Get all notifications for the user
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read
    user_notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': user_notifications,
    }
    
    return render(request, 'food_donation/notifications.html', context)

@login_required
def delete_conversation(request, item_pk, user_pk):
    """Delete an entire conversation about an item with a specific user"""
    if request.method == 'POST':
        item = get_object_or_404(MarketplaceItem, pk=item_pk)
        other_user = get_object_or_404(User, pk=user_pk)
        
        # Delete messages where current user is sender or receiver
        MarketplaceChat.objects.filter(
            item=item,
            sender=request.user,
            receiver=other_user
        ).delete()
        
        MarketplaceChat.objects.filter(
            item=item,
            sender=other_user,
            receiver=request.user
        ).delete()
        
        messages.success(request, 'Conversation deleted successfully.')
    
    return redirect('food_donation:view_messages')

@login_required
def delete_message(request, message_id):
    """Delete a specific message"""
    if request.method == 'POST':
        message = get_object_or_404(MarketplaceChat, pk=message_id)
        
        # Only allow users to delete messages they sent
        if message.sender == request.user:
            item_pk = message.item.pk
            user_pk = message.receiver.pk if message.receiver != request.user else message.sender.pk
            
            message.delete()
            messages.success(request, 'Message deleted successfully.')
            
            # Return to the conversation
            return redirect('food_donation:view_conversation', item_pk=item_pk, user_pk=user_pk)
        else:
            messages.error(request, 'You can only delete messages you sent.')
    
    return redirect('food_donation:view_messages')

@login_required
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.delete()
        messages.success(request, 'Notification deleted successfully.')
    
    return redirect('food_donation:notifications')

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.type == 'message' and notification.related_chat:
        # Redirect to the conversation if it's a message notification
        return redirect('food_donation:view_conversation', 
                         item_pk=notification.related_chat.item.pk,
                         user_pk=notification.related_chat.sender.pk)
    
    return redirect('food_donation:notifications')

@login_required
def send_message(request, item_pk):
    """Send a message to the seller or bidder of a marketplace item"""
    item = get_object_or_404(MarketplaceItem, pk=item_pk)
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver_id = request.POST.get('receiver')
        include_phone = 'include_phone' in request.POST
        
        if not message_text:
            messages.error(request, 'Message cannot be empty.')
            return redirect('food_donation:marketplace_item_detail', pk=item_pk)
        
        try:
            receiver = User.objects.get(id=receiver_id)
            
            # Handle file upload if present
            media_file = None
            if 'message_media' in request.FILES:
                media_file = request.FILES['message_media']
            
            # Create the message
            chat = MarketplaceChat.objects.create(
                item=item,
                sender=request.user,
                receiver=receiver,
                message=message_text,
                include_phone=include_phone,
                media_file=media_file
            )
            
            # Create notification for receiver
            notification = Notification.objects.create(
                user=receiver,
                type='message',
                title=f'New message about {item.title}',
                message=f'{request.user.username} sent you a message about your listing "{item.title}"',
                related_item=item,
                related_chat=chat
            )
            
            # Send email notification if user has email
            if receiver.email:
                try:
                    from django.core.mail import send_mail
                    
                    # Get the sender's phone if they chose to include it
                    sender_phone = ''
                    if include_phone:
                        try:
                            profile = UserProfile.objects.get(user=request.user)
                            sender_phone = fr"\nPhone: {profile.phone}"
                        except:
                            pass
                    
                    # Note if the message includes media
                    media_note = ''
                    if media_file:
                        media_note = "\n* This message includes media attachment."
                    
                    subject = f'New message about {item.title}'
                    from_email = 'Beyond Hunger <beyoundhunger1@gmail.com>'
                    message_body = f"""
                    You have received a new message:
                    
                    Item: {item.title}
                    From: {request.user.username}
                    Message: {message_text}
                    {sender_phone}
                    {media_note}
                    
                    Log in to your account to view and respond to this message.
                    """
                    
                    send_mail(subject, message_body, from_email, [receiver.email])
                except Exception as e:
                    print(f"Error sending message notification email: {str(e)}")
            
            messages.success(request, 'Your message has been sent.')
            
            # If the user sent the message from the conversation view, redirect back there
            referrer = request.META.get('HTTP_REFERER', '')
            if 'messages/' in referrer and str(item_pk) in referrer:
                return redirect('food_donation:view_conversation', item_pk=item_pk, user_pk=receiver.id)
                
        except User.DoesNotExist:
            messages.error(request, 'Recipient not found.')
        
        return redirect('food_donation:marketplace_item_detail', pk=item_pk)
    
    return redirect('food_donation:marketplace_item_detail', pk=item_pk)

@login_required
def view_messages(request):
    """View for user to see their marketplace messages"""
    # Get received messages
    received_messages = MarketplaceChat.objects.filter(receiver=request.user).order_by('-created_at')
    
    # Get sent messages
    sent_messages = MarketplaceChat.objects.filter(sender=request.user).order_by('-created_at')
    
    # Create conversation groups
    conversations = {}
    
    # Process received messages
    for msg in received_messages:
        key = f"{msg.item.id}_{msg.sender.id}"
        if key not in conversations:
            conversations[key] = {
                'item': msg.item,
                'other_user': msg.sender,
                'messages': [],
                'latest_message_date': msg.created_at
            }
        conversations[key]['messages'].append(msg)
        if msg.created_at > conversations[key]['latest_message_date']:
            conversations[key]['latest_message_date'] = msg.created_at
    
    # Process sent messages
    for msg in sent_messages:
        key = f"{msg.item.id}_{msg.receiver.id}"
        if key not in conversations:
            conversations[key] = {
                'item': msg.item,
                'other_user': msg.receiver,
                'messages': [],
                'latest_message_date': msg.created_at
            }
        conversations[key]['messages'].append(msg)
        if msg.created_at > conversations[key]['latest_message_date']:
            conversations[key]['latest_message_date'] = msg.created_at
    
    # Sort conversations by latest message date
    sorted_conversations = sorted(
        conversations.values(),
        key=lambda x: x['latest_message_date'],
        reverse=True
    )
    
    # Mark messages as read
    received_messages.filter(is_read=False).update(is_read=True)
    
    # Also mark related notifications as read
    Notification.objects.filter(
        user=request.user,
        type='message',
        is_read=False,
        related_chat__in=received_messages
    ).update(is_read=True)
    
    context = {
        'conversations': sorted_conversations,
    }
    
    return render(request, 'food_donation/marketplace_messages.html', context)

@login_required
def view_conversation(request, item_pk, user_pk):
    """View a specific conversation with a user about an item"""
    item = get_object_or_404(MarketplaceItem, pk=item_pk)
    other_user = get_object_or_404(User, pk=user_pk)
    
    # Get all messages between the current user and the other user about this item
    messages_received = MarketplaceChat.objects.filter(
        item=item,
        sender=other_user,
        receiver=request.user
    ).order_by('created_at')
    
    messages_sent = MarketplaceChat.objects.filter(
        item=item,
        sender=request.user,
        receiver=other_user
    ).order_by('created_at')
    
    # Combine and sort by creation date
    all_messages = sorted(
        list(messages_received) + list(messages_sent),
        key=lambda x: x.created_at
    )
    
    # Mark received messages as read
    messages_received.filter(is_read=False).update(is_read=True)
    
    # Also mark related notifications as read
    Notification.objects.filter(
        user=request.user,
        type='message',
        is_read=False,
        related_chat__in=messages_received
    ).update(is_read=True)
    
    # Check if user is seller or potential buyer
    is_seller = (request.user == item.seller)
    
    # Get other user's profile for contact info
    try:
        other_profile = UserProfile.objects.get(user=other_user)
    except UserProfile.DoesNotExist:
        other_profile = None
    
    context = {
        'item': item,
        'other_user': other_user,
        'other_profile': other_profile,
        'messages': all_messages,
        'is_seller': is_seller,
    }
    
    return render(request, 'food_donation/marketplace_conversation.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_send_notification(request):
    """Admin view to send a notification to users"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        specific_user_id = request.POST.get('specific_user')
        
        if not title or not message:
            messages.error(request, 'Title and message are required.')
            return redirect('food_donation:admin_send_notification')
        
        # Determine recipients
        if recipient_type == 'all':
            recipients = User.objects.all()
        elif recipient_type == 'donors':
            recipients = User.objects.filter(userprofile__is_donor=True)
        elif recipient_type == 'volunteers':
            recipients = User.objects.filter(userprofile__is_volunteer=True)
        elif recipient_type == 'marketplace':
            recipients = MarketplaceLister.objects.filter(status='approved').values_list('user', flat=True)
            recipients = User.objects.filter(id__in=recipients)
        elif recipient_type == 'specific' and specific_user_id:
            try:
                recipients = [User.objects.get(id=specific_user_id)]
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                recipients = []
        else:
            messages.error(request, 'Invalid recipient type.')
            return redirect('food_donation:admin_send_notification')
        
        # Create notifications for all recipients
        for user in recipients:
            Notification.objects.create(
                user=user,
                type='admin',
                title=title,
                message=message
            )
        
        messages.success(request, f'Notification sent to {len(recipients)} users.')
        return redirect('food_donation:admin_dashboard')
    
    # Get all users for the dropdown
    users = User.objects.all().order_by('username')
    
    context = {
        'users': users
    }
    
    return render(request, 'food_donation/admin_send_notification.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def download_delivered_donations_csv(request):
    """Generate and download a CSV file with all delivered donations for admin users"""
    # Ensure it's a superuser
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this feature.")
        return redirect('food_donation:admin_dashboard')
    
    # Get all delivered donations
    delivered_donations = FoodDonation.objects.filter(status='delivered')
    
    # Create a response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="delivered_donations.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Donation ID', 
        'Donor', 
        'Email',
        'Phone',
        'Food Type', 
        'Quantity', 
        'Expiry Date',
        'Pickup Address',
        'Pickup Date', 
        'Status',
        'Payment Method',
        'Amount',
        'Transaction ID',
        'Payment Status',
        'Creation Date',
        'Notes'
    ])
    
    # Write data rows
    for donation in delivered_donations:
        try:
            profile = donation.donor.userprofile
            phone = profile.phone
        except:
            phone = "Not available"
            
        writer.writerow([
            donation.id,
            donation.donor.get_full_name() or donation.donor.username,
            donation.donor.email,
            phone,
            donation.food_type,
            donation.quantity,
            donation.expiry_date.strftime('%Y-%m-%d'),
            donation.pickup_address,
            donation.pickup_date.strftime('%Y-%m-%d'),
            donation.get_status_display(),
            donation.get_payment_method_display() if donation.payment_method else 'None',
            donation.amount if donation.amount else 'None',
            donation.transaction_id if donation.transaction_id else 'None',
            donation.get_payment_status_display(),
            donation.created_at.strftime('%Y-%m-%d %H:%M'),
            donation.notes
        ])
    
    return response

@login_required
def money_donation_history(request):
    """View for user to see their money donation history"""
    # Get all money donations for the current user
    user_donations = MoneyDonation.objects.filter(donor=request.user).order_by('-created_at')
    
    context = {
        'money_donations': user_donations,
        'total_amount': sum(donation.amount for donation in user_donations)
    }
    
    return render(request, 'food_donation/money_donation_history.html', context)

def donate_money(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '')
        
        if amount and payment_method:
            try:
                amount = float(amount)
                donation = MoneyDonation.objects.create(
                    donor=request.user,
                    amount=amount,
                    payment_method=payment_method,
                    transaction_id=transaction_id
                )
                
                # Send confirmation email
                if request.user.email:
                    send_money_donation_confirmation(request.user, donation)
                
                messages.success(request, 'Thank you for your donation! We have sent a confirmation to your email.')
                return redirect('profile')
            except ValueError:
                messages.error(request, 'Please enter a valid amount.')
        else:
            messages.error(request, 'Please provide both amount and payment method.')
            
    return redirect('profile')
