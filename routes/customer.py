"""
Customer Routes
Handles customer portal, bookings, payments
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from modules.sheets_db import SheetsDatabase
from modules.email_service import EmailService
from utils.decorators import customer_required
from utils.validators import validate_email, sanitize_input
from utils.helpers import calculate_price
from datetime import datetime
from config import Config

customer_bp = Blueprint('customer', __name__)

# Initialize services
db = SheetsDatabase()
email_service = EmailService()

@customer_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        customer = db.verify_customer(email)
        if customer:
            session['user_id'] = customer['ID']
            session['user_type'] = 'customer'
            session['user_name'] = customer['Name']
            session['customer_data'] = customer
            
            flash(f'Welcome back, {customer["Name"]}!', 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash('Email not found or account inactive', 'error')
    
    return render_template('customer/login.html')

@customer_bp.route('/dashboard')
@customer_required
def dashboard():
    """Customer dashboard"""
    customer_data = session.get('customer_data')
    customer_name = customer_data['Name']
    
    # Get upcoming jobs
    all_jobs = db.get_customer_jobs(customer_name)
    today = datetime.now().strftime('%Y-%m-%d')
    
    upcoming_jobs = [j for j in all_jobs if j['Date'] >= today and j['Status'] == 'scheduled']
    past_jobs = [j for j in all_jobs if j['Completed'] == 'yes']
    
    # Get payments
    payments = db.get_customer_payments(customer_name)
    total_spent = sum(float(p['Amount']) for p in payments)
    
    return render_template('customer/dashboard.html',
                         customer=customer_data,
                         upcoming_jobs=upcoming_jobs[:5],
                         past_jobs=past_jobs[:5],
                         total_spent=total_spent)

@customer_bp.route('/bookings')
@customer_required
def bookings():
    """View all bookings"""
    customer_name = session.get('customer_data')['Name']
    jobs = db.get_customer_jobs(customer_name)
    
    # Separate by status
    upcoming = [j for j in jobs if j['Status'] == 'scheduled']
    completed = [j for j in jobs if j['Completed'] == 'yes']
    
    return render_template('customer/bookings.html',
                         upcoming=upcoming,
                         completed=completed)

@customer_bp.route('/book', methods=['GET', 'POST'])
@customer_required
def book_service():
    """Book a new service"""
    customer_data = session.get('customer_data')
    
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        service_type = request.form.get('service_type', 'weekly')
        special_requests = sanitize_input(request.form.get('special_requests', ''))
        
        # Calculate price
        price = calculate_price(
            customer_data['Business_Type'],
            int(customer_data['Square_Feet']),
            service_type
        )
        
        # Create job (admin will assign employee)
        job_id = db.add_job(
            customer_data['Name'],
            date,
            time,
            'Unassigned',  # Admin will assign
            customer_data['Address'],
            service_type,
            price,
            special_requests
        )
        
        flash('Service booked successfully! We will confirm your appointment soon.', 'success')
        
        # Send notification email
        email_service.send_appointment_confirmation(
            customer_data['Email'],
            customer_data['Name'],
            date,
            time,
            customer_data['Address'],
            'To be assigned'
        )
        
        return redirect(url_for('customer.bookings'))
    
    # Generate available dates (next 30 days, weekdays only)
    available_dates = []
    current_date = datetime.now()
    for i in range(30):
        date = current_date + timedelta(days=i)
        if date.weekday() < 5:  # Monday = 0, Friday = 4
            available_dates.append(date.strftime('%Y-%m-%d'))
    
    return render_template('customer/book_service.html',
                         customer=customer_data,
                         available_dates=available_dates)

@customer_bp.route('/payments')
@customer_required
def payments():
    """View payment history"""
    customer_name = session.get('customer_data')['Name']
    payments = db.get_customer_payments(customer_name)
    
    total_paid = sum(float(p['Amount']) for p in payments)
    
    return render_template('customer/payments.html',
                         payments=payments,
                         total_paid=total_paid)

@customer_bp.route('/profile', methods=['GET', 'POST'])
@customer_required
def profile():
    """Customer profile"""
    customer_data = session.get('customer_data')
    
    if request.method == 'POST':
        # Update profile
        phone = sanitize_input(request.form.get('phone'))
        address = sanitize_input(request.form.get('address'))
        special_instructions = sanitize_input(request.form.get('special_instructions'))
        
        # Update in database
        customers = db.customers.get_all_records()
        for idx, customer in enumerate(customers, start=2):
            if customer['ID'] == customer_data['ID']:
                db.customers.update_cell(idx, 4, phone)  # Phone
                db.customers.update_cell(idx, 5, address)  # Address
                db.customers.update_cell(idx, 11, special_instructions)  # Special_Instructions
                
                # Update session
                customer_data['Phone'] = phone
                customer_data['Address'] = address
                customer_data['Special_Instructions'] = special_instructions
                session['customer_data'] = customer_data
                
                flash('Profile updated successfully!', 'success')
                break
    
    return render_template('customer/profile.html',
                         customer=customer_data)

@customer_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('public.index'))