from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_money_donation_confirmation(user, donation):
    """
    Send a confirmation email for a money donation
    """
    try:
        subject = 'Thank You for Your Donation!'
        from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
        to_email = user.email
        
        # Prepare context for the email template
        context = {
            'user': user,
            'donation': donation,
            'site_name': 'Beyond Hunger',
        }
        
        # Render the HTML email
        html_content = render_to_string('food_donation/email/money_donation_confirmation.html', context)
        text_content = strip_tags(html_content)  # Create a plain text version
        
        # Create the email message
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        msg.send()
        
        # Mark donation as acknowledged
        donation.is_acknowledged = True
        donation.save()
        
        return True
    except Exception as e:
        logger.error(f"Error sending money donation confirmation email: {str(e)}")
        return False 