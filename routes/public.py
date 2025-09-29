"""
Public Routes
Handles public-facing pages like home, quote calculator, etc.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from modules.sheets_db import SheetsDatabase
from modules.email_service import EmailService
from utils.validators import validate_email, validate_phone, sanitize_input, validate_square_feet
from utils.helpers import calculate_price
from config import Config

public_bp = Blueprint('public', __name__)

# Initialize services
db = SheetsDatabase()
email_service = EmailService()

@public_bp.route('/')
def index():
    """Homepage"""
    return render_template('public/index.html',
                         service_areas=Config.SERVICE_AREAS)

@public_bp.route('/quote', methods=['GET', 'POST'])
def quote():
    """Quote calculator"""
    if request.method == 'POST':
        # Get form data
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))
        phone = sanitize_input(request.form.get('phone'))
        property_type = request.form.get('property_type', 'office')
        square_feet = request.form.get('square_feet', 0)
        service_type = request.form.get('service_type', 'weekly')
        special_instructions = sanitize_input(request.form.get('special_instructions', ''))
        
        # Validation
        errors = []
        if not name:
            errors.append("Name is required")
        if not validate_email(email):
            errors.append("Valid email is required")
        if not validate_phone(phone):
            errors.append("Valid phone number is required")
        
        try:
            square_feet = int(square_feet)
            if square_feet < 100 or square_feet > 100000:
                errors.append("Square footage must be between 100 and 100,000")
        except:
            errors.append("Invalid square footage")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('public/quote.html',
                                 property_types=Config.PRICING.keys(),
                                 form_data=request.form)
        
        # Calculate price
        price = calculate_price(property_type, square_feet, service_type)
        
        # Save quote
        quote_id = db.add_quote(name, email, phone, property_type,
                               square_feet, service_type, price)
        
        # Send email notifications
        email_service.send_quote_notification(name, email, phone,
                                             property_type, square_feet,
                                             price, quote_id)
        
        # Store in session for result page
        session['quote_result'] = {
            'quote_id': quote_id,
            'name': name,
            'price': price,
            'square_feet': square_feet,
            'property_type': property_type,
            'service_type': service_type
        }
        
        return redirect(url_for('public.quote_result'))
    
    return render_template('public/quote.html',
                         property_types=Config.PRICING.keys())

@public_bp.route('/quote/result')
def quote_result():
    """Quote result page"""
    result = session.get('quote_result')
    if not result:
        return redirect(url_for('public.quote'))
    
    return render_template('public/quote_result.html', result=result)

@public_bp.route('/about')
def about():
    """About page"""
    return render_template('public/about.html')

@public_bp.route('/login')
def login():
    """General login page with options"""
    return render_template('public/login.html')