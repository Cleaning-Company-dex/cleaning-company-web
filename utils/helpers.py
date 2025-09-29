"""
Helper Functions
"""

from datetime import datetime, timedelta
import random
import string

def generate_id(prefix='ID'):
    """Generate unique ID with prefix"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"

def calculate_price(property_type, square_feet, frequency='weekly'):
    """Calculate cleaning price"""
    from config import Config
    
    # Base rate per square foot
    base_rates = Config.PRICING
    base_rate = base_rates.get(property_type, 0.10)
    
    # Frequency multipliers
    multipliers = Config.FREQUENCY_MULTIPLIERS
    multiplier = multipliers.get(frequency, 1.0)
    
    # Calculate price
    price = square_feet * base_rate * multiplier
    
    # Apply minimum charge
    return max(price, Config.MINIMUM_CHARGE)

def get_time_slots(date_str, duration_hours=2):
    """Generate available time slots for a date"""
    slots = []
    start_hour = 8  # 8 AM
    end_hour = 18   # 6 PM
    
    for hour in range(start_hour, end_hour, duration_hours):
        time_str = f"{hour:02d}:00"
        slots.append(time_str)
    
    return slots

def format_currency(amount):
    """Format number as currency"""
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"

def get_week_dates(start_date=None):
    """Get dates for current week (Mon-Fri)"""
    if not start_date:
        start_date = datetime.now()
    
    # Get Monday of the week
    monday = start_date - timedelta(days=start_date.weekday())
    
    week_dates = []
    for i in range(5):  # Mon-Fri
        date = monday + timedelta(days=i)
        week_dates.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%A'),
            'display': date.strftime('%b %d')
        })
    
    return week_dates

def get_calendar_data(year=None, month=None):
    """Get calendar data for a month"""
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    
    import calendar
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    return {
        'year': year,
        'month': month,
        'month_name': month_name,
        'calendar': cal,
        'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    }

def send_notification(user_type, message, data=None):
    """Send notification (placeholder for future implementation)"""
    # This could be expanded to send push notifications, SMS, etc.
    print(f"Notification to {user_type}: {message}")
    return True

def get_color_for_employee(employee_name):
    """Get consistent color for employee (for calendar)"""
    colors = [
        '#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
        '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085'
    ]
    
    # Use hash of name to get consistent color
    index = sum(ord(c) for c in employee_name) % len(colors)
    return colors[index]