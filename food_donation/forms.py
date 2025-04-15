from django import forms
from django.core.exceptions import ValidationError
from .models import Bhandara, UserProfile, FoodDonation, MarketplaceItem, MarketplaceLister, MoneyDonation
from .content_moderation import contains_inappropriate_content

class BhandaraForm(forms.ModelForm):
    """Form for creating and editing Bhandara events."""
    class Meta:
        model = Bhandara
        fields = [
            'name', 'description', 'start_datetime', 'end_datetime', 
            'address', 'city', 'state', 'postal_code', 'contact_phone', 
            'organizer_name', 'organizer_email', 'expected_attendees',
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        
        if start and end and start >= end:
            self.add_error('end_datetime', "End date must be after start date")
        
        # Check for inappropriate content
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        organizer_name = cleaned_data.get('organizer_name')
        
        if contains_inappropriate_content(name):
            self.add_error('name', "Please avoid using inappropriate language in the event name.")
        
        if contains_inappropriate_content(description):
            self.add_error('description', "Please avoid using inappropriate language in the description.")
        
        if contains_inappropriate_content(organizer_name):
            self.add_error('organizer_name', "Please avoid using inappropriate language in the organizer name.")
        
        return cleaned_data

class FoodDonationForm(forms.ModelForm):
    class Meta:
        model = FoodDonation
        fields = ['food_type', 'quantity', 'pickup_date', 'pickup_time', 'pickup_address', 'notes']
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
            'pickup_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean_notes(self):
        notes = self.cleaned_data.get('notes')
        if contains_inappropriate_content(notes):
            raise ValidationError("Please avoid using inappropriate language in your notes.")
        return notes

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if contains_inappropriate_content(subject):
            raise ValidationError("Please avoid using inappropriate language in the subject.")
        return subject
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if contains_inappropriate_content(message):
            raise ValidationError("Please avoid using inappropriate language in your message.")
        return message

class MarketplaceItemForm(forms.ModelForm):
    class Meta:
        model = MarketplaceItem
        fields = ['title', 'description', 'price', 'condition', 'location', 'category', 'allow_bidding']
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if contains_inappropriate_content(title):
            raise ValidationError("Please avoid using inappropriate language in the title.")
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if contains_inappropriate_content(description):
            raise ValidationError("Please avoid using inappropriate language in the description.")
        return description

class ChatMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if contains_inappropriate_content(message):
            raise ValidationError("Please avoid using inappropriate language in your message.")
        return message 