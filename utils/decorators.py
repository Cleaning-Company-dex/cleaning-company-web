"""
Custom Decorators for Route Protection
"""

from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(user_type=None):
    """Require login for accessing routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('public.login'))
            
            if user_type and session.get('user_type') != user_type:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('public.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    """Require employee login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'employee':
            flash('Employee access required.', 'error')
            return redirect(url_for('employee.login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """Require customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'customer':
            flash('Customer access required.', 'error')
            return redirect(url_for('customer.login'))
        return f(*args, **kwargs)
    return decorated_function