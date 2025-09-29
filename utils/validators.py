"""
Input Validation Utilities
"""

import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (US format)"""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    return len(digits) == 10

def format_phone(phone):
    """Format phone number to (XXX) XXX-XXXX"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def validate_date(date_string):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except:
        return False

def validate_time(time_string):
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except:
        return False

def sanitize_input(text):
    """Remove potentially harmful HTML/scripts from input"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(text))
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def validate_square_feet(value):
    """Validate square feet is a positive number"""
    try:
        sq_ft = int(value)
        return sq_ft > 0 and sq_ft < 1000000
    except:
        return False

def validate_price(value):
    """Validate price is a positive number"""
    try:
        price = float(value)
        return price >= 0 and price < 100000
    except:
        return False