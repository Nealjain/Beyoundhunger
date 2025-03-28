from django.urls import path
from . import views
from . import api

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
    
    # Custom admin dashboard URLs
    path('admin-dashboard/', views.custom_admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/donation/<int:donation_id>/update/', views.update_donation_status, name='update_donation_status'),
    path('admin-dashboard/assignment/<int:assignment_id>/update/', views.update_assignment_status, name='update_assignment_status'),
    
    # Add accounts redirects for Django's default auth
    path('accounts/login/', views.login_view, name='account_login'),
    path('accounts/profile/', views.profile, name='account_profile'),

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
] 