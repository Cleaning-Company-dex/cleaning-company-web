# modules/sheets_db.py

import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import json

class SheetsDatabase:
    def __init__(self):
        """Initialize Google Sheets connection"""
        try:
            # Setup Google Sheets credentials
            scopes = ['https://www.googleapis.com/auth/spreadsheets',
                     'https://www.googleapis.com/auth/drive']

            # Use service account credentials (you'll need to set this up)
            creds = Credentials.from_service_account_file(
                'credentials.json',  # Path to your service account JSON file
                scopes=scopes
            )

            self.client = gspread.authorize(creds)

            # Open the spreadsheet (replace with your spreadsheet ID or name)
            self.spreadsheet = self.client.open('Baez Cleaning Database')

            # Initialize sheets
            self.init_sheets()

        except Exception as e:
            print(f"Error initializing Google Sheets: {e}")
            self.spreadsheet = None

    def init_sheets(self):
        """Initialize required sheets if they don't exist"""
        try:
            # Get or create Quotes sheet
            try:
                self.quotes_sheet = self.spreadsheet.worksheet('Quotes')
            except:
                # Create Quotes sheet with proper headers
                self.quotes_sheet = self.spreadsheet.add_worksheet(
                    title='Quotes',
                    rows=1000,
                    cols=40
                )

                # Add headers matching Google Apps Script structure
                headers = [
                    'ID', 'Date_Created', 'Customer_Name', 'Customer_Email', 'Customer_Phone',
                    'Customer_Address', 'Customer_City', 'Customer_State', 'Customer_Zip',
                    'Properties', 'Materials', 'Services', 'Employees', 'Labor_Hours',
                    'Labor_Cost', 'Material_Cost', 'Service_Cost', 'Travel_Cost',
                    'Base_Cost', 'Profit_Margin', 'Profit_Amount', 'Subtotal',
                    'Tax_Amount', 'Total_Amount', 'Status', 'Valid_Until', 'Notes',
                    'Internal_Notes', 'Created_By', 'Assigned_To', 'Follow_Up_Date',
                    'Customer_ID', 'Converted_Date', 'Decline_Reason', 'Service_Type',
                    'Frequency', 'Mileage'
                ]
                self.quotes_sheet.append_row(headers)

                # Format headers
                self.quotes_sheet.format('A1:AK1', {
                    'backgroundColor': {'red': 0.17, 'green': 0.24, 'blue': 0.31},
                    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                })

            # Get or create other sheets
            self.init_other_sheets()

        except Exception as e:
            print(f"Error initializing sheets: {e}")

    def init_other_sheets(self):
        """Initialize other required sheets"""
        # Initialize Customers sheet
        try:
            self.customers_sheet = self.spreadsheet.worksheet('Customers')
        except:
            self.customers_sheet = self.spreadsheet.add_worksheet(
                title='Customers',
                rows=1000,
                cols=20
            )
            headers = ['ID', 'Name', 'Email', 'Phone', 'Address', 'City', 'State',
                      'Zip', 'Status', 'Created_Date', 'Type', 'Business_Name',
                      'Frequency', 'Contract_Start', 'Contract_End', 'Price_Range',
                      'Notes', 'Source', 'Assigned_Rep', 'Last_Service']
            self.customers_sheet.append_row(headers)
            self.customers_sheet.format('A1:T1', {
                'backgroundColor': {'red': 0.2, 'green': 0.3, 'blue': 0.5},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })

        # Initialize Employees sheet
        try:
            self.employees_sheet = self.spreadsheet.worksheet('Employees')
        except:
            self.employees_sheet = self.spreadsheet.add_worksheet(
                title='Employees',
                rows=100,
                cols=20
            )
            headers = ['ID', 'Name', 'Email', 'Phone', 'Username', 'Password',
                      'Role', 'Hourly_Rate', 'Active', 'Start_Date', 'Address',
                      'City', 'State', 'Zip', 'Emergency_Contact', 'Emergency_Phone',
                      'Skills', 'Certifications', 'Notes', 'Last_Login']
            self.employees_sheet.append_row(headers)
            self.employees_sheet.format('A1:T1', {
                'backgroundColor': {'red': 0.1, 'green': 0.4, 'blue': 0.3},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })

        # Initialize Materials_Services sheet
        try:
            self.materials_sheet = self.spreadsheet.worksheet('Materials_Services')
        except:
            self.materials_sheet = self.spreadsheet.add_worksheet(
                title='Materials_Services',
                rows=500,
                cols=15
            )
            headers = ['ID', 'Type', 'Category', 'Name', 'Description', 'Unit_Type',
                      'Cost', 'Price', 'Active', 'Last_Updated', 'Created_By',
                      'Supplier', 'SKU', 'Min_Stock', 'Current_Stock']
            self.materials_sheet.append_row(headers)
            self.materials_sheet.format('A1:O1', {
                'backgroundColor': {'red': 0.3, 'green': 0.2, 'blue': 0.4},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })

        # Initialize Jobs sheet
        try:
            self.jobs_sheet = self.spreadsheet.worksheet('Jobs')
        except:
            self.jobs_sheet = self.spreadsheet.add_worksheet(
                title='Jobs',
                rows=2000,
                cols=25
            )
            headers = ['ID', 'Customer_ID', 'Customer_Name', 'Property_Address', 'Date',
                      'Time', 'Duration', 'Employees', 'Status', 'Type', 'Frequency',
                      'Total_Price', 'Labor_Cost', 'Material_Cost', 'Profit',
                      'Payment_Status', 'Payment_Method', 'Invoice_ID', 'Notes',
                      'Completed_Time', 'Created_Date', 'Created_By', 'Modified_Date',
                      'Modified_By', 'Rating']
            self.jobs_sheet.append_row(headers)

    def add_quote_full(self, quote_data):
        """Add a complete quote with all fields to Google Sheets

        Args:
            quote_data: List containing all quote fields in the correct order

        Returns:
            Dictionary with success status and quote ID
        """
        try:
            if not self.quotes_sheet:
                return {'success': False, 'error': 'Sheets not initialized'}

            # Ensure all data is properly formatted for Google Sheets
            formatted_data = []
            for item in quote_data:
                if isinstance(item, (dict, list)):
                    formatted_data.append(json.dumps(item))
                elif isinstance(item, datetime):
                    formatted_data.append(item.isoformat())
                elif item is None:
                    formatted_data.append('')
                else:
                    formatted_data.append(str(item))

            # Append the quote data
            self.quotes_sheet.append_row(formatted_data)

            # Log the action
            self.log_activity('Quote Created', f"New quote {formatted_data[0]} created via web form")

            return {
                'success': True,
                'quote_id': formatted_data[0]  # First element is the ID
            }

        except Exception as e:
            print(f"Error adding quote: {e}")
            return {'success': False, 'error': str(e)}

    def add_quote(self, name, email, phone, property_type, sqft, frequency, price):
        """Legacy method for simple quote addition"""
        try:
            # Generate quote ID
            quote_id = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Create minimal quote data
            properties = [{
                'type': property_type,
                'sqft': sqft
            }]

            # Prepare the row data in the correct order
            quote_data = [
                quote_id,                           # ID
                datetime.now().isoformat(),         # Date_Created
                name,                               # Customer_Name
                email,                              # Customer_Email
                phone,                              # Customer_Phone
                '',                                 # Customer_Address
                '',                                 # Customer_City
                '',                                 # Customer_State
                '',                                 # Customer_Zip
                json.dumps(properties),             # Properties
                '[]',                               # Materials
                '[]',                               # Services
                '[]',                               # Employees
                0,                                  # Labor_Hours
                0,                                  # Labor_Cost
                0,                                  # Material_Cost
                0,                                  # Service_Cost
                0,                                  # Travel_Cost
                price * 0.65,                       # Base_Cost (estimate)
                35,                                 # Profit_Margin
                price * 0.35,                       # Profit_Amount (estimate)
                price / 1.0625,                     # Subtotal (estimate)
                price * 0.0625,                     # Tax_Amount (estimate)
                price,                              # Total_Amount
                'pending',                          # Status
                '',                                 # Valid_Until
                '',                                 # Notes
                f'Web quote: {property_type}',     # Internal_Notes
                'Web Form',                         # Created_By
                '',                                 # Assigned_To
                '',                                 # Follow_Up_Date
                '',                                 # Customer_ID
                '',                                 # Converted_Date
                '',                                 # Decline_Reason
                'regular',                          # Service_Type
                frequency,                          # Frequency
                0                                   # Mileage
            ]

            return self.add_quote_full(quote_data)

        except Exception as e:
            print(f"Error in add_quote: {e}")
            return {'success': False, 'error': str(e)}

    def get_quotes(self, status=None):
        """Retrieve quotes from Google Sheets

        Args:
            status: Optional status filter ('pending', 'sent', 'accepted', 'declined')

        Returns:
            List of quote dictionaries
        """
        try:
            if not self.quotes_sheet:
                return []

            # Get all data
            data = self.quotes_sheet.get_all_records()

            # Filter by status if provided
            if status:
                data = [q for q in data if q.get('Status') == status]

            # Sort by date (newest first)
            data.sort(key=lambda x: x.get('Date_Created', ''), reverse=True)

            return data

        except Exception as e:
            print(f"Error getting quotes: {e}")
            return []

    def update_quote_status(self, quote_id, new_status):
        """Update the status of a quote

        Args:
            quote_id: The quote ID to update
            new_status: New status value

        Returns:
            Success dictionary
        """
        try:
            if not self.quotes_sheet:
                return {'success': False, 'error': 'Sheets not initialized'}

            # Find the quote
            data = self.quotes_sheet.get_all_values()
            headers = data[0]

            for i, row in enumerate(data[1:], start=2):
                if row[0] == quote_id:  # ID is in first column
                    status_col = headers.index('Status') + 1
                    self.quotes_sheet.update_cell(i, status_col, new_status)

                    # If accepted, update converted date
                    if new_status == 'accepted':
                        converted_col = headers.index('Converted_Date') + 1
                        self.quotes_sheet.update_cell(i, converted_col, datetime.now().isoformat())

                    self.log_activity('Quote Updated', f"Quote {quote_id} status changed to {new_status}")
                    return {'success': True}

            return {'success': False, 'error': 'Quote not found'}

        except Exception as e:
            print(f"Error updating quote status: {e}")
            return {'success': False, 'error': str(e)}

    def get_quote_by_id(self, quote_id):
        """Get a specific quote by ID

        Args:
            quote_id: The quote ID to retrieve

        Returns:
            Quote dictionary or None
        """
        try:
            quotes = self.get_quotes()
            for quote in quotes:
                if quote.get('ID') == quote_id:
                    return quote
            return None
        except Exception as e:
            print(f"Error getting quote by ID: {e}")
            return None

    def verify_admin(self, username, password):
        """Verify admin credentials

        Args:
            username: Admin username
            password: Admin password

        Returns:
            Boolean indicating if credentials are valid
        """
        # For development, you can use hardcoded credentials
        # In production, store these securely or check against the Employees sheet
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

        # First check hardcoded admin
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return True

        # Then check employee sheet for admin role
        try:
            if self.employees_sheet:
                employees = self.employees_sheet.get_all_records()
                for emp in employees:
                    if (emp.get('Username') == username and
                        emp.get('Password') == password and
                        emp.get('Role') == 'Admin' and
                        emp.get('Active') == 'yes'):
                        return True
        except Exception as e:
            print(f"Error checking admin in employees: {e}")

        return False

    def verify_employee(self, username, password):
        """Verify employee credentials

        Args:
            username: Employee username
            password: Employee password

        Returns:
            Employee data dictionary if valid, None otherwise
        """
        try:
            if not self.employees_sheet:
                return None

            employees = self.employees_sheet.get_all_records()

            for employee in employees:
                if (employee.get('Username') == username and
                    employee.get('Password') == password and
                    employee.get('Active') == 'yes'):

                    # Update last login
                    self.update_employee_last_login(employee.get('ID'))
                    return employee

            return None

        except Exception as e:
            print(f"Error verifying employee: {e}")
            return None

    def update_employee_last_login(self, employee_id):
        """Update the last login time for an employee

        Args:
            employee_id: The employee ID
        """
        try:
            if not self.employees_sheet:
                return

            data = self.employees_sheet.get_all_values()
            headers = data[0]

            for i, row in enumerate(data[1:], start=2):
                if row[0] == employee_id:
                    if 'Last_Login' in headers:
                        col = headers.index('Last_Login') + 1
                        self.employees_sheet.update_cell(i, col, datetime.now().isoformat())
                    break
        except Exception as e:
            print(f"Error updating last login: {e}")

    def get_customers(self):
        """Get all customers from the database

        Returns:
            List of customer dictionaries
        """
        try:
            if not self.customers_sheet:
                return []

            customers = self.customers_sheet.get_all_records()

            # Filter for active customers only
            active_customers = [c for c in customers if c.get('Status') == 'active']

            return active_customers

        except Exception as e:
            print(f"Error getting customers: {e}")
            return []

    def add_customer(self, customer_data):
        """Add a new customer to the database

        Args:
            customer_data: Dictionary containing customer information

        Returns:
            Success dictionary with customer ID
        """
        try:
            if not self.customers_sheet:
                return {'success': False, 'error': 'Sheets not initialized'}

            # Generate customer ID
            customer_id = f"C{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Prepare row data
            row = [
                customer_id,
                customer_data.get('name', ''),
                customer_data.get('email', ''),
                customer_data.get('phone', ''),
                customer_data.get('address', ''),
                customer_data.get('city', ''),
                customer_data.get('state', ''),
                customer_data.get('zip', ''),
                'active',
                datetime.now().isoformat(),
                customer_data.get('type', 'commercial'),
                customer_data.get('business_name', ''),
                customer_data.get('frequency', 'monthly'),
                customer_data.get('contract_start', ''),
                customer_data.get('contract_end', ''),
                customer_data.get('price_range', ''),
                customer_data.get('notes', ''),
                customer_data.get('source', 'Web Quote'),
                customer_data.get('assigned_rep', ''),
                ''  # Last service date
            ]

            self.customers_sheet.append_row(row)

            self.log_activity('Customer Added', f"New customer {customer_data.get('name')} added")

            return {'success': True, 'customer_id': customer_id}

        except Exception as e:
            print(f"Error adding customer: {e}")
            return {'success': False, 'error': str(e)}

    def get_jobs(self, employee_id=None, status=None):
        """Get jobs from the database

        Args:
            employee_id: Optional filter by employee
            status: Optional filter by status

        Returns:
            List of job dictionaries
        """
        try:
            if not self.jobs_sheet:
                return []

            jobs = self.jobs_sheet.get_all_records()

            # Apply filters
            if employee_id:
                jobs = [j for j in jobs if employee_id in j.get('Employees', '')]

            if status:
                jobs = [j for j in jobs if j.get('Status') == status]

            # Sort by date (newest first)
            jobs.sort(key=lambda x: x.get('Date', ''), reverse=True)

            return jobs

        except Exception as e:
            print(f"Error getting jobs: {e}")
            return []

    def add_job(self, job_data):
        """Add a new job to the database

        Args:
            job_data: Dictionary containing job information

        Returns:
            Success dictionary with job ID
        """
        try:
            if not self.jobs_sheet:
                return {'success': False, 'error': 'Sheets not initialized'}

            # Generate job ID
            job_id = f"J{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Prepare row data
            row = [
                job_id,
                job_data.get('customer_id', ''),
                job_data.get('customer_name', ''),
                job_data.get('property_address', ''),
                job_data.get('date', datetime.now().date().isoformat()),
                job_data.get('time', ''),
                job_data.get('duration', ''),
                json.dumps(job_data.get('employees', [])),
                job_data.get('status', 'scheduled'),
                job_data.get('type', 'regular'),
                job_data.get('frequency', ''),
                job_data.get('total_price', 0),
                job_data.get('labor_cost', 0),
                job_data.get('material_cost', 0),
                job_data.get('profit', 0),
                job_data.get('payment_status', 'pending'),
                job_data.get('payment_method', ''),
                job_data.get('invoice_id', ''),
                job_data.get('notes', ''),
                '',  # Completed time
                datetime.now().isoformat(),  # Created date
                job_data.get('created_by', 'System'),
                '',  # Modified date
                '',  # Modified by
                ''   # Rating
            ]

            self.jobs_sheet.append_row(row)

            self.log_activity('Job Created', f"New job {job_id} scheduled for {job_data.get('customer_name')}")

            return {'success': True, 'job_id': job_id}

        except Exception as e:
            print(f"Error adding job: {e}")
            return {'success': False, 'error': str(e)}

    def get_employees(self):
        """Get all employees from the database

        Returns:
            List of employee dictionaries
        """
        try:
            if not self.employees_sheet:
                return []

            employees = self.employees_sheet.get_all_records()

            # Return only active employees
            active_employees = [e for e in employees if e.get('Active') == 'yes']

            return active_employees

        except Exception as e:
            print(f"Error getting employees: {e}")
            return []

    def add_employee(self, employee_data):
        """Add a new employee to the database

        Args:
            employee_data: Dictionary containing employee information

        Returns:
            Success dictionary with employee ID
        """
        try:
            if not self.employees_sheet:
                return {'success': False, 'error': 'Sheets not initialized'}

            # Generate employee ID
            employee_id = f"E{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Prepare row data
            row = [
                employee_id,
                employee_data.get('name', ''),
                employee_data.get('email', ''),
                employee_data.get('phone', ''),
                employee_data.get('username', ''),
                employee_data.get('password', ''),
                employee_data.get('role', 'Cleaner'),
                employee_data.get('hourly_rate', 15),
                'yes',  # Active
                datetime.now().date().isoformat(),  # Start date
                employee_data.get('address', ''),
                employee_data.get('city', ''),
                employee_data.get('state', ''),
                employee_data.get('zip', ''),
                employee_data.get('emergency_contact', ''),
                employee_data.get('emergency_phone', ''),
                employee_data.get('skills', ''),
                employee_data.get('certifications', ''),
                employee_data.get('notes', ''),
                ''  # Last login
            ]

            self.employees_sheet.append_row(row)

            self.log_activity('Employee Added', f"New employee {employee_data.get('name')} added")

            return {'success': True, 'employee_id': employee_id}

        except Exception as e:
            print(f"Error adding employee: {e}")
            return {'success': False, 'error': str(e)}

    def log_activity(self, action, description):
        """Log an activity to the activity log

        Args:
            action: Type of action performed
            description: Description of the activity
        """
        try:
            # Try to get or create Activity_Log sheet
            try:
                log_sheet = self.spreadsheet.worksheet('Activity_Log')
            except:
                log_sheet = self.spreadsheet.add_worksheet(
                    title='Activity_Log',
                    rows=5000,
                    cols=5
                )
                headers = ['Timestamp', 'Action', 'Description', 'User', 'IP_Address']
                log_sheet.append_row(headers)

            # Add log entry
            log_entry = [
                datetime.now().isoformat(),
                action,
                description,
                'System',  # In production, get actual user
                ''  # In production, get IP address
            ]

            log_sheet.append_row(log_entry)

        except Exception as e:
            print(f"Error logging activity: {e}")

    def get_dashboard_stats(self):
        """Get statistics for dashboard display

        Returns:
            Dictionary with various statistics
        """
        try:
            stats = {
                'total_quotes': 0,
                'pending_quotes': 0,
                'accepted_quotes': 0,
                'total_customers': 0,
                'active_jobs': 0,
                'completed_jobs': 0,
                'total_revenue': 0,
                'monthly_revenue': 0,
                'total_employees': 0,
                'active_employees': 0
            }

            # Get quotes stats
            if self.quotes_sheet:
                quotes = self.get_quotes()
                stats['total_quotes'] = len(quotes)
                stats['pending_quotes'] = len([q for q in quotes if q.get('Status') == 'pending'])
                stats['accepted_quotes'] = len([q for q in quotes if q.get('Status') == 'accepted'])

                # Calculate revenue from accepted quotes
                for quote in quotes:
                    if quote.get('Status') == 'accepted':
                        try:
                            stats['total_revenue'] += float(quote.get('Total_Amount', 0))
                        except:
                            pass

            # Get customer stats
            if self.customers_sheet:
                customers = self.get_customers()
                stats['total_customers'] = len(customers)

            # Get job stats
            if self.jobs_sheet:
                jobs = self.get_jobs()
                stats['active_jobs'] = len([j for j in jobs if j.get('Status') == 'scheduled'])
                stats['completed_jobs'] = len([j for j in jobs if j.get('Status') == 'completed'])

            # Get employee stats
            if self.employees_sheet:
                employees = self.get_employees()
                stats['total_employees'] = len(employees)
                stats['active_employees'] = len([e for e in employees if e.get('Active') == 'yes'])

            return stats

        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}

    # ADD THIS METHOD TO YOUR sheets_db.py file (add it after the __init__ method)

