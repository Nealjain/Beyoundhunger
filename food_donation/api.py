from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import FoodDonation, DeliveryAssignment, Volunteer, UserProfile, ChatbotResponse
from django.db.models import Count, Sum
from django.utils import timezone
import json

# Serializers for our models
from rest_framework import serializers

# Import OpenAI library
import openai
from django.conf import settings
from django.http import JsonResponse

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'address', 'is_donor', 'is_volunteer', 'created_at']

class VolunteerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Volunteer
        fields = ['id', 'user', 'availability', 'vehicle_type', 'service_area', 'created_at']

class FoodDonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FoodDonation
        fields = ['id', 'donor', 'donor_name', 'food_type', 'quantity', 'expiry_date', 
                  'pickup_address', 'pickup_date', 'status', 'created_at', 'additional_notes']
    
    def get_donor_name(self, obj):
        return f"{obj.donor.first_name} {obj.donor.last_name}" if obj.donor.first_name and obj.donor.last_name else obj.donor.username

class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    donation = FoodDonationSerializer()
    volunteer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'donation', 'volunteer', 'volunteer_name', 'status', 'pickup_time', 
                  'delivery_time', 'created_at', 'notes']
    
    def get_volunteer_name(self, obj):
        return f"{obj.volunteer.user.first_name} {obj.volunteer.user.last_name}" if obj.volunteer.user.first_name and obj.volunteer.user.last_name else obj.volunteer.user.username

