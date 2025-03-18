from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, FoodDonation, Volunteer, DeliveryAssignment
from django.utils import timezone
from decimal import Decimal

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
        
        donation.save()
        messages.success(request, 'Thank you for your donation!')
        return redirect('profile')
    return render(request, 'food_donation/donate.html')

def about(request):
    return render(request, 'food_donation/about.html')

def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        messages.success(request, 'Thank you for your message. We will get back to you soon.')
        return redirect('contact')
    return render(request, 'food_donation/contact.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
            
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
            
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('profile')
    return render(request, 'food_donation/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'food_donation/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile(request):
    user_profile = request.user.userprofile
    context = {
        'profile': user_profile,
        'donations': FoodDonation.objects.filter(donor=request.user).order_by('-created_at'),
    }
    if user_profile.is_volunteer:
        volunteer = Volunteer.objects.get(user=request.user)
        context['volunteer'] = volunteer
        context['assignments'] = DeliveryAssignment.objects.filter(volunteer=volunteer).order_by('-created_at')
    return render(request, 'food_donation/profile.html', context)

@login_required
def custom_admin_dashboard(request):
    # Check if user is a superuser (admin)
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('home')
    
    # Get all model data for display
    users = User.objects.all().order_by('-date_joined')
    user_profiles = UserProfile.objects.all().order_by('-created_at')
    donations = FoodDonation.objects.all().order_by('-created_at')
    volunteers = Volunteer.objects.all().order_by('-created_at')
    assignments = DeliveryAssignment.objects.all().order_by('-created_at')
    
    # Statistics for dashboard
    stats = {
        'total_users': users.count(),
        'total_donors': UserProfile.objects.filter(is_donor=True).count(),
        'total_volunteers': UserProfile.objects.filter(is_volunteer=True).count(),
        'total_donations': donations.count(),
        'pending_donations': donations.filter(status='pending').count(),
        'completed_donations': donations.filter(status='delivered').count(),
        'cancelled_donations': donations.filter(status='cancelled').count(),
        'active_assignments': assignments.filter(status__in=['assigned', 'picked_up']).count(),
    }
    
    context = {
        'stats': stats,
        'users': users,
        'user_profiles': user_profiles,
        'donations': donations,
        'volunteers': volunteers,
        'assignments': assignments,
        'donation_status_choices': FoodDonation.STATUS_CHOICES,
        'assignment_status_choices': DeliveryAssignment.STATUS_CHOICES,
    }
    
    return render(request, 'food_donation/admin_dashboard.html', context)

@login_required
def update_donation_status(request, donation_id):
    # Check if user is a superuser (admin)
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to update donation status.')
        return redirect('home')
    
    if request.method == 'POST':
        donation = FoodDonation.objects.get(id=donation_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(FoodDonation.STATUS_CHOICES).keys():
            donation.status = new_status
            donation.save()
            messages.success(request, f'Donation status updated to {dict(FoodDonation.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Invalid status.')
            
    return redirect('admin_dashboard')

@login_required
def update_assignment_status(request, assignment_id):
    # Check if user is a superuser (admin)
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to update assignment status.')
        return redirect('home')
    
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
            
    return redirect('admin_dashboard')