def add_quote_full(self, quote_data):
    """Add a complete quote with all 37 fields to Google Sheets
    This matches the exact structure expected by Google Apps Script
    """
    try:
        # First, ensure we have a Quotes sheet with the right structure
        try:
            quotes_sheet = self.spreadsheet.worksheet('Quotes')
        except:
            # Create Quotes sheet if it doesn't exist
            quotes_sheet = self.spreadsheet.add_worksheet(
                title='Quotes',
                rows=1000,
                cols=37
            )

            # Add the exact headers expected by Google Apps Script
            headers = [
                'ID', 'Date_Created', 'Customer_Name', 'Customer_Email', 'Customer_Phone',
                'Customer_Address', 'Customer_City', 'Customer_State', 'Customer_Zip',
                'Properties', 'Materials', 'Services', 'Employees', 'Labor_Hours',
                'Labor_Cost', 'Material_Cost', 'Service_Cost', 'Travel_Cost',
                'Base_Cost', 'Profit_Margin', 'Profit_Amount', 'Subtotal',
                'Tax_Amount', 'Total_Amount', 'Status', 'Valid_Until', 'Notes',
                'Internal_Notes', 'Created_By', 'Assigned_To', 'Follow_Up_Date',
                'Customer_ID', 'Converted_Date', 'Decline_Reason', 'Service_Type',
                'Frequency', 'Mileage'
            ]
            quotes_sheet.append_row(headers)

        # Check if headers exist, add them if not
        if quotes_sheet.row_count > 0:
            existing_headers = quotes_sheet.row_values(1)
            if len(existing_headers) == 0 or existing_headers[0] != 'ID':
                # Headers are missing or wrong, add correct ones
                headers = [
                    'ID', 'Date_Created', 'Customer_Name', 'Customer_Email', 'Customer_Phone',
                    'Customer_Address', 'Customer_City', 'Customer_State', 'Customer_Zip',
                    'Properties', 'Materials', 'Services', 'Employees', 'Labor_Hours',
                    'Labor_Cost', 'Material_Cost', 'Service_Cost', 'Travel_Cost',
                    'Base_Cost', 'Profit_Margin', 'Profit_Amount', 'Subtotal',
                    'Tax_Amount', 'Total_Amount', 'Status', 'Valid_Until', 'Notes',
                    'Internal_Notes', 'Created_By', 'Assigned_To', 'Follow_Up_Date',
                    'Customer_ID', 'Converted_Date', 'Decline_Reason', 'Service_Type',
                    'Frequency', 'Mileage'
                ]

                # Clear first row and add headers
                quotes_sheet.update('A1:AK1', [headers])

        # Validate we have exactly 37 columns
        if len(quote_data) != 37:
            print(f"Warning: Expected 37 columns, got {len(quote_data)}")
            # Pad or trim to exactly 37 columns
            while len(quote_data) < 37:
                quote_data.append('')
            quote_data = quote_data[:37]

        # Convert all data to string format for Google Sheets
        formatted_data = []
        for i, item in enumerate(quote_data):
            if item is None or item == '':
                formatted_data.append('')
            elif isinstance(item, (dict, list)):
                # JSON fields (Properties, Materials, Services, Employees)
                import json
                formatted_data.append(json.dumps(item) if isinstance(item, (dict, list)) else str(item))
            elif isinstance(item, bool):
                formatted_data.append('yes' if item else 'no')
            elif isinstance(item, (int, float)):
                formatted_data.append(str(item))
            else:
                formatted_data.append(str(item))

        # Apply rate limiting before writing
        self._rate_limit()

        # Append the row
        quotes_sheet.append_row(formatted_data)

        print(f"Quote {formatted_data[0]} successfully saved to Google Sheets")

        return {
            'success': True,
            'quote_id': formatted_data[0]
        }

    except Exception as e:
        print(f"Error adding quote to Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

# ALSO UPDATE YOUR EXISTING add_quote METHOD to use add_quote_full
def add_quote(self, name, email, phone, property_type, square_feet,
             service_type, calculated_price):
    """Legacy method - now creates full 37-column structure"""

    # Generate quote ID
    quote_id = f"QUOTE{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Create properties JSON
    properties = [{
        'id': 1,
        'name': f"{property_type.title()} Property",
        'facilityType': property_type,
        'squareFeet': square_feet,
        'restrooms': 2,
        'windows': 10,
        'rooms': 5,
        'floors': 1
    }]

    # Calculate basic pricing
    base_rates = {
        'office': 0.05,
        'medical': 0.08,
        'retail': 0.04,
        'restaurant': 0.06,
        'warehouse': 0.03,
        'residential': 0.06
    }

    base_rate = base_rates.get(property_type, 0.05)
    base_cost = square_feet * base_rate
    labor_hours = max(2, square_feet / 3000)
    labor_cost = labor_hours * 25
    material_cost = square_feet * 0.01

    total_base = base_cost + labor_cost + material_cost
    profit_amount = total_base * 0.35
    subtotal = total_base + profit_amount
    tax_amount = subtotal * 0.0625
    total_amount = subtotal + tax_amount

    # Create the full 37-column row
    import json
    quote_data = [
        quote_id,                                    # 1. ID
        datetime.now().isoformat(),                  # 2. Date_Created
        name,                                        # 3. Customer_Name
        email,                                       # 4. Customer_Email
        phone,                                       # 5. Customer_Phone
        '',                                          # 6. Customer_Address
        '',                                          # 7. Customer_City
        'MA',                                        # 8. Customer_State
        '',                                          # 9. Customer_Zip
        json.dumps(properties),                      # 10. Properties (JSON)
        json.dumps([]),                              # 11. Materials (JSON)
        json.dumps([]),                              # 12. Services (JSON)
        json.dumps([]),                              # 13. Employees (JSON)
        round(labor_hours, 2),                       # 14. Labor_Hours
        round(labor_cost, 2),                        # 15. Labor_Cost
        round(material_cost, 2),                     # 16. Material_Cost
        0,                                           # 17. Service_Cost
        0,                                           # 18. Travel_Cost
        round(total_base, 2),                        # 19. Base_Cost
        35,                                          # 20. Profit_Margin
        round(profit_amount, 2),                     # 21. Profit_Amount
        round(subtotal, 2),                          # 22. Subtotal
        round(tax_amount, 2),                        # 23. Tax_Amount
        round(calculated_price or total_amount, 2),  # 24. Total_Amount
        'pending',                                   # 25. Status
        (datetime.now() + timedelta(days=30)).isoformat(), # 26. Valid_Until
        '',                                          # 27. Notes
        f'Web quote: {property_type} - {square_feet} sqft', # 28. Internal_Notes
        'Python Web Form',                           # 29. Created_By
        '',                                          # 30. Assigned_To
        '',                                          # 31. Follow_Up_Date
        '',                                          # 32. Customer_ID
        '',                                          # 33. Converted_Date
        '',                                          # 34. Decline_Reason
        service_type or 'regular',                   # 35. Service_Type
        'monthly',                                   # 36. Frequency
        0                                            # 37. Mileage
    ]

    return self.add_quote_full(quote_data)

# Example usage and testing
if __name__ == "__main__":
    # Test the database connection
    db = SheetsDatabase()

    # Test getting quotes
    quotes = db.get_quotes(status='pending')
    print(f"Found {len(quotes)} pending quotes")

    # Test getting dashboard stats
    stats = db.get_dashboard_stats()
    print(f"Dashboard stats: {stats}")