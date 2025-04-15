from django.urls import path
from . import api

app_name = 'food_donation_api'

urlpatterns = [
    # Statistics API
    path('statistics/', api.get_statistics, name='statistics'),
    
    # Food Donation APIs
    path('donations/', api.list_donations, name='list_donations'),
    path('donations/<int:pk>/update-status/', api.update_donation_status, name='update_donation_status'),
    path('donations/<int:pk>/discard/', api.discard_donation, name='discard_donation'),
    
    # Delivery Assignment APIs
    path('assignments/', api.list_assignments, name='list_assignments'),
    path('assignments/<int:pk>/update-status/', api.update_assignment_status, name='update_assignment_status'),
    path('assignments/<int:pk>/discard/', api.discard_assignment, name='discard_assignment'),
    path('assign-delivery/', api.assign_delivery, name='assign_delivery'),
    
    # Volunteer APIs
    path('volunteers/', api.list_volunteers, name='list_volunteers'),
    
    # User APIs
    path('users/', api.list_users, name='list_users'),
    path('login/', api.login_api, name='login'),
    
    # Chatbot API
    path('chatbot/', api.chatbot_api, name='chatbot'),
    
    # Bhandara API
    path('bhandara/<int:pk>/', api.bhandara_detail_api, name='bhandara_detail'),
] 