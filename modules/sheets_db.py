"""
Google Sheets Database Module
Handles all database operations using Google Sheets as backend
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import hashlib
import re
import os
import time
from functools import lru_cache

class SheetsDatabase:
    def __init__(self, credentials_file='credentials.json', spreadsheet_name='Cleaning_Business_Database'):
        """Initialize connection to Google Sheets with caching and rate limiting"""
        
        # Caching mechanism
        self._cache = {}
        self._cache_time = {}
        self.CACHE_DURATION = 60  # Cache for 60 seconds
        
        # Rate limiting
        self._last_request_time = 0
        self._request_delay = 1.5  # Increased delay between requests
        self._request_count = 0
        self._request_window_start = time.time()
        
        # Setup credentials and scope
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Authenticate
        self.creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        self.client = gspread.authorize(self.creds)
        
        # Open spreadsheet
        try:
            self.spreadsheet = self.client.open(spreadsheet_name)
            print(f"Connected to spreadsheet: {spreadsheet_name}")
        except Exception as e:
            print(f"Error opening spreadsheet: {e}")
            print(f"Creating new spreadsheet: {spreadsheet_name}")
            self.spreadsheet = self.client.create(spreadsheet_name)
        
        # Initialize sheets
        self._initialize_sheets()
    
    def _rate_limit(self):
        """Smart rate limiting - only when necessary"""
        current_time = time.time()
        
        # Option 1: MINIMAL RATE LIMITING (Recommended)
        # Only add delay if we're making rapid consecutive requests
        if self._request_count > 10:  # Only rate limit after 10 rapid requests
            time.sleep(0.05)  # Just 50ms delay instead of 1.1 seconds
        
        self._request_count += 1
        
        # Reset counter every 10 seconds (not every minute)
        if current_time - self._request_window_start > 10:
            self._request_count = 0
            self._request_window_start = current_time
    
    def _get_from_cache(self, key):
        """Get data from cache if still valid"""
        if key in self._cache and key in self._cache_time:
            age = (datetime.now() - self._cache_time[key]).seconds
            if age < self.CACHE_DURATION:
                return self._cache[key]
        return None
    
    def _set_cache(self, key, value):
        """Store data in cache"""
        self._cache[key] = value
        self._cache_time[key] = datetime.now()
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache = {}
        self._cache_time = {}
        print("Cache cleared")

    def _initialize_sheets(self):
        """Initialize all required sheets"""
        required_sheets = {
            'Customers': ['ID', 'Name', 'Email', 'Phone', 'Address', 'Business_Type',
                         'Square_Feet', 'Service_Frequency', 'Added_Date', 'Status',
                         'Special_Instructions', 'Preferred_Day', 'Preferred_Time'],
            'Jobs': ['ID', 'Customer_Name', 'Date', 'Time', 'Employee', 'Address',
                    'Service_Type', 'Price', 'Status', 'Completed', 'Notes',
                    'Check_In_Time', 'Check_Out_Time', 'Photos'],
            'Employees': ['ID', 'Name', 'Email', 'Phone', 'Username', 'Password_Hash',
                         'Hire_Date', 'Active', 'Hourly_Rate', 'Color_Code'],
            'Quotes': ['ID', 'Name', 'Email', 'Phone', 'Property_Type', 'Square_Feet',
                      'Service_Type', 'Calculated_Price', 'Date_Requested', 'Status',
                      'Converted', 'Follow_Up_Date', 'Notes'],
            'Payments': ['ID', 'Customer_Name', 'Amount', 'Date', 'Method',
                        'Invoice_Number', 'Status', 'Job_IDs', 'Notes'],
            'Settings': ['Key', 'Value', 'Category', 'Updated_Date']
        }

        # Create sheets if they don't exist
        existing_sheets = [sheet.title for sheet in self.spreadsheet.worksheets()]

        for sheet_name, headers in required_sheets.items():
            if sheet_name not in existing_sheets:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)
                worksheet.append_row(headers)
                print(f"Created sheet: {sheet_name}")
            else:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                if not worksheet.row_values(1):
                    worksheet.append_row(headers)

        # Store references
        self.customers = self.spreadsheet.worksheet('Customers')
        self.jobs = self.spreadsheet.worksheet('Jobs')
        self.employees = self.spreadsheet.worksheet('Employees')
        self.quotes = self.spreadsheet.worksheet('Quotes')
        self.payments = self.spreadsheet.worksheet('Payments')
        self.settings = self.spreadsheet.worksheet('Settings')

    # ========== AUTHENTICATION ==========

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_admin(self, username, password):
        """Verify admin credentials"""
        from config import Config
        return username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD

    def verify_employee(self, username, password):
        """Verify employee credentials"""
        self._rate_limit()
        employees = self.employees.get_all_records()
        password_hash = self.hash_password(password)

        for emp in employees:
            if emp['Username'] == username and emp['Password_Hash'] == password_hash:
                if emp['Active'] == 'yes':
                    return emp
        return None

    def verify_customer(self, email):
        """Verify customer by email"""
        self._rate_limit()
        customers = self.customers.get_all_records()
        for customer in customers:
            if customer['Email'].lower() == email.lower():
                if customer['Status'] == 'active':
                    return customer
        return None

    # ========== CUSTOMER OPERATIONS ==========

    def add_customer(self, name, email, phone, address, business_type='office',
                    square_feet=1000, service_frequency='weekly', special_instructions=''):
        """Add new customer"""
        self._rate_limit()
        
        # Check if customer exists
        existing = self.get_customer_by_email(email)
        if existing:
            return existing['ID']

        customer_id = f"CUST{datetime.now().strftime('%Y%m%d%H%M%S')}"
        row = [
            customer_id, name, email, phone, address, business_type,
            square_feet, service_frequency, datetime.now().isoformat(),
            'active', special_instructions, '', ''
        ]
        self.customers.append_row(row)
        return customer_id

    def get_all_customers(self):
        """Get all customers"""
        self._rate_limit()
        try:
            return self.customers.get_all_records()
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []

    def get_customer_by_email(self, email):
        """Get customer by email"""
        customers = self.get_all_customers()
        for customer in customers:
            if customer['Email'].lower() == email.lower():
                return customer
        return None

    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        customers = self.get_all_customers()
        for customer in customers:
            if customer['ID'] == customer_id:
                return customer
        return None

    def update_customer_status(self, customer_id, status):
        """Update customer status"""
        self._rate_limit()
        customers = self.customers.get_all_records()
        for idx, customer in enumerate(customers, start=2):
            if customer['ID'] == customer_id:
                self.customers.update_cell(idx, 10, status)  # Status column
                return True
        return False

    # ========== JOB OPERATIONS ==========

    def add_job(self, customer_name, date, time, employee, address, service_type, price):
        """Add a new job"""
        try:
            # Ensure date is in consistent format (YYYY-MM-DD)
            if isinstance(date, str) and '/' in date:
                # Convert MM/DD/YYYY to YYYY-MM-DD
                parts = date.split('/')
                if len(parts) == 3:
                    date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            
            job_id = self.generate_id('JOB')
            self.jobs.append_row([
                job_id,
                customer_name,
                date,  # This should now be in YYYY-MM-DD format
                time,
                employee,
                address,
                service_type,
                'scheduled',
                'no',
                price
            ])
            return job_id
        except Exception as e:
            print(f"Error adding job: {e}")
            return None

    def get_all_jobs(self):
        """Get all jobs"""
        self._rate_limit()
        try:
            return self.jobs.get_all_records()
        except Exception as e:
            print(f"Error getting jobs: {e}")
            return []

    def get_jobs_for_date(self, date):
        """Get jobs for a specific date"""
        try:
            # Use cache if available
            cache_key = f"jobs_{date}"
            if cache_key in self._cache:
                if (datetime.now() - self._cache_time[cache_key]).seconds < self.CACHE_DURATION:
                    return self._cache[cache_key]
            
            # Rate limit before request
            self._rate_limit()
            
            all_jobs = self.get_all_jobs()
            
            # Normalize date format for comparison
            if isinstance(date, str):
                # Ensure date is in YYYY-MM-DD format
                if '/' in date:
                    # Convert MM/DD/YYYY to YYYY-MM-DD
                    parts = date.split('/')
                    date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            
            # Filter jobs for the specific date
            jobs_for_date = []
            for job in all_jobs:
                job_date = job.get('Date', '')
                
                # Normalize job date if needed
                if '/' in job_date:
                    parts = job_date.split('/')
                    job_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                
                if job_date == date:
                    jobs_for_date.append(job)
            
            # Cache the result
            self._cache[cache_key] = jobs_for_date
            self._cache_time[cache_key] = datetime.now()
            
            print(f"Found {len(jobs_for_date)} jobs for date {date}")
            return jobs_for_date
            
        except Exception as e:
            print(f"Error getting jobs for date {date}: {e}")
            return []

    def get_employee_jobs(self, employee_name, date=None):
        """Get jobs for specific employee"""
        all_jobs = self.get_all_jobs()
        jobs = [job for job in all_jobs if job['Employee'] == employee_name]

        if date:
            jobs = [job for job in jobs if job['Date'] == date]

        return sorted(jobs, key=lambda x: (x['Date'], x['Time']))

    def get_customer_jobs(self, customer_name):
        """Get jobs for specific customer"""
        all_jobs = self.get_all_jobs()
        return [job for job in all_jobs if job['Customer_Name'] == customer_name]

    def update_job_status(self, job_id, status, completed='no'):
        """Update job status"""
        self._rate_limit()
        jobs = self.jobs.get_all_records()
        for idx, job in enumerate(jobs, start=2):
            if job['ID'] == job_id:
                self.jobs.update_cell(idx, 9, status)  # Status column
                self.jobs.update_cell(idx, 10, completed)  # Completed column
                return True
        return False

    def complete_job(self, job_id, check_out_time=None, notes=''):
        """Mark job as completed"""
        self._rate_limit()
        if not check_out_time:
            check_out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        jobs = self.jobs.get_all_records()
        for idx, job in enumerate(jobs, start=2):
            if job['ID'] == job_id:
                self.jobs.update_cell(idx, 9, 'completed')  # Status
                self.jobs.update_cell(idx, 10, 'yes')  # Completed
                self.jobs.update_cell(idx, 13, check_out_time)  # Check_Out_Time
                if notes:
                    self.jobs.update_cell(idx, 11, notes)  # Notes
                return True
        return False

    # ========== EMPLOYEE OPERATIONS ==========

    def add_employee(self, name, email, phone, username, password,
                    hourly_rate=20, color_code='#3498db'):
        """Add new employee"""
        self._rate_limit()
        employee_id = f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        password_hash = self.hash_password(password)

        row = [
            employee_id, name, email, phone, username, password_hash,
            datetime.now().strftime('%Y-%m-%d'), 'yes', hourly_rate, color_code
        ]
        self.employees.append_row(row)
        return employee_id

    def get_all_employees(self):
        """Get all employees"""
        self._rate_limit()
        try:
            return self.employees.get_all_records()
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []

    def get_active_employees(self):
        """Get active employees only"""
        employees = self.get_all_employees()
        return [emp for emp in employees if emp['Active'] == 'yes']

    def update_employee_status(self, employee_id, active):
        """Update employee active status"""
        self._rate_limit()
        employees = self.employees.get_all_records()
        for idx, emp in enumerate(employees, start=2):
            if emp['ID'] == employee_id:
                self.employees.update_cell(idx, 8, 'yes' if active else 'no')
                return True
        return False

    # ========== QUOTE OPERATIONS ==========

    def add_quote(self, name, email, phone, property_type, square_feet,
                 service_type, calculated_price):
        """Add new quote"""
        self._rate_limit()
        quote_id = f"QUOTE{datetime.now().strftime('%Y%m%d%H%M%S')}"
        row = [
            quote_id, name, email, phone, property_type, square_feet,
            service_type, calculated_price, datetime.now().isoformat(),
            'pending', 'no', '', ''
        ]
        self.quotes.append_row(row)
        return quote_id

    def get_all_quotes(self):
        """Get all quotes"""
        self._rate_limit()
        try:
            return self.quotes.get_all_records()
        except Exception as e:
            print(f"Error getting quotes: {e}")
            return []

    def get_pending_quotes(self):
        """Get pending quotes"""
        quotes = self.get_all_quotes()
        return [q for q in quotes if q['Status'] == 'pending']

    def convert_quote(self, quote_id):
        """Convert quote to customer"""
        self._rate_limit()
        quotes = self.quotes.get_all_records()
        for idx, quote in enumerate(quotes, start=2):
            if quote['ID'] == quote_id:
                self.quotes.update_cell(idx, 10, 'converted')  # Status
                self.quotes.update_cell(idx, 11, 'yes')  # Converted

                # Add as customer
                customer_id = self.add_customer(
                    quote['Name'], quote['Email'], quote['Phone'],
                    '', quote['Property_Type'], quote['Square_Feet'],
                    quote['Service_Type']
                )
                return customer_id
        return None

    # ========== PAYMENT OPERATIONS ==========

    def add_payment(self, customer_name, amount, method='card', job_ids='', notes=''):
        """Add payment record"""
        self._rate_limit()
        payment_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}"
        invoice_number = f"INV{datetime.now().strftime('%Y%m%d')}{payment_id[-4:]}"

        row = [
            payment_id, customer_name, amount, datetime.now().isoformat(),
            method, invoice_number, 'completed', job_ids, notes
        ]
        self.payments.append_row(row)
        return payment_id

    def get_all_payments(self):
        """Get all payments"""
        self._rate_limit()
        try:
            return self.payments.get_all_records()
        except Exception as e:
            print(f"Error getting payments: {e}")
            return []

    def get_customer_payments(self, customer_name):
        """Get payments for specific customer"""
        payments = self.get_all_payments()
        return [p for p in payments if p['Customer_Name'] == customer_name]

    # ========== DASHBOARD STATS ==========

    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        try:
            jobs = self.get_all_jobs()
            customers = self.get_all_customers()
            payments = self.get_all_payments()
            quotes = self.get_pending_quotes()
            employees = self.get_active_employees()

            # Today's date
            today = datetime.now().strftime('%Y-%m-%d')

            # Calculate stats
            todays_jobs = [j for j in jobs if j['Date'] == today]
            completed_today = len([j for j in todays_jobs if j['Completed'] == 'yes'])

            # Revenue calculation
            revenue_today = 0
            revenue_month = 0
            current_month = datetime.now().strftime('%Y-%m')

            for payment in payments:
                try:
                    amount = float(payment['Amount'])
                    payment_date = payment['Date'].split('T')[0] if 'T' in payment['Date'] else payment['Date']

                    if payment_date == today:
                        revenue_today += amount
                    if payment_date.startswith(current_month):
                        revenue_month += amount
                except:
                    pass

            return {
                'total_customers': len([c for c in customers if c['Status'] == 'active']),
                'jobs_today': len(todays_jobs),
                'completed_today': completed_today,
                'pending_quotes': len(quotes),
                'revenue_today': revenue_today,
                'revenue_month': revenue_month,
                'active_employees': len(employees),
                'upcoming_jobs': len([j for j in jobs if j['Date'] >= today and j['Status'] == 'scheduled'])
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_customers': 0,
                'jobs_today': 0,
                'completed_today': 0,
                'pending_quotes': 0,
                'revenue_today': 0,
                'revenue_month': 0,
                'active_employees': 0,
                'upcoming_jobs': 0
            }

    # ========== ADDITIONAL METHODS ==========
    
    def get_recent_jobs(self, limit=10):
        """Get recent jobs sorted by date"""
        try:
            jobs = self.get_all_jobs()
            
            # Sort by date descending
            sorted_jobs = sorted(
                jobs, 
                key=lambda x: x.get('Date', ''), 
                reverse=True
            )
            
            return sorted_jobs[:limit]
        except Exception as e:
            print(f"Error getting recent jobs: {e}")
            return []