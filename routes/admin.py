"""
Admin Routes - Complete Implementation
Full CRUD operations for all business entities
"""

from flask import Blueprint, render_template_string, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from functools import wraps
import hashlib
from modules.sheets_db import SheetsDatabase

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Global database instance - initialize once
_db_instance = None
def get_db():
    """Get database instance - singleton pattern"""
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = SheetsDatabase()
        except Exception as e:
            print(f"Database connection failed: {e}")
            flash('Database connection failed. Please check your credentials.', 'error')
            return None
    return _db_instance

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please login as admin to access this page', 'error')
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return decorated_function

# ========== DASHBOARD ==========

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Main admin dashboard with stats and quick actions"""
    try:
        db = get_db()
        if not db:
            return redirect('/admin-login')

        stats = db.get_dashboard_stats()
        todays_jobs = db.get_jobs_for_date(datetime.now().strftime('%Y-%m-%d'))
        pending_quotes = db.get_pending_quotes()[:5]
        recent_jobs = db.get_recent_jobs(10)
    except Exception as e:
        # Handle database errors gracefully
        print(f"Dashboard error: {e}")
        stats = {
            'total_customers': 0,
            'jobs_today': 0,
            'completed_today': 0,
            'pending_quotes': 0,
            'revenue_today': 0,
            'revenue_month': 0,
            'active_employees': 0,
            'upcoming_jobs': 0
        }
        todays_jobs = []
        pending_quotes = []
        recent_jobs = []
        flash('Database connection issue. Please refresh the page.', 'warning')
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .action-btn { transition: all 0.2s; }
            .action-btn:hover { transform: translateY(-2px); }
        </style>
        <script>
            // Prevent duplicate clicks
            let isNavigating = false;
            function safeNavigate(url) {
                if (isNavigating) return false;
                isNavigating = true;
                window.location.href = url;
                return false;
            }
        </script>
    </head>
    <body class="bg-gray-100 font-sans">
        <!-- Navigation - Updated with safe navigation -->
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🏢 Admin Dashboard</h1>
                <div class="space-x-4">
                    <a href="#" onclick="return safeNavigate('/admin/customers')" class="hover:text-gray-200 transition-colors duration-200">👥 Customers</a>
                    <a href="#" onclick="return safeNavigate('/admin/employees')" class="hover:text-gray-200 transition-colors duration-200">👷 Employees</a>
                    <a href="#" onclick="return safeNavigate('/admin/schedule')" class="hover:text-gray-200 transition-colors duration-200">📅 Schedule</a>
                    <a href="#" onclick="return safeNavigate('/admin/quotes')" class="hover:text-gray-200 transition-colors duration-200">💰 Quotes</a>
                    <a href="#" onclick="return safeNavigate('/admin/payments')" class="hover:text-gray-200 transition-colors duration-200">💳 Payments</a>
                    <a href="#" onclick="return safeNavigate('/logout')" class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition-colors duration-200">Logout</a>
                </div>
            </div>
        </nav>

        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="container mx-auto mt-4 px-4">
                    <div class="bg-{{ 'green' if category == 'success' else 'red' }}-100 border border-{{ 'green' if category == 'success' else 'red' }}-400 text-{{ 'green' if category == 'success' else 'red' }}-700 px-4 py-3 rounded-lg relative" role="alert">
                        {{ message }}
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Stats Grid -->
        <div class="container mx-auto mt-8 px-4">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow-md action-btn cursor-pointer" onclick="safeNavigate('/admin/customers')">
                    <div class="text-gray-500 text-sm">Total Customers</div>
                    <div class="text-4xl font-extrabold text-indigo-600">{{ stats.total_customers }}</div>
                    <div class="text-sm text-indigo-500 mt-2">View all →</div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md action-btn cursor-pointer" onclick="safeNavigate('/admin/schedule')">
                    <div class="text-gray-500 text-sm">Jobs Today</div>
                    <div class="text-4xl font-extrabold text-green-600">{{ stats.jobs_today }}</div>
                    <div class="text-sm text-gray-600">Completed: {{ stats.completed_today }}</div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md action-btn cursor-pointer" onclick="safeNavigate('/admin/payments')">
                    <div class="text-gray-500 text-sm">Revenue Today</div>
                    <div class="text-4xl font-extrabold text-blue-600">${{ "%.2f"|format(stats.revenue_today) }}</div>
                    <div class="text-sm text-gray-600">This Month: ${{ "%.2f"|format(stats.revenue_month) }}</div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md action-btn cursor-pointer" onclick="safeNavigate('/admin/quotes')">
                    <div class="text-gray-500 text-sm">Pending Quotes</div>
                    <div class="text-4xl font-extrabold text-orange-600">{{ stats.pending_quotes }}</div>
                    <div class="text-sm text-orange-500">View quotes →</div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="bg-white rounded-lg shadow-md mb-8 p-6">
                <h2 class="text-xl font-bold border-b pb-4 mb-4">⚡ Quick Actions</h2>
                <div class="flex flex-wrap gap-4">
                    <a href="#" onclick="safeNavigate('/admin/customers/add')" class="bg-green-500 text-white px-6 py-3 rounded-full hover:bg-green-600 transition-colors duration-200">➕ Add Customer</a>
                    <a href="#" onclick="safeNavigate('/admin/employees/add')" class="bg-blue-500 text-white px-6 py-3 rounded-full hover:bg-blue-600 transition-colors duration-200">➕ Add Employee</a>
                    <a href="#" onclick="safeNavigate('/admin/jobs/add')" class="bg-purple-500 text-white px-6 py-3 rounded-full hover:bg-purple-600 transition-colors duration-200">📅 Schedule Job</a>
                    <a href="#" onclick="safeNavigate('/admin/payments/add')" class="bg-yellow-500 text-white px-6 py-3 rounded-full hover:bg-yellow-600 transition-colors duration-200">💳 Record Payment</a>
                </div>
            </div>

            <!-- Today's Jobs -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex justify-between items-center border-b pb-4 mb-4">
                    <h2 class="text-xl font-bold">📋 Today's Jobs</h2>
                    <a href="#" onclick="safeNavigate('/admin/jobs/add')" class="bg-indigo-500 text-white px-4 py-2 rounded-full text-sm hover:bg-indigo-600 transition-colors duration-200">Add Job</a>
                </div>
                {% if todays_jobs %}
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-600 text-sm">
                            <th class="pb-2">Time</th>
                            <th class="pb-2">Customer</th>
                            <th class="pb-2">Employee</th>
                            <th class="pb-2">Status</th>
                            <th class="pb-2 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for job in todays_jobs %}
                        <tr class="border-t hover:bg-gray-50">
                            <td class="py-3">{{ job.Time }}</td>
                            <td class="py-3">{{ job.Customer_Name }}</td>
                            <td class="py-3">{{ job.Employee or 'Unassigned' }}</td>
                            <td class="py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold
                                    {% if job.Status == 'Completed' %}bg-green-100 text-green-800{% else %}bg-yellow-100 text-yellow-800{% endif %}">
                                    {{ job.Status }}
                                </span>
                            </td>
                            <td class="py-3 text-right space-x-2">
                                <a href="#" onclick="safeNavigate('/admin/job/{{ job.ID }}/edit')" class="text-blue-600 hover:underline">Edit</a>
                                {% if job.Status != 'Completed' %}
                                <form method="POST" action="/admin/job/{{ job.ID }}/complete" style="display:inline;">
                                    <button type="submit" class="text-green-600 hover:underline">Complete</button>
                                </form>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-gray-500 text-center py-4">No jobs scheduled for today. Time to find a new client!</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    from flask import get_flashed_messages
    return render_template_string(template, stats=stats, todays_jobs=todays_jobs, 
                                 pending_quotes=pending_quotes, get_flashed_messages=get_flashed_messages)

# ========== CUSTOMER MANAGEMENT ==========

@admin_bp.route('/customers')
@admin_required
def customers():
    """List all customers with search and actions"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    customers = db.get_all_customers()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Management</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            function confirmDelete(name) {
                return confirm('Are you sure you want to delete customer: ' + name + '?');
            }
        </script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">👥 Customer Management</h1>
                <div class="space-x-4">
                    <a href="/admin/dashboard" class="hover:text-gray-200 transition-colors duration-200">Dashboard</a>
                    <a href="/admin/customers/add" class="bg-green-500 px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200">➕ Add Customer</a>
                    <a href="/logout" class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition-colors duration-200">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="bg-white rounded-lg shadow-md p-6">
                {% if customers %}
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-600 border-b text-sm">
                            <th class="pb-3">Name</th>
                            <th class="pb-3">Email</th>
                            <th class="pb-3">Phone</th>
                            <th class="pb-3">Type</th>
                            <th class="pb-3">Frequency</th>
                            <th class="pb-3">Status</th>
                            <th class="pb-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for customer in customers %}
                        <tr class="border-t hover:bg-gray-50">
                            <td class="py-3">{{ customer.Name }}</td>
                            <td class="py-3">{{ customer.Email }}</td>
                            <td class="py-3">{{ customer.Phone }}</td>
                            <td class="py-3">{{ customer.Business_Type }}</td>
                            <td class="py-3">{{ customer.Service_Frequency }}</td>
                            <td class="py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold
                                    {% if customer.Status == 'active' %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                                    {{ customer.Status }}
                                </span>
                            </td>
                            <td class="py-3 text-right space-x-2">
                                <a href="/admin/customer/{{ customer.ID }}/edit" class="text-blue-600 hover:underline">Edit</a>
                                <a href="/admin/jobs/add?customer={{ customer.ID }}" class="text-green-600 hover:underline">Schedule</a>
                                <form method="POST" action="/admin/customer/{{ customer.ID }}/delete" style="display:inline;"
                                    onsubmit="return confirmDelete('{{ customer.Name }}')">
                                    <button type="submit" class="text-red-600 hover:underline">Delete</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-gray-500 text-center py-4">No customers found.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, customers=customers)

@admin_bp.route('/customers/add', methods=['GET', 'POST'])
@admin_required
def add_customer():
    """Add new customer"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    
    if request.method == 'POST':
        customer_id = db.add_customer(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            business_type=request.form.get('business_type', 'office'),
            square_feet=int(request.form.get('square_feet', 1000)),
            service_frequency=request.form.get('service_frequency', 'weekly'),
            special_instructions=request.form.get('special_instructions', '')
        )
        
        flash('Customer added successfully!', 'success')
        
        if request.form.get('schedule_now') == 'yes':
            return redirect(f'/admin/jobs/add?customer={customer_id}')
        
        return redirect('/admin/customers')
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Customer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">➕ Add New Customer</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Name</label>
                            <input type="text" name="name" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" name="email" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Phone</label>
                                <input type="tel" name="phone" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Address</label>
                            <input type="text" name="address" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Business Type</label>
                                <select name="business_type" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="office">Office</option>
                                    <option value="retail">Retail</option>
                                    <option value="medical">Medical</option>
                                    <option value="restaurant">Restaurant</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Square Feet</label>
                                <input type="number" name="square_feet" value="1000" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Service Frequency</label>
                                <select name="service_frequency" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="weekly">Weekly</option>
                                    <option value="biweekly">Bi-Weekly</option>
                                    <option value="monthly">Monthly</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Special Instructions</label>
                            <textarea name="special_instructions" rows="3" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2"></textarea>
                        </div>
                        
                        <div>
                            <label class="flex items-center">
                                <input type="checkbox" name="schedule_now" value="yes" class="mr-2 rounded-lg">
                                <span class="text-sm">Schedule a job immediately after adding</span>
                            </label>
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/customers" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors duration-200">Add Customer</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template)

@admin_bp.route('/customer/<customer_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_customer(customer_id):
    """Edit customer information"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    customer = db.get_customer_by_id(customer_id)
    
    if not customer:
        flash('Customer not found', 'error')
        return redirect('/admin/customers')
    
    if request.method == 'POST':
        # Update customer
        customers = db.customers.get_all_records()
        for idx, c in enumerate(customers, start=2):
            if c['ID'] == customer_id:
                db.customers.update_cell(idx, 2, request.form.get('name'))
                db.customers.update_cell(idx, 3, request.form.get('email'))
                db.customers.update_cell(idx, 4, request.form.get('phone'))
                db.customers.update_cell(idx, 5, request.form.get('address'))
                db.customers.update_cell(idx, 6, request.form.get('business_type'))
                db.customers.update_cell(idx, 8, request.form.get('status'))
                db.customers.update_cell(idx, 9, request.form.get('square_feet'))
                db.customers.update_cell(idx, 10, request.form.get('service_frequency'))
                db.customers.update_cell(idx, 13, request.form.get('special_instructions'))
                break
        
        flash('Customer updated successfully!', 'success')
        return redirect('/admin/customers')
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Customer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">✏️ Edit Customer</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Status</label>
                            <select name="status" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="active" {% if customer.Status == 'active' %}selected{% endif %}>Active</option>
                                <option value="inactive" {% if customer.Status == 'inactive' %}selected{% endif %}>Inactive</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Name</label>
                            <input type="text" name="name" value="{{ customer.Name }}" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" name="email" value="{{ customer.Email }}" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Phone</label>
                                <input type="tel" name="phone" value="{{ customer.Phone }}" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Address</label>
                            <input type="text" name="address" value="{{ customer.Address }}" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Business Type</label>
                                <select name="business_type" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="office" {% if customer.Business_Type == 'office' %}selected{% endif %}>Office</option>
                                    <option value="retail" {% if customer.Business_Type == 'retail' %}selected{% endif %}>Retail</option>
                                    <option value="medical" {% if customer.Business_Type == 'medical' %}selected{% endif %}>Medical</option>
                                    <option value="restaurant" {% if customer.Business_Type == 'restaurant' %}selected{% endif %}>Restaurant</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Square Feet</label>
                                <input type="number" name="square_feet" value="{{ customer.Square_Feet }}" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Service Frequency</label>
                                <select name="service_frequency" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="weekly" {% if customer.Service_Frequency == 'weekly' %}selected{% endif %}>Weekly</option>
                                    <option value="biweekly" {% if customer.Service_Frequency == 'biweekly' %}selected{% endif %}>Bi-Weekly</option>
                                    <option value="monthly" {% if customer.Service_Frequency == 'monthly' %}selected{% endif %}>Monthly</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Special Instructions</label>
                            <textarea name="special_instructions" rows="3" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">{{ customer.Special_Instructions }}</textarea>
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/customers" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200">Save Changes</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, customer=customer)