# API Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_statistics(request):
    """Get statistics for dashboard"""
    # Donation statistics
    total_donations = FoodDonation.objects.count()
    pending_donations = FoodDonation.objects.filter(status='pending').count()
    accepted_donations = FoodDonation.objects.filter(status='accepted').count()
    completed_donations = FoodDonation.objects.filter(status='delivered').count()
    cancelled_donations = FoodDonation.objects.filter(status='cancelled').count()
    
    # Volunteer statistics
    total_volunteers = Volunteer.objects.count()
    active_volunteers = Volunteer.objects.filter(availability=True).count()
    
    # Delivery statistics
    total_deliveries = DeliveryAssignment.objects.count()
    assigned_deliveries = DeliveryAssignment.objects.filter(status='assigned').count()
    picked_up_deliveries = DeliveryAssignment.objects.filter(status='picked_up').count()
    completed_deliveries = DeliveryAssignment.objects.filter(status='delivered').count()
    
    return Response({
        'donations': {
            'total': total_donations,
            'pending': pending_donations,
            'accepted': accepted_donations,
            'completed': completed_donations,
            'cancelled': cancelled_donations
        },
        'volunteers': {
            'total': total_volunteers,
            'active': active_volunteers
        },
        'deliveries': {
            'total': total_deliveries,
            'assigned': assigned_deliveries,
            'picked_up': picked_up_deliveries,
            'completed': completed_deliveries
        }
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_donations(request):
    """Get all donations"""
    donations = FoodDonation.objects.all().order_by('-created_at')
    serializer = FoodDonationSerializer(donations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_donation_status(request, pk):
    """Update the status of a donation"""
    try:
        donation = FoodDonation.objects.get(pk=pk)
        new_status = request.data.get('status')
        
        if new_status and new_status in ['pending', 'accepted', 'delivered', 'cancelled']:
            donation.status = new_status
            donation.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    except FoodDonation.DoesNotExist:
        return Response({'error': 'Donation not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_assignments(request):
    """Get all delivery assignments"""
    assignments = DeliveryAssignment.objects.all().order_by('-created_at')
    serializer = DeliveryAssignmentSerializer(assignments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_assignment_status(request, pk):
    """Update the status of a delivery assignment"""
    try:
        assignment = DeliveryAssignment.objects.get(pk=pk)
        new_status = request.data.get('status')
        
        if new_status and new_status in ['assigned', 'picked_up', 'delivered', 'cancelled']:
            assignment.status = new_status
            
            if new_status == 'picked_up':
                assignment.pickup_time = timezone.now()
            elif new_status == 'delivered':
                assignment.delivery_time = timezone.now()
                # Also update the donation status
                assignment.donation.status = 'delivered'
                assignment.donation.save()
            
            assignment.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    except DeliveryAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_volunteers(request):
    """Get all volunteers"""
    volunteers = Volunteer.objects.all().order_by('-created_at')
    serializer = VolunteerSerializer(volunteers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_delivery(request):
    """Assign a delivery to a volunteer"""
    try:
        donation_id = request.data.get('donation_id')
        volunteer_id = request.data.get('volunteer_id')
        pickup_time = request.data.get('pickup_time')
        notes = request.data.get('notes')
        manual_name = request.data.get('manual_name')
        manual_phone = request.data.get('manual_phone')
        
        donation = FoodDonation.objects.get(pk=donation_id)
        
        # Check if there's an existing assignment
        existing_assignment = DeliveryAssignment.objects.filter(donation=donation).first()
        
        if manual_name:
            # Manual delivery partner assignment
            volunteer = Volunteer.objects.first()
            if not volunteer:
                # Create a system user/volunteer if none exists
                from django.contrib.auth.models import User
                
                system_user, created = User.objects.get_or_create(
                    username='system',
                    defaults={
                        'first_name': 'System',
                        'last_name': 'Account',
                        'email': 'system@example.com',
                        'is_active': True
                    }
                )
                
                volunteer, created = Volunteer.objects.get_or_create(
                    user=system_user,
                    defaults={
                        'availability': False,
                        'vehicle_type': 'System',
                        'service_area': 'System'
                    }
                )
                
                if created:
                    UserProfile.objects.get_or_create(
                        user=system_user,
                        defaults={
                            'phone': '0000000000',
                            'address': 'System Account',
                            'is_volunteer': True
                        }
                    )
            
            full_notes = f"Manual delivery partner: {manual_name}"
            if manual_phone:
                full_notes += f", Phone: {manual_phone}"
            if notes:
                full_notes += f"\nNotes: {notes}"
                
            if existing_assignment:
                existing_assignment.notes = full_notes
                existing_assignment.pickup_time = pickup_time
                existing_assignment.status = 'assigned'
                existing_assignment.save()
            else:
                DeliveryAssignment.objects.create(
                    donation=donation,
                    volunteer=volunteer,
                    status='assigned',
                    pickup_time=pickup_time,
                    notes=full_notes
                )
        else:
            # Database volunteer assignment
            volunteer = Volunteer.objects.get(pk=volunteer_id)
            
            if existing_assignment:
                existing_assignment.volunteer = volunteer
                existing_assignment.pickup_time = pickup_time
                existing_assignment.notes = notes
                existing_assignment.status = 'assigned'
                existing_assignment.save()
            else:
                DeliveryAssignment.objects.create(
                    donation=donation,
                    volunteer=volunteer,
                    status='assigned',
                    pickup_time=pickup_time,
                    notes=notes
                )
        
        # Update donation status to "accepted" if it's "pending"
        if donation.status == 'pending':
            donation.status = 'accepted'
            donation.save()
            
        return Response({'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def discard_donation(request, pk):
    """Discard a donation"""
    try:
        donation = FoodDonation.objects.get(pk=pk)
        
        # Update the donation status to cancelled
        donation.status = 'cancelled'
        donation.save()
        
        # Also cancel any associated delivery assignments
        assignments = DeliveryAssignment.objects.filter(donation=donation)
        for assignment in assignments:
            assignment.status = 'cancelled'
            assignment.save()
            
        return Response({'success': True}, status=status.HTTP_200_OK)
    except FoodDonation.DoesNotExist:
        return Response({'error': 'Donation not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def discard_assignment(request, pk):
    """Discard a delivery assignment"""
    try:
        assignment = DeliveryAssignment.objects.get(pk=pk)
        
        # Update the assignment status to cancelled
        assignment.status = 'cancelled'
        assignment.save()
            
        return Response({'success': True}, status=status.HTTP_200_OK)
    except DeliveryAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_users(request):
    """Get all user profiles"""
    user_profiles = UserProfile.objects.all().order_by('-created_at')
    serializer = UserProfileSerializer(user_profiles, many=True)
    return Response(serializer.data)

# API for authentication
@api_view(['POST'])
def login_api(request):
    """API endpoint for logging in and getting a token"""
    from django.contrib.auth import authenticate
    from rest_framework.authtoken.models import Token
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Improved chatbot API endpoint that doesn't depend on OpenAI
@api_view(['POST'])
def chatbot_api(request):
    """API endpoint for getting a response from the local chatbot database"""
    try:
        # Get message from request
        message = request.data.get('message', '')
        if not message or message.strip() == '':
            # Return default greeting if message is empty
            greeting_response = ChatbotResponse.objects.filter(
                category='greeting', 
                is_active=True
            ).order_by('-priority', '?').first()
            
            if greeting_response:
                return JsonResponse({'response': greeting_response.response})
            return JsonResponse({'response': "Hello! I'm Mr.Jain. How can I help you today?"})
        
        # Clean the message for better matching
        import re
        message = message.lower().strip()
        message = re.sub(r'[^\w\s]', '', message)  # Remove punctuation
        
        # Get all active chatbot responses
        all_responses = ChatbotResponse.objects.filter(is_active=True)
        
        # Initialize variables to track the best match
        best_match = None
        best_match_score = 0
        best_match_priority = -1
        
        # Check each response for keyword matches
        for response in all_responses:
            keywords = [k.strip().lower() for k in response.keywords.split(',')]
            
            # Calculate match score based on keywords presence
            score = 0
            for keyword in keywords:
                if keyword and keyword in message:
                    score += 1
            
            # Check if this is a better match
            if score > 0:
                if (score > best_match_score) or (score == best_match_score and response.priority > best_match_priority):
                    best_match = response
                    best_match_score = score
                    best_match_priority = response.priority
        
        # If we found a match, return it
        if best_match:
            # Personalize the response if user is authenticated
            personalized_response = best_match.response
            if request.user.is_authenticated and '{user}' in personalized_response:
                name = request.user.first_name or request.user.username
                personalized_response = personalized_response.replace('{user}', name)
            
            # Save the interaction if user is authenticated
            if request.user.is_authenticated:
                from .models import ChatbotMessage
                ChatbotMessage.objects.create(
                    user=request.user,
                    message=message,
                    response=personalized_response,
                    is_user_message=True
                )
            
            return JsonResponse({'response': personalized_response})
        
        # If no match found, return a fallback response
        fallback = ChatbotResponse.objects.filter(
            category='fallback',
            is_active=True
        ).order_by('-priority', '?').first()
        
        if fallback:
            return JsonResponse({'response': fallback.response})
        
        # Default fallback if no fallbacks defined in the database
        return JsonResponse({
            'response': "I'm sorry, I don't have specific information about that. Can I help you with food donations, volunteering, or our marketplace instead?"
        })
    
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Chatbot error: {str(e)}")
        
        # Always return a friendly response even if errors occur
        return JsonResponse({
            'response': "I'm sorry, I'm having technical difficulties. Please try asking about donations, volunteering, or using our marketplace."
        }) 