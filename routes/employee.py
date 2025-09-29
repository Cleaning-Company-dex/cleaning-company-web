"""
Employee Routes
Handles employee login, schedule, job management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from modules.sheets_db import SheetsDatabase
from utils.decorators import employee_required
from utils.validators import sanitize_input
from datetime import datetime, timedelta
import os

employee_bp = Blueprint('employee', __name__)

# Initialize database
db = SheetsDatabase()

@employee_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Employee login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        employee = db.verify_employee(username, password)
        if employee:
            session['user_id'] = employee['ID']
            session['user_type'] = 'employee'
            session['user_name'] = employee['Name']
            session['employee_data'] = employee
            
            flash(f'Welcome back, {employee["Name"]}!', 'success')
            return redirect(url_for('employee.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('employee/login.html')

@employee_bp.route('/dashboard')
@employee_required
def dashboard():
    """Employee dashboard"""
    employee_name = session.get('user_name')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's jobs
    todays_jobs = db.get_employee_jobs(employee_name, today)
    
    # Get week stats
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_jobs = []
    for i in range(7):
        date = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
        jobs = db.get_employee_jobs(employee_name, date)
        week_jobs.extend(jobs)
    
    completed_week = len([j for j in week_jobs if j['Completed'] == 'yes'])
    
    return render_template('employee/dashboard.html',
                         todays_jobs=todays_jobs,
                         total_today=len(todays_jobs),
                         completed_week=completed_week,
                         total_week=len(week_jobs))

@employee_bp.route('/schedule')
@employee_required
def schedule():
    """Employee schedule view"""
    employee_name = session.get('user_name')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    view = request.args.get('view', 'week')
    
    if view == 'week':
        # Get week schedule
        week_start = datetime.strptime(date, '%Y-%m-%d')
        week_start = week_start - timedelta(days=week_start.weekday())
        
        schedule = []
        for i in range(5):  # Mon-Fri
            day_date = week_start + timedelta(days=i)
            jobs = db.get_employee_jobs(employee_name, day_date.strftime('%Y-%m-%d'))
            schedule.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'day': day_date.strftime('%A'),
                'display': day_date.strftime('%b %d'),
                'jobs': jobs
            })
        
        return render_template('employee/schedule.html',
                             schedule=schedule,
                             view='week')
    else:
        # Day view
        jobs = db.get_employee_jobs(employee_name, date)
        
        return render_template('employee/schedule_day.html',
                             date=date,
                             jobs=jobs)

@employee_bp.route('/job/<job_id>')
@employee_required
def job_detail(job_id):
    """View job details"""
    jobs = db.get_all_jobs()
    job = next((j for j in jobs if j['ID'] == job_id), None)
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('employee.schedule'))
    
    # Check if employee has access to this job
    if job['Employee'] != session.get('user_name'):
        flash('Access denied', 'error')
        return redirect(url_for('employee.schedule'))
    
    # Get customer details
    customers = db.get_all_customers()
    customer = next((c for c in customers if c['Name'] == job['Customer_Name']), None)
    
    return render_template('employee/job_detail.html',
                         job=job,
                         customer=customer)

@employee_bp.route('/job/<job_id>/checkin', methods=['POST'])
@employee_required
def checkin(job_id):
    """Check in to job"""
    check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    jobs = db.jobs.get_all_records()
    for idx, job in enumerate(jobs, start=2):
        if job['ID'] == job_id:
            db.jobs.update_cell(idx, 9, 'in_progress')  # Status
            db.jobs.update_cell(idx, 12, check_in_time)  # Check_In_Time
            flash('Checked in successfully!', 'success')
            break
    
    return redirect(url_for('employee.job_detail', job_id=job_id))

@employee_bp.route('/job/<job_id>/complete', methods=['GET', 'POST'])
@employee_required
def complete_job(job_id):
    """Complete job"""
    if request.method == 'POST':
        notes = sanitize_input(request.form.get('notes', ''))
        
        # Handle photo upload if provided
        photo_link = ''
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                # Save photo temporarily
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"{job_id}_{photo.filename}")
                photo_path = os.path.join('static/uploads', filename)
                photo.save(photo_path)
                
                # Upload to Google Drive if configured
                try:
                    from modules.drive_storage import DriveStorage
                    storage = DriveStorage()
                    photo_link = storage.upload_file(photo_path, filename)
                    os.remove(photo_path)  # Clean up temp file
                except:
                    photo_link = f"/static/uploads/{filename}"
        
        # Complete the job
        success = db.complete_job(job_id, notes=notes)
        
        if photo_link:
            # Update photo link
            jobs = db.jobs.get_all_records()
            for idx, job in enumerate(jobs, start=2):
                if job['ID'] == job_id:
                    db.jobs.update_cell(idx, 14, photo_link)  # Photos column
                    break
        
        if success:
            flash('Job completed successfully!', 'success')
        else:
            flash('Failed to complete job', 'error')
        
        return redirect(url_for('employee.dashboard'))
    
    return render_template('employee/complete_job.html', job_id=job_id)

@employee_bp.route('/profile')
@employee_required
def profile():
    """Employee profile"""
    employee_data = session.get('employee_data')
    
    # Get employee stats
    employee_name = session.get('user_name')
    all_jobs = db.get_employee_jobs(employee_name)
    completed = len([j for j in all_jobs if j['Completed'] == 'yes'])
    
    stats = {
        'total_jobs': len(all_jobs),
        'completed_jobs': completed,
        'completion_rate': (completed / len(all_jobs) * 100) if all_jobs else 0
    }
    
    return render_template('employee/profile.html',
                         employee=employee_data,
                         stats=stats)

@employee_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('public.index'))