from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_money_donation_confirmation(user, donation, is_receipt=False):
    """
    Send a confirmation email or receipt for a money donation
    
    Args:
        user: The user who made the donation
        donation: The MoneyDonation instance
        is_receipt: Boolean flag to determine if this is a receipt (True) or just a confirmation (False)
    """
    try:
        if is_receipt:
            subject = 'Receipt for Your Donation - Beyond Hunger'
            template = 'food_donation/email/money_donation_receipt.html'
        else:
            subject = 'Thank You for Your Donation!'
            template = 'food_donation/email/money_donation_confirmation.html'
            
        from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
        to_email = user.email
        
        # Prepare context for the email template
        context = {
            'user': user,
            'donation': donation,
            'site_name': 'Beyond Hunger',
            'is_receipt': is_receipt,
            'receipt_number': f"R-{donation.transaction_id}"
        }
        
        # Render the HTML email
        html_content = render_to_string(template, context)
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
        logger.error(f"Error sending money donation {'receipt' if is_receipt else 'confirmation'} email: {str(e)}")
        return False 