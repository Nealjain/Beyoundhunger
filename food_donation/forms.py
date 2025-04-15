from django import forms
from .models import Bhandara

class BhandaraForm(forms.ModelForm):
    """Form for creating and editing Bhandara events."""
    class Meta:
        model = Bhandara
        fields = [
            'name', 'description', 'organizer_name', 'contact_phone', 'organizer_email', 'organizer_type',
            'address', 'city', 'state', 'postal_code', 'latitude', 'longitude',
            'start_datetime', 'end_datetime', 'food_items', 'expected_attendees', 'special_instructions',
            'volunteers_needed', 'volunteers_count', 'volunteer_tasks',
            'is_recurring', 'recurrence_pattern', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the event'}),
            'organizer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of person or organization'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number (optional)'}),
            'organizer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address (optional)'}),
            'organizer_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Individual, Organization, Temple'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'food_items': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List the food items that will be available'}),
            'expected_attendees': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any special instructions for attendees'}),
            'volunteers_needed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'volunteers_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'volunteer_tasks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What tasks will volunteers perform?'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_pattern': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_pattern = cleaned_data.get('recurrence_pattern')
        
        # Validate start and end datetime
        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                self.add_error('end_datetime', 'End time must be after start time.')
        
        # Validate recurrence pattern if is_recurring is True
        if is_recurring and not recurrence_pattern:
            self.add_error('recurrence_pattern', 'Please select a recurrence pattern.')
        
        return cleaned_data 