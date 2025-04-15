/**
 * Beyond Hunger - Main JavaScript
 * Created by Neal Jain
 * Version 1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize user agreement
    initUserAgreement();
    
    // Initialize tooltips and popovers
    initBootstrapComponents();
});

/**
 * Initialize user agreement modal
 */
function initUserAgreement() {
    // Check if user has already agreed
    const hasAgreed = localStorage.getItem('userAgreement');
    
    if (!hasAgreed) {
        // Show the agreement modal
        const agreementModal = document.getElementById('userAgreementModal');
        if (agreementModal) {
            const modal = new bootstrap.Modal(agreementModal);
            modal.show();
            
            // Handle agreement acceptance
            const agreeButton = document.getElementById('agreeButton');
            if (agreeButton) {
                agreeButton.addEventListener('click', function() {
                    localStorage.setItem('userAgreement', 'agreed');
                    modal.hide();
                });
            }
        }
    }
}

/**
 * Initialize Bootstrap components
 */
function initBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(function(tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.forEach(function(popoverTriggerEl) {
            new bootstrap.Popover(popoverTriggerEl);
        });
    }
} 