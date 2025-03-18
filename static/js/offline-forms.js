/**
 * Offline Forms Functionality
 * 
 * This script handles the submission of forms that were created while offline
 * and synchronizes them when the user comes back online.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're online
    if (navigator.onLine) {
        // Check if there are any saved offline forms to submit
        checkForOfflineForms();
    }
    
    // Listen for online event
    window.addEventListener('online', function() {
        console.log('Back online, checking for offline forms...');
        checkForOfflineForms();
    });
});

/**
 * Check for offline forms and offer to submit them
 */
function checkForOfflineForms() {
    const offlineForms = JSON.parse(localStorage.getItem('beyondHungerOfflineForms') || '[]');
    
    if (offlineForms.length > 0) {
        // Show notification about offline forms
        showOfflineFormsNotification(offlineForms.length);
    }
}

/**
 * Show notification about offline forms
 */
function showOfflineFormsNotification(count) {
    // Check if we already have a notification
    if (document.getElementById('offline-forms-notification')) {
        return;
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'offline-forms-notification';
    notification.className = 'offline-notification';
    notification.innerHTML = `
        <div class="offline-notification-content">
            <h4><i class="fas fa-cloud-upload-alt me-2"></i>Offline Forms Available</h4>
            <p>You have ${count} form(s) that were created while offline. Would you like to submit them now?</p>
            <div class="offline-notification-actions">
                <button id="submit-offline-forms" class="btn btn-primary">Submit Now</button>
                <button id="dismiss-offline-notification" class="btn btn-secondary">Later</button>
            </div>
        </div>
    `;
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .offline-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1050;
            max-width: 400px;
            overflow: hidden;
            animation: slideIn 0.3s ease-out;
        }
        
        .offline-notification-content {
            padding: 16px;
        }
        
        .offline-notification h4 {
            margin-top: 0;
            color: #0d6efd;
        }
        
        .offline-notification-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 12px;
        }
        
        @keyframes slideIn {
            from {
                transform: translateY(100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
    `;
    
    // Add to document
    document.head.appendChild(style);
    document.body.appendChild(notification);
    
    // Add event listeners
    document.getElementById('submit-offline-forms').addEventListener('click', function() {
        submitOfflineForms();
        notification.remove();
    });
    
    document.getElementById('dismiss-offline-notification').addEventListener('click', function() {
        notification.remove();
    });
}

/**
 * Submit offline forms
 */
function submitOfflineForms() {
    const offlineForms = JSON.parse(localStorage.getItem('beyondHungerOfflineForms') || '[]');
    
    if (offlineForms.length === 0) {
        return;
    }
    
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'offline-forms-loading';
    loadingIndicator.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p>Submitting offline forms...</p>
    `;
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .offline-forms-loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 2000;
            color: white;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(loadingIndicator);
    
    // Use the API endpoint to submit all forms at once
    const csrfToken = getCsrfToken();
    
    fetch('/api/submit-offline-forms/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ forms: offlineForms }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        loadingIndicator.remove();
        
        if (data.status === 'success') {
            // Count successful submissions
            const successCount = data.results.filter(result => result.status === 'success').length;
            const errorCount = data.results.filter(result => result.status === 'error').length;
            
            if (successCount > 0) {
                alert(`Successfully submitted ${successCount} form(s).`);
                
                // Clear the submitted forms
                localStorage.removeItem('beyondHungerOfflineForms');
            }
            
            if (errorCount > 0) {
                alert(`Failed to submit ${errorCount} form(s). Please try again later.`);
            }
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        // Remove loading indicator
        loadingIndicator.remove();
        
        console.error('Error submitting forms:', error);
        alert('Failed to submit offline forms. Please try again later.');
    });
}

/**
 * Get CSRF token from cookies
 */
function getCsrfToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='));
    
    if (cookieValue) {
        return cookieValue.split('=')[1];
    }
    
    // Try to get from the page
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    return null;
} 