from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import (
    UserProfile, FoodDonation, Volunteer, DeliveryAssignment, 
    MarketplaceLister, MarketplaceItem, MarketplaceItemImage, 
    FoodDonationImage, IDVerificationImage, MoneyDonation
)
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q
from django.core.paginator import Paginator
import os
from django.db import connection
from django.core.mail import EmailMultiAlternatives

def home(request):
    context = {
        'total_donations': FoodDonation.objects.count(),
        'total_volunteers': Volunteer.objects.count(),
        'total_requests': FoodDonation.objects.filter(status='delivered').count(),  # Changed to show delivered donations
        'recent_donations': FoodDonation.objects.order_by('-created_at')[:5],
    }
    return render(request, 'food_donation/home.html', context)

def money_donate(request):
    return render(request, 'food_donation/money_donate.html')

@login_required
def donate(request):
    # Get current date for minimum date fields
    current_date = timezone.now().date().isoformat()
    
    # Pre-populate data from user profile
    user_profile = request.user.userprofile
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
            import uuid
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
        
        messages.success(request, 'Thank you for your donation!')
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
        # Handle contact form submission
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
    user_profile = request.user.userprofile
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
    
    items = MarketplaceItem.objects.filter(status='available').order_by('-created_at')
    
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
    
    context = {
        'item': item,
        'is_owner': is_owner,
        'additional_images': additional_images,
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
        user_profile = request.user.userprofile
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
        
        # Create item
        item = MarketplaceItem(
            seller=request.user,
            title=title,
            description=description,
            category=category,
            quantity=quantity,
            location=location,
            is_free=is_free,
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
        
        # Create a new model instance for the report
        report = MarketplaceReport.objects.create(
            reporter=request.user,
            item=item,
            reason=report_reason,
            details=report_details
        )
        
        # Optional: Send notification to admins about the new report
        
        messages.success(request, "Thank you for your report. Our team will review it shortly.")
        return redirect('food_donation:marketplace_item_detail', pk=pk)
    
    # If not a POST request, redirect back to the item detail page
    return redirect('food_donation:marketplace_item_detail', pk=pk)

@login_required
def confirm_money_donation(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            money_donation = MoneyDonation.objects.create(
                donor=request.user,
                amount=float(amount),
                is_acknowledged=True
            )
            # Send email confirmation if email is configured
            try:
                send_money_donation_confirmation(request.user, money_donation)
            except:
                pass  # Handle silently if email sending fails
            messages.success(request, "Thank you for your donation! It has been recorded.")
        return redirect('food_donation:profile')
    return redirect('food_donation:money_donate')

def send_money_donation_confirmation(user, donation):
    subject = 'Thank you for your monetary donation'
    from_email = 'Beyond Hunger <beyoundhunger1@gmail.com>'
    to = user.email
    
    # Prepare HTML message
    html_content = f"""
    <html>
    <head>
        <title>Donation Confirmation</title>
    </head>
    <body>
        <h1>Thank you for your donation!</h1>
        <p>Dear {user.first_name or user.username},</p>
        <p>We have received your monetary donation of ${donation.amount}.</p>
        <p>Your contribution will help us fight hunger in our community.</p>
        <p>Thank you for supporting Beyond Hunger!</p>
    </body>
    </html>
    """
    text_content = f"Thank you for your donation of ${donation.amount}. Your contribution will help us fight hunger in our community."
    
    # Create email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to])
    email.attach_alternative(html_content, "text/html")
    email.send()
    return True
