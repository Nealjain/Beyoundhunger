#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beyond_hunger.settings')
django.setup()

from food_donation.models import ChatbotResponse

# Delete existing responses to avoid duplicates
ChatbotResponse.objects.all().delete()

# Create initial responses
responses = [
    # Greetings
    {
        'category': 'greeting',
        'keywords': 'hello,hi,hey,greeting,start,hola',
        'question': 'Hello',
        'response': "Hello! I'm Mr. Jain from Beyond Hunger. How can I help you today?",
        'priority': 10,
    },
    {
        'category': 'greeting',
        'keywords': 'how are you,how r u,how\'s it going',
        'question': 'How are you?',
        'response': "I'm doing well, thank you for asking! How can I assist you with Beyond Hunger's services today?",
        'priority': 5,
    },
    
    # Food Donation
    {
        'category': 'food_donation',
        'keywords': 'donate food,food donate,food donation,can i donate food,how to donate food',
        'question': 'How can I donate food?',
        'response': "To donate food, click on the 'Donate Food' link in the navigation menu. You'll need to provide details about the food, pickup location, and schedule a pickup time. Our volunteers will collect the food from your location.",
        'priority': 10,
    },
    {
        'category': 'food_donation',
        'keywords': 'what food,type of food,which food,food type,food category,accept food',
        'question': 'What types of food can I donate?',
        'response': "We accept non-perishable food items, fresh fruits and vegetables, packaged foods, and cooked meals that are properly stored. Please ensure all food items are within their expiry date and in good condition.",
        'priority': 8,
    },
    
    # Money Donation
    {
        'category': 'money_donation',
        'keywords': 'donate money,money donate,donate cash,financial donation,financial support,monetary donation',
        'question': 'How can I donate money?',
        'response': "You can donate money by visiting the 'Donate Money' page from the navigation menu. We accept UPI payments and bank transfers. After making your donation, you can confirm it on the website to receive a thank you email.",
        'priority': 10,
    },
    {
        'category': 'money_donation',
        'keywords': 'receipt,tax benefit,tax deduction,donation receipt,acknowledgment',
        'question': 'Will I get a receipt for my donation?',
        'response': "Yes, you will receive an automated email acknowledgment for your donation that can be used for tax purposes. All donations to Beyond Hunger are eligible for tax deduction under Section 80G.",
        'priority': 8,
    },
    
    # Volunteer
    {
        'category': 'volunteer',
        'keywords': 'volunteer,become volunteer,join volunteer,how to volunteer,volunteering',
        'question': 'How can I volunteer?',
        'response': "To become a volunteer, please register an account and select the volunteer option during signup. You can specify your availability, vehicle type, and service area. Once registered, you can start accepting food delivery assignments.",
        'priority': 10,
    },
    {
        'category': 'volunteer',
        'keywords': 'volunteer time,volunteer hours,how long,time commitment,volunteer requirement',
        'question': 'How much time do I need to commit as a volunteer?',
        'response': "You can volunteer as per your convenience. There's no minimum time commitment. You can choose to accept delivery assignments based on your availability.",
        'priority': 8,
    },
    
    # Marketplace
    {
        'category': 'marketplace',
        'keywords': 'marketplace,what is marketplace,market place,how marketplace works',
        'question': 'What is the marketplace?',
        'response': "The marketplace is a platform where approved users can list food items for donation or sale. It helps connect people who have excess food with those who need it. You can browse the marketplace to find available food items in your area.",
        'priority': 10,
    },
    {
        'category': 'marketplace',
        'keywords': 'marketplace lister,become lister,sell on marketplace,list on marketplace,marketplace seller',
        'question': 'How can I become a marketplace lister?',
        'response': "To become a marketplace lister, go to the Marketplace section and click on 'Apply to Become a Lister'. You'll need to provide some business information and ID verification. After your application is approved by our admin team, you can start listing items.",
        'priority': 8,
    },
    
    # Account
    {
        'category': 'account',
        'keywords': 'register,signup,sign up,create account,new account',
        'question': 'How do I register?',
        'response': "To register, click on the 'Register' link in the navigation menu. Fill out the registration form with your details, and choose whether you want to be a donor, volunteer, or both. After registering, you can log in and access all features.",
        'priority': 10,
    },
    {
        'category': 'account',
        'keywords': 'login,log in,signin,sign in,cannot login,login issue',
        'question': 'How do I log in?',
        'response': "To log in, click on the 'Login' link in the navigation menu. Enter your username or email and password. If you've forgotten your password, you can reset it from the login page.",
        'priority': 8,
    },
    
    # Contact
    {
        'category': 'general',
        'keywords': 'contact,contact information,reach out,get in touch,phone number,email address',
        'question': 'How can I contact Beyond Hunger?',
        'response': "You can contact us through the 'Contact' page on our website, by email at beyoundhunger1@gmail.com, or by phone at +91 9372820541. We'll get back to you as soon as possible.",
        'priority': 10,
    },
    
    # Fallback
    {
        'category': 'fallback',
        'keywords': 'unknown,help,don\'t understand',
        'question': 'I don\'t understand',
        'response': "I'm sorry, I don't have specific information about that. Can I help you with food donations, money donations, volunteering, or our marketplace?",
        'priority': 1,
    },
]

# Add responses to database
for response_data in responses:
    ChatbotResponse.objects.create(**response_data)

print(f"Created {len(responses)} chatbot responses.") 