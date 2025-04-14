import json
from django.core.management.base import BaseCommand
from food_donation.models import ChatbotResponse

class Command(BaseCommand):
    help = 'Seeds the database with chatbot responses from the training data'

    def handle(self, *args, **options):
        # Clear existing responses if needed
        ChatbotResponse.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared existing chatbot responses'))
        
        # Create greeting responses
        greetings = [
            {
                'category': 'greeting',
                'keywords': 'hi,hello,hey,greetings',
                'question': 'Hi there',
                'response': "Hello! I'm Mr.Jain, your Beyond Hunger assistant. How can I help you with food donation, volunteering, or using our marketplace today?",
                'priority': 10
            },
            {
                'category': 'greeting',
                'keywords': 'mr jain,mr.jain',
                'question': 'Hello Mr.Jain',
                'response': "Hello! It's nice to meet you. I'm Mr.Jain, your Beyond Hunger assistant. How can I assist you today with food donations, volunteering opportunities, or our marketplace? I'm here to answer any questions you might have about our platform and how we're working to reduce hunger in our community.",
                'priority': 10
            },
            {
                'category': 'greeting',
                'keywords': 'hi {user},hello {user}',
                'question': 'Hi [personalized]',
                'response': "Hello, {user}! I'm Mr.Jain, your Beyond Hunger assistant. How can I help you today?",
                'priority': 20
            },
            {
                'category': 'greeting',
                'keywords': 'thanks,thank you,thx',
                'question': 'Thanks',
                'response': "You're very welcome! I'm glad I could assist you. If you have any other questions about Beyond Hunger, food donations, volunteering opportunities, or our marketplace in the future, please don't hesitate to ask. We appreciate your interest in our platform and mission to reduce hunger in our communities. Have a wonderful day!",
                'priority': 10
            },
            {
                'category': 'greeting',
                'keywords': 'help,assist,support',
                'question': 'Help',
                'response': "I'd be happy to help! Here are the main ways I can assist you with Beyond Hunger:\n\n1. Food Donations - How to donate, what foods are accepted, pickup process\n2. Monetary Donations - How to contribute financially\n3. Volunteering - How to sign up, delivery assignments, responsibilities\n4. Marketplace - How to become a verified lister, create listings, browse items\n5. Account Management - Profile updates, tracking donations\n\nPlease let me know which topic you'd like more information about, or ask any specific question about our platform.",
                'priority': 10
            }
        ]
        
        # Food donation responses
        food_donations = [
            {
                'category': 'food_donation',
                'keywords': 'donate food,food donation,how donate,give food',
                'question': 'How can I donate food?',
                'response': "To donate food, simply click on the 'Donate Food' option in our navigation menu. You'll need to fill out a form with details like food type, quantity, expiry date, and pickup address. We'll then arrange for a volunteer to collect the food. Your generosity helps us feed those in need. Is there anything specific you'd like to donate?",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'what food,type of food,food type,can donate',
                'question': 'What types of food can I donate?',
                'response': "You can donate various types of food including non-perishable items (canned goods, rice, pasta), fresh produce, dairy products (with sufficient shelf life), and prepared foods that are properly packaged. Please ensure all food is within its expiry date and in good condition. We particularly welcome nutritious items that can provide balanced meals. When donating, you'll specify the food type in our donation form so we can properly categorize and distribute it.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'cancel donation,cancel my,stop donation',
                'question': 'Can I cancel my donation?',
                'response': "Yes, you can cancel your donation as long as it hasn't been picked up yet. To cancel, go to your profile page, find the donation in your list, and click on the cancel option. If a volunteer has already been assigned, please add a note explaining the cancellation reason. We understand that circumstances change, but we encourage rescheduling rather than cancelling when possible. If you're having any issues with the donation process, our support team is happy to assist.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'cooked food,prepared food,leftover',
                'question': 'Can I donate cooked food?',
                'response': "Yes, you can donate cooked food as long as it's properly packaged, hasn't been served (leftover from buffets), and is still within safe consumption timeframes. Cooked food donations typically have a higher priority for quick pickup due to shorter shelf life. Please ensure the food has been handled following proper food safety guidelines. When submitting your donation, specify that it's cooked food and include any relevant details like ingredients or preparation date.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'minimum,minimum amount,minimum donation',
                'question': 'Is there a minimum donation amount?',
                'response': "For food donations, there's no minimum quantity required - every bit helps! For monetary donations, the minimum amount is typically $1, but we appreciate contributions of any size. What matters most is the collective impact of our community working together. Whether you can donate a single can of food or a larger amount, your contribution makes a difference in our mission to fight hunger and reduce food waste.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'expire,expired food,food expires,expiry',
                'question': 'What if the food expires before pickup?',
                'response': "Safety is our priority, so if food is about to expire or has expired before pickup, please cancel or update your donation. We don't accept expired food for safety reasons. To prevent this situation, we prioritize perishable items for quick pickup and encourage donors to consider expiry dates when scheduling. If you notice your donation is close to expiring and hasn't been assigned a volunteer yet, please contact our support team immediately so we can expedite the process.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'pickup,how quick,food pickup,collect',
                'question': 'How quickly will my food donation be picked up?',
                'response': "We aim to pick up food donations within 24-48 hours of submission, depending on volunteer availability and your location. Perishable items are given priority for quick pickup. The exact timing will be coordinated with you based on the pickup date you specified in the donation form. Once a volunteer is assigned, you'll receive a notification with the estimated pickup time. If you have urgent timing needs, please mention this in the notes section of your donation form.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'after donate,what happens,process,pickup',
                'question': 'What happens after I donate food?',
                'response': "After you donate food, the process works as follows: 1) Your donation is listed as 'pending' initially, 2) Our admin team reviews it and assigns a volunteer for pickup, 3) The volunteer collects the food from your specified address, 4) The food is delivered to recipients or distribution centers, 5) You receive updates on the status in your profile. This entire process ensures your donation reaches those who need it, and you can track each step along the way.",
                'priority': 10
            },
            {
                'category': 'food_donation',
                'keywords': 'account,create account,register,sign up',
                'question': 'Do I need to create an account to donate?',
                'response': "Yes, you'll need to create an account to donate food or money through our platform. This helps us track donations, provide receipts, and ensure proper delivery. Creating an account is simple - just click on 'Register' in the navigation menu and provide the requested information. Once registered, you can make donations, track their status, and participate in other platform activities like volunteering or the marketplace.",
                'priority': 10
            }
        ]
        
        # Money donation responses
        money_donations = [
            {
                'category': 'money_donation',
                'keywords': 'donate money,money donation,financial,monetary',
                'question': 'How can I make a monetary donation?',
                'response': "You can make a monetary donation by clicking on the 'Donate Money' option in our navigation menu. We accept various payment methods, and your contribution will help us maintain our platform and support those in need. After making a donation, you can track it in your profile page where all your contributions are recorded. Every donation, no matter the size, makes a difference in our fight against hunger.",
                'priority': 10
            },
            {
                'category': 'money_donation',
                'keywords': 'money instead,instead of food,monetary,financial',
                'question': 'Can I donate money instead of food?',
                'response': "Absolutely! You can donate money instead of or in addition to food. Monetary donations are extremely valuable as they help us maintain our platform, support volunteer operations, and fill gaps in food availability. To make a monetary donation, click on the 'Donate Money' option in our navigation menu. You can track your monetary contributions in your profile page, and you'll receive a confirmation that can be used for tax purposes.",
                'priority': 10
            },
            {
                'category': 'money_donation',
                'keywords': 'tax,tax deduction,tax deductible,receipt',
                'question': 'Is my donation tax-deductible?',
                'response': "Yes, food and monetary donations to Beyond Hunger are generally tax-deductible as we are a registered non-profit organization. After making a donation, you'll receive a confirmation that can be used for tax purposes. For monetary donations, you can find receipts in your profile page. However, I recommend consulting with a tax professional for specific advice regarding your situation, as tax laws vary by location and individual circumstances.",
                'priority': 10
            }
        ]
        
        # Volunteer responses
        volunteer_responses = [
            {
                'category': 'volunteer',
                'keywords': 'volunteer,become volunteer,sign up volunteer',
                'question': 'How do I become a volunteer?',
                'response': "To become a volunteer with Beyond Hunger, visit your profile page and register as a volunteer. You'll need to specify your availability, vehicle type (if applicable), and service area. Once registered, our admin team can assign food delivery tasks to you based on your location and availability. Volunteers play a crucial role in connecting donors with recipients. Would you like more information about the volunteer program?",
                'priority': 10
            },
            {
                'category': 'volunteer',
                'keywords': 'volunteer pay,paid,compensation,paid volunteer',
                'question': 'Do volunteers get paid?',
                'response': "No, our volunteers are not paid financially as this is a community service opportunity. However, volunteers do receive benefits such as recognition in our community, the satisfaction of making a positive impact, and potential references for community service hours. Many volunteers find the experience rewarding as they directly connect donors with recipients and play a crucial role in reducing food waste while helping those in need. We greatly value the time and effort our volunteers contribute to our mission.",
                'priority': 10
            },
            {
                'category': 'volunteer',
                'keywords': 'track,volunteer assignment,my assignment,delivery assignment',
                'question': 'How do I track my volunteer assignments?',
                'response': "As a volunteer, you can track your delivery assignments in your profile page under the 'My Delivery Assignments' section. There, you'll find details about each assignment including the pickup location, delivery status, and relevant dates. You'll also receive notifications about new assignments based on your availability and service area. If you have any questions about a specific assignment, you can add notes or contact our admin team for assistance.",
                'priority': 10
            },
            {
                'category': 'volunteer',
                'keywords': 'volunteer delivery,deliveries work,delivery process',
                'question': 'How do volunteer deliveries work?',
                'response': "Volunteer deliveries work like this: When a food donation is received, our system matches it with available volunteers in the same area. The assigned volunteer receives a notification with details about the pickup location, time, and delivery destination. The volunteer then collects the food from the donor and delivers it to the recipient or distribution center. After delivery, they update the status in the system. This process ensures efficient distribution of donated food while providing flexibility for our volunteers.",
                'priority': 10
            }
        ]
        
        # Marketplace responses
        marketplace_responses = [
            {
                'category': 'marketplace',
                'keywords': 'marketplace,market,marketplace work',
                'question': 'Tell me about the marketplace',
                'response': "Our marketplace allows verified users to list food items that can be shared with others. To become a marketplace lister, you need to apply and get verified with an ID. Once approved, you can list items with details like title, description, price (or mark as free), and images. Other users can browse the marketplace and contact you about items they're interested in. The marketplace helps reduce food waste by connecting people with excess food to those who need it.",
                'priority': 10
            },
            {
                'category': 'marketplace',
                'keywords': 'report,report listing,flag,inappropriate',
                'question': 'I want to report a listing on the marketplace',
                'response': "If you need to report a marketplace listing that seems inappropriate or concerning, you can do so by clicking the 'Report Listing' button on the item's detail page. Please provide specific details about why you're reporting it. Our admin team will review the report promptly and take appropriate action. This reporting feature helps us maintain a safe and trustworthy marketplace environment for all users.",
                'priority': 10
            },
            {
                'category': 'marketplace',
                'keywords': 'list item,create listing,post item,sell',
                'question': 'How do I list an item on the marketplace?',
                'response': "To list an item on the marketplace, you first need to be a verified marketplace lister. Apply by clicking on 'Apply Marketplace Lister' in your profile. Once approved, you can create listings by selecting 'Create Marketplace Item' and providing details like title, description, price (or mark as free), category, quantity, expiry date, and photos. Good photos and detailed descriptions increase the chances of your listing being selected. Your listing will be available to all users browsing the marketplace.",
                'priority': 10
            },
            {
                'category': 'marketplace',
                'keywords': 'no interest,listing,no one wants',
                'question': 'What if no one wants my marketplace listing?',
                'response': "If your marketplace listing doesn't receive interest, you have several options: 1) Edit the listing to make it more appealing or adjust the price, 2) Extend the availability period if the food hasn't expired, 3) Consider donating it through our regular food donation process instead, or 4) Remove the listing if necessary. Not all items will find matches, especially time-sensitive ones, but our growing user base increases the chances of connecting your excess food with someone who needs it.",
                'priority': 10
            },
            {
                'category': 'marketplace',
                'keywords': 'marketplace application,application approved,lister application',
                'question': 'How do I know if my marketplace application is approved?',
                'response': "You'll receive a notification once your marketplace lister application has been reviewed. You can also check the status by visiting your profile page and looking at your marketplace lister status. If approved, you'll see an 'Approved' status and gain access to create marketplace listings. If rejected, you'll see the reason and can reapply after addressing any concerns. The approval process typically takes 1-3 business days as our admin team verifies your information and ID documentation.",
                'priority': 10
            }
        ]
        
        # Account responses
        account_responses = [
            {
                'category': 'account',
                'keywords': 'profile,update profile,edit profile,profile information',
                'question': 'How do I update my profile information?',
                'response': "To update your profile information, first log in to your account. Then, click on your username in the top right corner and select 'Profile' from the dropdown menu. On your profile page, you'll find an 'Edit Profile' button that allows you to update your personal details, contact information, and preferences. Don't forget to save your changes after editing. Keeping your profile updated helps us provide better service, especially for volunteers and marketplace participants.",
                'priority': 10
            },
            {
                'category': 'account',
                'keywords': 'see donation,track donation,my donation,donation history',
                'question': 'Where can I see my donations?',
                'response': "You can view all your donations in your profile page. Simply log in and visit your profile, where you'll find separate sections for food donations and monetary contributions. Each donation will show details like date, status, and other relevant information. This helps you track the impact you're making and manage your contribution history. Is there a specific donation you're looking for?",
                'priority': 10
            }
        ]
        
        # General information responses
        general_responses = [
            {
                'category': 'general',
                'keywords': 'beyond hunger,what is,about,platform,mission',
                'question': 'What is Beyond Hunger?',
                'response': "Beyond Hunger is a platform dedicated to connecting food donors with those in need, reducing food waste, and fighting hunger in our communities. We facilitate food donations through a network of volunteers who deliver the food to recipients. We also have a marketplace where verified users can list food items and a monetary donation system. Our mission is to create a sustainable solution to hunger by building a community-driven approach to food sharing and distribution.",
                'priority': 10
            },
            {
                'category': 'general',
                'keywords': 'created,who created,maker,developer,neal',
                'question': 'Who created this platform?',
                'response': "Beyond Hunger was created by a team of developers committed to addressing food insecurity and reducing food waste in our communities. The platform was developed as a solution to connect those with excess food to those who need it, with volunteers facilitating the connection. The project is led by Neal Jain, who envisioned a streamlined system for food donation and distribution. The team continues to improve the platform based on user feedback and community needs.",
                'priority': 10
            },
            {
                'category': 'general',
                'keywords': 'contact,reach,support,help,contact support',
                'question': 'How can I contact support?',
                'response': "You can contact our support team by visiting the 'Contact' page accessible from the navigation menu. There, you'll find a contact form where you can submit your questions or concerns. Alternatively, you can email us directly at support@beyondhunger.org. Our team strives to respond to all inquiries within 24-48 hours. For urgent matters related to food donations or volunteer assignments, please specify this in your message.",
                'priority': 10
            },
            {
                'category': 'general',
                'keywords': 'area,service area,location,where,region',
                'question': 'What areas do you serve?',
                'response': "Beyond Hunger currently serves the local community in and around the city. Our coverage depends on our volunteer network, which is constantly growing. When donating or volunteering, you can specify your location, and our system will determine if we can provide service in that area. We're actively expanding our reach, so if we're not yet in your area, please check back soon or consider becoming a pioneer volunteer to help us extend our services to your community.",
                'priority': 10
            },
            {
                'category': 'general',
                'keywords': 'app,mobile app,android,iphone,ios',
                'question': 'Do you have an app?',
                'response': "Currently, Beyond Hunger is available as a web platform optimized for both desktop and mobile browsers, but we don't have a dedicated mobile app yet. You can access all features by visiting our website on your phone or tablet. Developing a mobile app is on our roadmap for the future as we continue to grow. In the meantime, you can add our website to your home screen for quick access, which provides an app-like experience on most mobile devices.",
                'priority': 10
            },
            {
                'category': 'general',
                'keywords': 'organization,company,business,restaurant,donate',
                'question': 'Can organizations donate through Beyond Hunger?',
                'response': "Absolutely! Beyond Hunger welcomes donations from organizations such as restaurants, grocery stores, catering companies, food producers, and other businesses. Organizations can register with a business account and specify their donation frequency (one-time or recurring). For large or regular donations, we can arrange dedicated pickup schedules. We also provide donation receipts for tax purposes. If you're representing an organization interested in donating, please contact our support team for personalized assistance with setting up your account.",
                'priority': 10
            },
            {
                'category': 'general',
                'keywords': 'data,privacy,information,share,personal',
                'question': 'How is my data used?',
                'response': "At Beyond Hunger, we take your privacy seriously. Your data is primarily used to facilitate donations, volunteer assignments, and marketplace listings. Contact information is shared only with relevant parties (like volunteers for pickup coordination). We don't sell your data to third parties. Your donation history is stored to provide you with records and improve our service. For complete details on how we handle your information, please review our Privacy Policy accessible from the footer of our website.",
                'priority': 10
            }
        ]
        
        # Fallback responses
        fallback_responses = [
            {
                'category': 'fallback',
                'keywords': 'fallback,unknown,default',
                'question': 'Default fallback',
                'response': "I'm sorry, I don't have specific information about that. Can I help you with food donations, volunteering, or our marketplace instead?",
                'priority': 10
            },
            {
                'category': 'fallback',
                'keywords': 'error,mistake,wrong,incorrect',
                'question': 'Error fallback',
                'response': "I apologize for the confusion. Let me try to better understand your question. Could you please rephrase it or specify what aspect of Beyond Hunger you're interested in learning more about?",
                'priority': 10
            }
        ]
        
        # Combine all responses
        all_responses = (
            greetings + 
            food_donations + 
            money_donations + 
            volunteer_responses + 
            marketplace_responses + 
            account_responses + 
            general_responses + 
            fallback_responses
        )
        
        # Create responses in the database
        for response_data in all_responses:
            ChatbotResponse.objects.create(
                category=response_data['category'],
                keywords=response_data['keywords'],
                question=response_data['question'],
                response=response_data['response'],
                priority=response_data['priority'],
                is_active=True
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(all_responses)} chatbot responses')) 