@admin_bp.route('/customer/<customer_id>/delete', methods=['POST'])
@admin_required
def delete_customer(customer_id):
    """Delete customer"""
    db = get_db()
    if not db:
        flash('Database connection failed.', 'error')
        return redirect('/admin/customers')

    if db.update_customer_status(customer_id, 'deleted'):
        flash('Customer deleted successfully!', 'success')
    else:
        flash('Error deleting customer', 'error')
    
    return redirect('/admin/customers')

# ========== EMPLOYEE MANAGEMENT ==========

@admin_bp.route('/employees')
@admin_required
def employees():
    """List all employees"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    employees = db.get_all_employees()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Employee Management</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">👷 Employee Management</h1>
                <div class="space-x-4">
                    <a href="/admin/dashboard" class="hover:text-gray-200 transition-colors duration-200">Dashboard</a>
                    <a href="/admin/employees/add" class="bg-green-500 px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200">➕ Add Employee</a>
                    <a href="/logout" class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition-colors duration-200">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="bg-white rounded-lg shadow-md p-6">
                {% if employees %}
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-600 border-b text-sm">
                            <th class="pb-3">Name</th>
                            <th class="pb-3">Email</th>
                            <th class="pb-3">Phone</th>
                            <th class="pb-3">Username</th>
                            <th class="pb-3">Status</th>
                            <th class="pb-3">Hourly Rate</th>
                            <th class="pb-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for emp in employees %}
                        <tr class="border-t hover:bg-gray-50">
                            <td class="py-3">{{ emp.Name }}</td>
                            <td class="py-3">{{ emp.Email }}</td>
                            <td class="py-3">{{ emp.Phone }}</td>
                            <td class="py-3">{{ emp.Username }}</td>
                            <td class="py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold
                                    {% if emp.Active == 'yes' %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
                                    {{ 'Active' if emp.Active == 'yes' else 'Inactive' }}
                                </span>
                            </td>
                            <td class="py-3">${{ emp.Hourly_Rate }}/hr</td>
                            <td class="py-3 text-right space-x-2">
                                <a href="/admin/employee/{{ emp.ID }}/edit" class="text-blue-600 hover:underline">Edit</a>
                                <form method="POST" action="/admin/employee/{{ emp.ID }}/toggle" style="display:inline;">
                                    <button type="submit" class="text-orange-600 hover:underline">
                                        {{ 'Deactivate' if emp.Active == 'yes' else 'Activate' }}
                                    </button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-gray-500 text-center py-4">No employees found.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, employees=employees)

@admin_bp.route('/employees/add', methods=['GET', 'POST'])
@admin_required
def add_employee():
    """Add new employee"""
    db = get_db()
    if not db:
        return redirect('/admin-login')

    if request.method == 'POST':
        employee_id = db.add_employee(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            username=request.form.get('username'),
            password=request.form.get('password'),
            hourly_rate=float(request.form.get('hourly_rate', 20)),
            color_code='#3498db'
        )
        
        flash(f'Employee added successfully! Username: {request.form.get("username")}', 'success')
        return redirect('/admin/employees')
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Employee</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">➕ Add New Employee</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Full Name</label>
                            <input type="text" name="name" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" name="email" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Phone</label>
                                <input type="tel" name="phone" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Username</label>
                                <input type="text" name="username" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Password</label>
                                <input type="password" name="password" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Hourly Rate</label>
                            <input type="number" name="hourly_rate" value="20" step="0.50" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/employees" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors duration-200">Add Employee</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template)

@admin_bp.route('/employee/<employee_id>/toggle', methods=['POST'])
@admin_required
def toggle_employee(employee_id):
    """Toggle employee active status"""
    db = get_db()
    if not db:
        flash('Database connection failed.', 'error')
        return redirect('/admin/employees')
    
    employees = db.get_all_employees()
    
    for emp in employees:
        if emp['ID'] == employee_id:
            new_status = 'no' if emp['Active'] == 'yes' else 'yes'
            db.update_employee_status(employee_id, new_status == 'yes')
            flash(f'Employee {"activated" if new_status == "yes" else "deactivated"} successfully!', 'success')
            break
    
    return redirect('/admin/employees')

# ========== JOB SCHEDULING ==========

@admin_bp.route('/schedule')
@admin_required
def schedule():
    """View job schedule"""
    db = get_db()
    if not db:
        return redirect('/admin-login')

    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    all_jobs = db.get_all_jobs()
    
    # Generate week view
    current_date = datetime.strptime(date_str, '%Y-%m-%d')
    week_start = current_date - timedelta(days=current_date.weekday())
    week_dates = []
    week_jobs = {}
    
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        week_dates.append({
            'date': day_str,
            'day': day.strftime('%A'),
            'display': day.strftime('%b %d')
        })
        week_jobs[day_str] = db.get_jobs_for_date(day_str)
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Schedule</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">📅 Schedule</h1>
                <div class="space-x-4">
                    <a href="/admin/dashboard" class="hover:text-gray-200 transition-colors duration-200">Dashboard</a>
                    <a href="/admin/jobs/add" class="bg-green-500 px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200">➕ Schedule Job</a>
                    <a href="/logout" class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition-colors duration-200">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <!-- All Jobs List -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex justify-between items-center border-b pb-4 mb-4">
                    <h2 class="text-xl font-bold">All Scheduled Jobs</h2>
                    <a href="/admin/jobs/add" class="bg-indigo-500 text-white px-4 py-2 rounded-full text-sm hover:bg-indigo-600 transition-colors duration-200">Add Job</a>
                </div>
                {% if all_jobs %}
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-600 border-b text-sm">
                            <th class="pb-3">Date</th>
                            <th class="pb-3">Time</th>
                            <th class="pb-3">Customer</th>
                            <th class="pb-3">Employee</th>
                            <th class="pb-3">Status</th>
                            <th class="pb-3">Price</th>
                            <th class="pb-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for job in all_jobs %}
                        {% if job.Status != 'cancelled' %}
                        <tr class="border-t hover:bg-gray-50">
                            <td class="py-3">{{ job.Date }}</td>
                            <td class="py-3">{{ job.Time }}</td>
                            <td class="py-3">{{ job.Customer_Name }}</td>
                            <td class="py-3">{{ job.Employee or 'Unassigned' }}</td>
                            <td class="py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold
                                    {% if job.Status == 'Completed' %}bg-green-100 text-green-800
                                    {% elif job.Status == 'scheduled' %}bg-yellow-100 text-yellow-800
                                    {% elif job.Status == 'in_progress' %}bg-blue-100 text-blue-800
                                    {% else %}bg-gray-100 text-gray-800{% endif %}">
                                    {{ job.Status }}
                                </span>
                            </td>
                            <td class="py-3">${{ job.Price }}</td>
                            <td class="py-3 text-right space-x-2">
                                <a href="/admin/job/{{ job.ID }}/edit" class="text-blue-600 hover:underline">Edit</a>
                                {% if job.Status != 'Completed' %}
                                <form method="POST" action="/admin/job/{{ job.ID }}/complete" style="display:inline;">
                                    <button type="submit" class="text-green-600 hover:underline">Complete</button>
                                </form>
                                {% endif %}
                            </td>
                        </tr>
                        {% endif %}
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-gray-500 text-center py-4">No jobs scheduled.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, week_dates=week_dates, week_jobs=week_jobs, all_jobs=all_jobs)

@admin_bp.route('/jobs/add', methods=['GET', 'POST'])
@admin_required
def add_job():
    """Schedule new job"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        customer = db.get_customer_by_id(customer_id)
        
        if customer:
            job_id = db.add_job(
                customer_name=customer['Name'],
                date=request.form.get('date'),
                time=request.form.get('time'),
                employee=request.form.get('employee'),
                address=customer['Address'],
                service_type=request.form.get('service_type', 'regular'),
                price=float(request.form.get('price', 100))
            )
            flash('Job scheduled successfully!', 'success')
            return redirect('/admin/schedule')
    
    customer_id = request.args.get('customer')
    selected_customer = db.get_customer_by_id(customer_id) if customer_id else None
    customers = db.get_all_customers()
    employees = db.get_active_employees()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Schedule Job</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">📅 Schedule New Job</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Customer</label>
                            <select name="customer_id" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="">Select Customer</option>
                                {% for customer in customers %}
                                <option value="{{ customer.ID }}" {% if selected_customer and selected_customer.ID == customer.ID %}selected{% endif %}>
                                    {{ customer.Name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Date</label>
                                <input type="date" name="date" required value="{{ datetime.now().strftime('%Y-%m-%d') }}"
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Time</label>
                                <input type="time" name="time" required value="09:00"
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Assign Employee</label>
                            <select name="employee" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="">Select Employee</option>
                                {% for emp in employees %}
                                <option value="{{ emp.Name }}">{{ emp.Name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Service Type</label>
                                <select name="service_type" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="regular">Regular Cleaning</option>
                                    <option value="deep">Deep Cleaning</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Price</label>
                                <input type="number" name="price" value="100" step="0.01" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/schedule" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors duration-200">Schedule Job</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, customers=customers, employees=employees, 
                                 selected_customer=selected_customer, datetime=datetime)

@admin_bp.route('/job/<job_id>/complete', methods=['POST'])
@admin_required
def complete_job(job_id):
    """Mark job as completed"""
    db = get_db()
    if not db:
        flash('Database connection failed.', 'error')
        return redirect('/admin/schedule')
    
    if db.complete_job(job_id):
        flash('Job marked as completed!', 'success')
    else:
        flash('Error completing job', 'error')
    
    return redirect('/admin/schedule')

# ========== QUOTES MANAGEMENT ==========

@admin_bp.route('/quotes')
@admin_required
def quotes():
    """View all quotes"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    quotes = db.get_all_quotes()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quote Management</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">💰 Quote Management</h1>
                <div class="space-x-4">
                    <a href="/admin/dashboard" class="hover:text-gray-200 transition-colors duration-200">Dashboard</a>
                    <a href="/logout" class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition-colors duration-200">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="bg-white rounded-lg shadow-md p-6">
                {% if quotes %}
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-600 border-b text-sm">
                            <th class="pb-3">Name</th>
                            <th class="pb-3">Email</th>
                            <th class="pb-3">Phone</th>
                            <th class="pb-3">Type</th>
                            <th class="pb-3">Price</th>
                            <th class="pb-3">Status</th>
                            <th class="pb-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for quote in quotes %}
                        <tr class="border-t hover:bg-gray-50">
                            <td class="py-3">{{ quote.Name }}</td>
                            <td class="py-3">{{ quote.Email }}</td>
                            <td class="py-3">{{ quote.Phone }}</td>
                            <td class="py-3">{{ quote.Property_Type }}</td>
                            <td class="py-3">${{ quote.Calculated_Price }}</td>
                            <td class="py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold
                                    {% if quote.Status == 'pending' %}bg-yellow-100 text-yellow-800
                                    {% elif quote.Status == 'converted' %}bg-green-100 text-green-800
                                    {% else %}bg-red-100 text-red-800{% endif %}">
                                    {{ quote.Status }}
                                </span>
                            </td>
                            <td class="py-3 text-right space-x-2">
                                <a href="/admin/quote/{{ quote.ID }}/edit" class="text-blue-600 hover:underline">Edit</a>
                                {% if quote.Status == 'pending' %}
                                <form method="POST" action="/admin/quote/{{ quote.ID }}/convert" style="display:inline;">
                                    <button type="submit" class="text-green-600 hover:underline">Convert</button>
                                </form>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-gray-500 text-center py-4">No quotes found.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, quotes=quotes)

@admin_bp.route('/quote/<quote_id>/convert', methods=['POST'])
@admin_required
def convert_quote(quote_id):
    """Convert quote to customer"""
    db = get_db()
    if not db:
        flash('Database connection failed.', 'error')
        return redirect('/admin/quotes')
    
    customer_id = db.convert_quote(quote_id)
    if customer_id:
        flash('Quote converted to customer successfully!', 'success')
        return redirect(f'/admin/jobs/add?customer={customer_id}')
    else:
        flash('Error converting quote', 'error')
        return redirect('/admin/quotes')

# ========== PAYMENTS ==========

@admin_bp.route('/payments')
@admin_required
def payments():
    """View all payments"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    payments = db.get_all_payments()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Management</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">💳 Payment Management</h1>
                <div class="space-x-4">
                    <a href="/admin/dashboard" class="hover:text-gray-200 transition-colors duration-200">Dashboard</a>
                    <a href="/admin/payments/add" class="bg-green-500 px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200">➕ Record Payment</a>
                    <a href="/logout" class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition-colors duration-200">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="bg-white rounded-lg shadow-md p-6">
                {% if payments %}
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-600 border-b text-sm">
                            <th class="pb-3">Date</th>
                            <th class="pb-3">Customer</th>
                            <th class="pb-3">Amount</th>
                            <th class="pb-3">Method</th>
                            <th class="pb-3">Invoice #</th>
                            <th class="pb-3">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for payment in payments %}
                        <tr class="border-t hover:bg-gray-50">
                            <td class="py-3">{{ payment.Date[:10] if payment.Date else '' }}</td>
                            <td class="py-3">{{ payment.Customer_Name }}</td>
                            <td class="py-3 font-bold text-green-600">${{ payment.Amount }}</td>
                            <td class="py-3">{{ payment.Method }}</td>
                            <td class="py-3">{{ payment.Invoice_Number }}</td>
                            <td class="py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                                    {{ payment.Status }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-gray-500 text-center py-4">No payments found.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, payments=payments)

@admin_bp.route('/payments/add', methods=['GET', 'POST'])
@admin_required
def add_payment():
    """Record new payment"""
    db = get_db()
    if not db:
        return redirect('/admin-login')
    
    if request.method == 'POST':
        payment_id = db.add_payment(
            customer_name=request.form.get('customer_name'),
            amount=float(request.form.get('amount')),
            method=request.form.get('method', 'card'),
            job_ids=request.form.get('job_ids', ''),
            notes=request.form.get('notes', '')
        )
        
        flash('Payment recorded successfully!', 'success')
        return redirect('/admin/payments')
    
    customers = db.get_all_customers()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Record Payment</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">💳 Record Payment</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Customer</label>
                            <select name="customer_name" required class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="">Select Customer</option>
                                {% for customer in customers %}
                                <option value="{{ customer.Name }}">{{ customer.Name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Amount</label>
                            <input type="number" name="amount" step="0.01" required
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Payment Method</label>
                            <select name="method" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="card">Credit Card</option>
                                <option value="cash">Cash</option>
                                <option value="check">Check</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Notes</label>
                            <textarea name="notes" rows="3"
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2"></textarea>
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/payments" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors duration-200">Record Payment</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, customers=customers)
    
# ========== MISSING ROUTES ==========

@admin_bp.route('/job/<job_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_job(job_id):
    """Edit job - including reassigning employee"""
    db = get_db()
    if not db:
        return redirect('/admin-login')

    jobs = db.get_all_jobs()
    job = next((j for j in jobs if j['ID'] == job_id), None)
    
    if not job:
        flash('Job not found', 'error')
        return redirect('/admin/schedule')
    
    if request.method == 'POST':
        # Update job directly in sheets
        for idx, j in enumerate(jobs, start=2):
            if j['ID'] == job_id:
                db.jobs.update_cell(idx, 3, request.form.get('date'))  # Date
                db.jobs.update_cell(idx, 4, request.form.get('time'))  # Time
                db.jobs.update_cell(idx, 5, request.form.get('employee'))  # Employee
                db.jobs.update_cell(idx, 7, request.form.get('service_type'))  # Service_Type
                db.jobs.update_cell(idx, 8, request.form.get('price'))  # Price
                db.jobs.update_cell(idx, 9, request.form.get('status'))  # Status
                db.jobs.update_cell(idx, 11, request.form.get('notes'))  # Notes
                break
        
        flash('Job updated successfully!', 'success')
        return redirect('/admin/schedule')
    
    employees = db.get_active_employees()
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Job</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">✏️ Edit Job</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                    <p class="text-sm text-blue-800"><strong>Customer:</strong> {{ job.Customer_Name }}</p>
                    <p class="text-sm text-blue-800"><strong>Address:</strong> {{ job.Address }}</p>
                </div>
                
                <form method="POST">
                    <div class="space-y-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Date</label>
                                <input type="date" name="date" value="{{ job.Date }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Time</label>
                                <input type="time" name="time" value="{{ job.Time }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Assign Employee</label>
                            <select name="employee" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="">Unassigned</option>
                                {% for emp in employees %}
                                <option value="{{ emp.Name }}" {% if job.Employee == emp.Name %}selected{% endif %}>
                                    {{ emp.Name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Service Type</label>
                                <select name="service_type" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="Regular Cleaning" {% if job.Service_Type == 'Regular Cleaning' %}selected{% endif %}>Regular Cleaning</option>
                                    <option value="Deep Cleaning" {% if job.Service_Type == 'Deep Cleaning' %}selected{% endif %}>Deep Cleaning</option>
                                    <option value="Move Out Cleaning" {% if job.Service_Type == 'Move Out Cleaning' %}selected{% endif %}>Move Out Cleaning</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Status</label>
                                <select name="status" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="scheduled" {% if job.Status == 'scheduled' %}selected{% endif %}>Scheduled</option>
                                    <option value="in_progress" {% if job.Status == 'in_progress' %}selected{% endif %}>In Progress</option>
                                    <option value="completed" {% if job.Status == 'completed' %}selected{% endif %}>Completed</option>
                                    <option value="cancelled" {% if job.Status == 'cancelled' %}selected{% endif %}>Cancelled</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Price</label>
                            <input type="number" name="price" value="{{ job.Price }}" step="0.01" required
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Notes</label>
                            <textarea name="notes" rows="3"
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">{{ job.Notes }}</textarea>
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/schedule" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200">Save Changes</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, job=job, employees=employees)

@admin_bp.route('/employee/<employee_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_employee(employee_id):
    """Edit employee - INCLUDING username and password"""
    db = get_db()
    if not db:
        return redirect('/admin-login')

    employees = db.get_all_employees()
    employee = next((e for e in employees if e['ID'] == employee_id), None)
    
    if not employee:
        flash('Employee not found', 'error')
        return redirect('/admin/employees')
    
    if request.method == 'POST':
        # Update employee directly in sheets
        for idx, emp in enumerate(employees, start=2):
            if emp['ID'] == employee_id:
                db.employees.update_cell(idx, 2, request.form.get('name'))  # Name
                db.employees.update_cell(idx, 3, request.form.get('email'))  # Email
                db.employees.update_cell(idx, 4, request.form.get('phone'))  # Phone
                db.employees.update_cell(idx, 5, request.form.get('username'))  # Username
                db.employees.update_cell(idx, 8, request.form.get('active'))  # Active
                db.employees.update_cell(idx, 9, request.form.get('hourly_rate'))  # Hourly_Rate
                
                # Handle password change if provided
                new_password = request.form.get('new_password')
                if new_password:
                    password_hash = db.hash_password(new_password)
                    db.employees.update_cell(idx, 6, password_hash)  # Password_Hash
                break
        
        flash('Employee updated successfully!', 'success')
        return redirect('/admin/employees')
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Employee</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">✏️ Edit Employee: {{ employee.Name }}</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                    <p class="text-sm text-yellow-800">⚠️ Leave password field blank to keep current password</p>
                </div>
                
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Status</label>
                            <select name="active" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="yes" {% if employee.Active == 'yes' %}selected{% endif %}>Active</option>
                                <option value="no" {% if employee.Active == 'no' %}selected{% endif %}>Inactive</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Name</label>
                            <input type="text" name="name" value="{{ employee.Name }}" required
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" name="email" value="{{ employee.Email }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Phone</label>
                                <input type="tel" name="phone" value="{{ employee.Phone }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Username</label>
                                <input type="text" name="username" value="{{ employee.Username }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">New Password (leave blank to keep current)</label>
                                <input type="password" name="new_password" placeholder="Enter new password"
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Hourly Rate</label>
                            <input type="number" name="hourly_rate" value="{{ employee.Hourly_Rate }}" step="0.50" required
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/employees" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200">Save Changes</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, employee=employee)

@admin_bp.route('/quote/<quote_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quote(quote_id):
    """Edit quote - including price adjustment"""
    db = get_db()
    if not db:
        return redirect('/admin-login')

    quotes = db.get_all_quotes()
    quote = next((q for q in quotes if q['ID'] == quote_id), None)
    
    if not quote:
        flash('Quote not found', 'error')
        return redirect('/admin/quotes')
    
    if request.method == 'POST':
        # Update quote directly in sheets
        for idx, q in enumerate(quotes, start=2):
            if q['ID'] == quote_id:
                db.quotes.update_cell(idx, 2, request.form.get('name'))  # Name
                db.quotes.update_cell(idx, 3, request.form.get('email'))  # Email
                db.quotes.update_cell(idx, 4, request.form.get('phone'))  # Phone
                db.quotes.update_cell(idx, 5, request.form.get('property_type'))  # Property_Type
                db.quotes.update_cell(idx, 6, request.form.get('square_feet'))  # Square_Feet
                db.quotes.update_cell(idx, 7, request.form.get('service_type'))  # Service_Type
                db.quotes.update_cell(idx, 8, request.form.get('price'))  # Calculated_Price
                db.quotes.update_cell(idx, 10, request.form.get('status'))  # Status
                db.quotes.update_cell(idx, 13, request.form.get('notes'))  # Notes
                break
        
        flash(f'Quote updated successfully! New price: ${request.form.get("price")}', 'success')
        return redirect('/admin/quotes')
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Quote</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">✏️ Edit Quote</h1>
            </div>
        </nav>

        <div class="container mx-auto mt-8 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
                <form method="POST">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Status</label>
                            <select name="status" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                <option value="pending" {% if quote.Status == 'pending' %}selected{% endif %}>Pending</option>
                                <option value="contacted" {% if quote.Status == 'contacted' %}selected{% endif %}>Contacted</option>
                                <option value="converted" {% if quote.Status == 'converted' %}selected{% endif %}>Converted</option>
                                <option value="lost" {% if quote.Status == 'lost' %}selected{% endif %}>Lost</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Name</label>
                            <input type="text" name="name" value="{{ quote.Name }}" required
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Email</label>
                                <input type="email" name="email" value="{{ quote.Email }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Phone</label>
                                <input type="tel" name="phone" value="{{ quote.Phone }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Property Type</label>
                                <select name="property_type" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="office" {% if quote.Property_Type == 'office' %}selected{% endif %}>Office</option>
                                    <option value="retail" {% if quote.Property_Type == 'retail' %}selected{% endif %}>Retail</option>
                                    <option value="medical" {% if quote.Property_Type == 'medical' %}selected{% endif %}>Medical</option>
                                    <option value="restaurant" {% if quote.Property_Type == 'restaurant' %}selected{% endif %}>Restaurant</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Square Feet</label>
                                <input type="number" name="square_feet" value="{{ quote.Square_Feet }}" required
                                    class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Service Type</label>
                                <select name="service_type" class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">
                                    <option value="weekly" {% if quote.Service_Type == 'weekly' %}selected{% endif %}>Weekly</option>
                                    <option value="biweekly" {% if quote.Service_Type == 'biweekly' %}selected{% endif %}>Bi-Weekly</option>
                                    <option value="monthly" {% if quote.Service_Type == 'monthly' %}selected{% endif %}>Monthly</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">💰 Quote Price (Fully Editable!)</label>
                            <input type="number" name="price" value="{{ quote.Calculated_Price }}" step="0.01" required
                                class="mt-1 block w-full border border-yellow-300 rounded-lg shadow-sm p-2 bg-yellow-50 text-xl font-bold">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Notes</label>
                            <textarea name="notes" rows="3"
                                class="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-2">{{ quote.Notes }}</textarea>
                        </div>
                        
                        <div class="flex justify-between pt-4">
                            <a href="/admin/quotes" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors duration-200">Cancel</a>
                            <button type="submit" class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200">Save Changes</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(template, quote=quote)
