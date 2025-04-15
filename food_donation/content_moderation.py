"""Content moderation tools to filter abusive language."""

import re

# List of words to filter (keep this PG)
INAPPROPRIATE_WORDS = [
    'badword', 'offensive', 'inappropriate',
    # Add more words here as needed
]

def contains_inappropriate_content(text):
    """Check if text contains inappropriate content."""
    if not text:
        return False
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for exact matches of inappropriate words
    for word in INAPPROPRIATE_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    return False

def filter_inappropriate_content(text):
    """Replace inappropriate words with asterisks."""
    if not text:
        return text
    
    filtered_text = text
    text_lower = text.lower()
    
    for word in INAPPROPRIATE_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        matches = list(re.finditer(pattern, text_lower))
        
        # Replace from end to start to preserve indices
        for match in reversed(matches):
            start, end = match.span()
            replacement = '*' * (end - start)
            filtered_text = filtered_text[:start] + replacement + filtered_text[end:]
    
    return filtered_text 