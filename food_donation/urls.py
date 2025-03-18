from django.urls import path
from . import views

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
] 