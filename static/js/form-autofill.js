/**
 * Form Autofill Functionality
 * 
 * This script automatically fills form fields with user data stored in localStorage
 * and saves form data when submitted to use for future autofill.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if autofill is enabled
    const autofillEnabled = localStorage.getItem('beyondHungerAutofillEnabled');
    if (autofillEnabled === 'false') {
        // If explicitly disabled, don't do anything
        return;
    }
    
    // Fields we want to save and autofill
    const autofillFields = [
        'name', 'email', 'phone', 'address', 'pickup_address', 
        'preferred_pickup_time', 'contact_phone', 'contact_email',
        'location'
    ];
    
    // Get all forms on the page
    const forms = document.querySelectorAll('form');
    
    // For each form, try to autofill fields
    forms.forEach(form => {
        // Skip login, registration, and search forms
        if (form.id === 'login-form' || 
            form.id === 'registration-form' || 
            form.classList.contains('search-form') ||
            form.classList.contains('no-autofill')) {
            return;
        }
        
        // Autofill the form with saved data
        autofillFormFields(form);
        
        // Add location button to address fields
        addLocationButtonsToForm(form);
        
        // Save form data on submit
        form.addEventListener('submit', function() {
            saveFormData(form);
        });
    });
    
    // Add a clear autofill data button if we're on a profile page
    if (window.location.pathname.includes('profile')) {
        const profileSection = document.querySelector('.profile-section');
        if (profileSection) {
            const clearButton = document.createElement('button');
            clearButton.type = 'button';
            clearButton.className = 'btn btn-sm btn-outline-danger mt-3';
            clearButton.innerHTML = '<i class="fas fa-trash me-2"></i>Clear Saved Form Data';
            clearButton.addEventListener('click', function() {
                clearSavedFormData();
                alert('Your saved form data has been cleared.');
            });
            
            profileSection.appendChild(clearButton);
        }
    }
});

/**
 * Add location buttons next to address fields
 */
function addLocationButtonsToForm(form) {
    // Find address fields
    const addressFields = Array.from(form.querySelectorAll('input, textarea')).filter(input => {
        return input.name === 'address' || 
               input.name === 'pickup_address' || 
               input.name === 'location' || 
               input.id === 'id_address' || 
               input.id === 'id_pickup_address' || 
               input.id === 'id_location';
    });
    
    // Add location button next to each address field
    addressFields.forEach(field => {
        // Create a wrapper div if it doesn't exist
        let wrapper = field.parentElement;
        if (!wrapper.classList.contains('input-group')) {
            // Create a new wrapper
            const newWrapper = document.createElement('div');
            newWrapper.className = 'input-group';
            
            // Replace the field with the wrapper containing the field
            field.parentNode.insertBefore(newWrapper, field);
            newWrapper.appendChild(field);
            wrapper = newWrapper;
        }
        
        // Create the location button
        const locationButton = document.createElement('button');
        locationButton.type = 'button';
        locationButton.className = 'btn btn-outline-secondary';
        locationButton.innerHTML = '<i class="fas fa-map-marker-alt"></i>';
        locationButton.title = 'Use my current location';
        
        // Add event listener to the button
        locationButton.addEventListener('click', function() {
            getUserLocation(field);
        });
        
        // Add the button to the wrapper
        wrapper.appendChild(locationButton);
    });
}

/**
 * Get user's current location and fill the address field
 */
function getUserLocation(addressField) {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }
    
    // Show loading indicator
    addressField.placeholder = 'Getting your location...';
    
    navigator.geolocation.getCurrentPosition(
        // Success callback
        function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            
            // Use reverse geocoding to get address
            reverseGeocode(latitude, longitude, addressField);
        },
        // Error callback
        function(error) {
            let errorMessage = 'Unable to retrieve your location: ';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Location permission denied.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information is unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'The request to get location timed out.';
                    break;
                case error.UNKNOWN_ERROR:
                    errorMessage += 'An unknown error occurred.';
                    break;
            }
            
            alert(errorMessage);
            addressField.placeholder = 'Enter your address';
        }
    );
}

/**
 * Convert coordinates to address using reverse geocoding
 */
function reverseGeocode(latitude, longitude, addressField) {
    // Using OpenStreetMap Nominatim API for reverse geocoding
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                addressField.value = data.display_name;
                
                // Save this to localStorage
                const savedData = getSavedFormData() || {};
                savedData[addressField.name] = data.display_name;
                localStorage.setItem('beyondHungerFormData', JSON.stringify(savedData));
            } else {
                throw new Error('No address found');
            }
        })
        .catch(error => {
            console.error('Error getting address:', error);
            alert('Could not retrieve address from your location. Please enter it manually.');
            addressField.placeholder = 'Enter your address';
        });
}

/**
 * Autofill form fields with saved data
 */
function autofillFormFields(form) {
    // Get saved form data
    const savedData = getSavedFormData();
    if (!savedData) return;
    
    // For each input in the form
    form.querySelectorAll('input, textarea, select').forEach(input => {
        // Skip hidden, submit, button, and checkbox inputs
        if (input.type === 'hidden' || 
            input.type === 'submit' || 
            input.type === 'button' || 
            input.type === 'checkbox' ||
            input.name === 'csrfmiddlewaretoken') {
            return;
        }
        
        // If we have saved data for this field and the field is empty
        if (savedData[input.name] && !input.value) {
            input.value = savedData[input.name];
            
            // Trigger change event for select elements
            if (input.tagName === 'SELECT') {
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        }
    });
}

/**
 * Save form data to localStorage
 */
function saveFormData(form) {
    // Check if autofill is enabled
    const autofillEnabled = localStorage.getItem('beyondHungerAutofillEnabled');
    if (autofillEnabled === 'false') {
        // If explicitly disabled, don't save data
        return;
    }
    
    const formData = {};
    const savedData = getSavedFormData() || {};
    
    // For each input in the form
    form.querySelectorAll('input, textarea, select').forEach(input => {
        // Skip hidden, submit, button, and checkbox inputs
        if (input.type === 'hidden' || 
            input.type === 'submit' || 
            input.type === 'button' || 
            input.type === 'checkbox' ||
            input.name === 'csrfmiddlewaretoken') {
            return;
        }
        
        // If the input has a name and value
        if (input.name && input.value) {
            formData[input.name] = input.value;
        }
    });
    
    // Merge with existing data
    const mergedData = { ...savedData, ...formData };
    
    // Save to localStorage
    localStorage.setItem('beyondHungerFormData', JSON.stringify(mergedData));
}

/**
 * Get saved form data from localStorage
 */
function getSavedFormData() {
    const savedData = localStorage.getItem('beyondHungerFormData');
    return savedData ? JSON.parse(savedData) : null;
}

/**
 * Clear all saved form data
 */
function clearSavedFormData() {
    localStorage.removeItem('beyondHungerFormData');
} 