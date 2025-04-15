from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import api
from . import views_debug
from . import bhandara_views  # Import the new bhandara_views module

app_name = 'food_donation'

urlpatterns = [
    path('', views.home, name='home'),
    path('donate/', views.donate, name='donate'),
    path('money-donate/', views.money_donate, name='money_donate'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update-photo/', views.update_profile_photo, name='update_profile_photo'),
    
    # Custom admin dashboard URLs
    path('admin-dashboard/', views.custom_admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/donation/<int:donation_id>/update/', views.update_donation_status, name='update_donation_status'),
    path('admin-dashboard/assignment/<int:assignment_id>/update/', views.update_assignment_status, name='update_assignment_status'),
    path('admin-dashboard/marketplace-listers/', views.admin_marketplace_listers, name='admin_marketplace_listers'),
    path('admin-dashboard/marketplace-lister/<int:pk>/update/', views.update_marketplace_lister_status, name='update_marketplace_lister_status'),
    path('admin-dashboard/contact-messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('admin-dashboard/contact-messages/<int:pk>/update/', views.update_contact_message_status, name='update_contact_message_status'),
    path('admin-dashboard/send-notification/', views.admin_send_notification, name='admin_send_notification'),
    path('admin-dashboard/download-delivered-donations/', views.download_delivered_donations_csv, name='download_delivered_donations_csv'),
    
    # Add accounts redirects for Django's default auth
    path('accounts/login/', views.login_view, name='account_login'),
    path('accounts/profile/', views.profile, name='account_profile'),

    # Marketplace URLs
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace/apply/', views.apply_marketplace_lister, name='apply_marketplace_lister'),
    path('marketplace/lister-status/', views.marketplace_lister_status, name='marketplace_lister_status'),
    path('marketplace/<int:pk>/', views.marketplace_item_detail, name='marketplace_item_detail'),
    path('marketplace/<int:pk>/report/', views.report_marketplace_item, name='report_marketplace_item'),
    path('marketplace/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('marketplace/<int:item_pk>/bids/<int:bid_pk>/accept/', views.accept_bid, name='accept_bid'),
    path('marketplace/apply-lister/', views.apply_marketplace_lister, name='apply_marketplace_lister'),
    path('marketplace/create/', views.create_marketplace_item, name='create_marketplace_item'),
    path('marketplace/item/<int:pk>/edit/', views.edit_marketplace_item, name='edit_marketplace_item'),
    path('marketplace/item/<int:pk>/delete/', views.delete_marketplace_item, name='delete_marketplace_item'),
    path('marketplace/item/<int:pk>/update-status/', views.update_marketplace_status, name='update_marketplace_status'),
    path('my-marketplace-items/', views.my_marketplace_items, name='my_marketplace_items'),
    
    # Marketplace messaging URLs
    path('marketplace/<int:item_pk>/send-message/', views.send_message, name='send_message'),
    path('messages/', views.view_messages, name='view_messages'),
    path('messages/<int:item_pk>/<int:user_pk>/', views.view_conversation, name='view_conversation'),
    path('messages/send/<int:item_pk>/', views.send_message, name='send_message'),
    path('messages/delete-conversation/<int:item_pk>/<int:user_pk>/', views.delete_conversation, name='delete_conversation'),
    path('messages/delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

    # API routes
    path('api/login/', api.login_api, name='api_login'),
    path('api/statistics/', api.get_statistics, name='api_statistics'),
    path('api/donations/', api.list_donations, name='api_donations'),
    path('api/donations/<int:pk>/update-status/', api.update_donation_status, name='api_update_donation_status'),
    path('api/donations/<int:pk>/discard/', api.discard_donation, name='api_discard_donation'),
    path('api/assignments/', api.list_assignments, name='api_assignments'),
    path('api/assignments/<int:pk>/update-status/', api.update_assignment_status, name='api_update_assignment_status'),
    path('api/assignments/<int:pk>/discard/', api.discard_assignment, name='api_discard_assignment'),
    path('api/volunteers/', api.list_volunteers, name='api_volunteers'),
    path('api/assign-delivery/', api.assign_delivery, name='api_assign_delivery'),
    path('api/users/', api.list_users, name='api_users'),

    # Chatbot API
    path('api/chatbot/', api.chatbot_api, name='api_chatbot'),

    # Debug URLs - these will work without authentication
    path('debug/', views_debug.debug_home, name='debug_home'),
    path('debug-info/', views_debug.debug_info, name='debug_info'),

    # Add this new URL for money donation confirmation
    path('confirm-money-donation/', views.confirm_money_donation, name='confirm_money_donation'),

    # Chatbot view
    path('chatbot/', views.chatbot, name='chatbot'),

    # New profile completion URL
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    # Donation receipt download URL
    path('donation/<int:donation_id>/receipt/', views.download_donation_receipt, name='download_donation_receipt'),
    path('money-donations/history/', views.money_donation_history, name='money_donation_history'),
    path('money-donations/<int:donation_id>/notify-payment/', views.notify_payment, name='notify_payment'),

    # Bhandara URLs
    path('bhandara/', views.bhandara_list, name='bhandara'),
    path('bhandara/<int:pk>/', bhandara_views.bhandara_detail, name='bhandara_detail'),
    path('bhandara/create/', views.create_bhandara, name='create_bhandara'),
    path('bhandara/manage/', views.manage_bhandaras, name='manage_bhandaras'),
    path('bhandara/<int:event_id>/volunteer/', views.volunteer_signup, name='volunteer_signup'),
    path('bhandara/<int:event_id>/ical/', views.event_ical, name='event_ical'),

    # Admin & Analytics URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('visitor-logs/', views.visitor_logs, name='visitor_logs'),
    
    # Money donation admin actions
    path('money-donation/<int:donation_id>/update-status/', views.update_money_donation_status, name='update_money_donation_status'),
    path('money-donation/<int:donation_id>/cancel/', views.cancel_money_donation, name='cancel_money_donation'),
    path('money-donation/<int:donation_id>/receipt/', views.admin_money_donation_receipt, name='money_donation_receipt'),
    path('money-donation/<int:donation_id>/delete/', views.delete_money_donation, name='delete_money_donation'),
    
    # Food donation admin actions
    path('donation/<int:donation_id>/delete/', views.delete_food_donation, name='delete_food_donation'),
] 