"""
Initialize Google Sheets Database
Creates all required sheets with proper structure
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def initialize_database():
    """Create and initialize all database sheets"""
    
    print("🔧 Initializing Google Sheets Database...")
    print("=" * 50)
    
    # Setup credentials
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    
    try:
        creds = Credentials.from_service_account_file(Config.GOOGLE_SHEETS_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        print("✅ Connected to Google Sheets")
    except FileNotFoundError:
        print("❌ Error: credentials.json not found!")
        print("Please download your service account credentials from Google Cloud Console")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return False
    
    # Create or open spreadsheet
    try:
        spreadsheet = client.open(Config.SPREADSHEET_NAME)
        print(f"📊 Found existing spreadsheet: {Config.SPREADSHEET_NAME}")
    except:
        try:
            spreadsheet = client.create(Config.SPREADSHEET_NAME)
            print(f"📊 Created new spreadsheet: {Config.SPREADSHEET_NAME}")
        except Exception as e:
            print(f"❌ Error creating spreadsheet: {e}")
            return False
    
    # Define sheet structures
    sheets_structure = {
        'Customers': [
            'ID', 'Name', 'Email', 'Phone', 'Address', 'Business_Type',
            'Square_Feet', 'Service_Frequency', 'Added_Date', 'Status',
            'Special_Instructions', 'Preferred_Day', 'Preferred_Time',
            'Gate_Code', 'Billing_Email', 'Payment_Method', 'Notes'
        ],
        'Jobs': [
            'ID', 'Customer_Name', 'Date', 'Time', 'Employee', 'Address',
            'Service_Type', 'Price', 'Status', 'Completed', 'Notes',
            'Check_In_Time', 'Check_Out_Time', 'Photos', 'Duration_Minutes',
            'Customer_Rating', 'Customer_Feedback'
        ],
        'Employees': [
            'ID', 'Name', 'Email', 'Phone', 'Username', 'Password_Hash',
            'Hire_Date', 'Active', 'Hourly_Rate', 'Color_Code',
            'Emergency_Contact', 'Skills', 'Performance_Score'
        ],
        'Quotes': [
            'ID', 'Name', 'Email', 'Phone', 'Property_Type', 'Square_Feet',
            'Service_Type', 'Calculated_Price', 'Date_Requested', 'Status',
            'Converted', 'Follow_Up_Date', 'Notes', 'Source', 'Competitor_Price'
        ],
        'Payments': [
            'ID', 'Customer_Name', 'Amount', 'Date', 'Method',
            'Invoice_Number', 'Status', 'Job_IDs', 'Notes',
            'Transaction_ID', 'Tax_Amount', 'Discount_Amount'
        ],
        'Settings': [
            'Key', 'Value', 'Category', 'Description', 'Updated_Date', 'Updated_By'
        ],
        'Schedule_Templates': [
            'ID', 'Template_Name', 'Customer_Name', 'Day_of_Week',
            'Time', 'Employee', 'Service_Type', 'Active'
        ]
    }
    
    # Create sheets
    existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
    
    for sheet_name, headers in sheets_structure.items():
        if sheet_name not in existing_sheets:
            try:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)
                worksheet.append_row(headers)
                print(f"✅ Created sheet: {sheet_name}")
            except Exception as e:
                print(f"❌ Error creating sheet {sheet_name}: {e}")
        else:
            worksheet = spreadsheet.worksheet(sheet_name)
            # Check if headers exist
            if not worksheet.row_values(1):
                worksheet.append_row(headers)
                print(f"✅ Added headers to: {sheet_name}")
            else:
                print(f"✓ Sheet exists: {sheet_name}")
    
    # Initialize default settings
    initialize_default_settings(spreadsheet)
    
    # Delete default Sheet1 if exists
    try:
        default_sheet = spreadsheet.worksheet('Sheet1')
        spreadsheet.del_worksheet(default_sheet)
        print("✅ Removed default Sheet1")
    except:
        pass
    
    print("=" * 50)
    print(f"✅ Database initialization complete!")
    print(f"📍 Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
    
    # Save the spreadsheet ID
    save_spreadsheet_id(spreadsheet.id)
    
    return True

def initialize_default_settings(spreadsheet):
    """Add default business settings"""
    
    settings_sheet = spreadsheet.worksheet('Settings')
    
    # Check if settings already exist
    existing = settings_sheet.get_all_records()
    if existing:
        print("✓ Settings already initialized")
        return
    
    # Default settings
    default_settings = [
        # Pricing
        ['price_office', '0.08', 'pricing', 'Price per sq ft for offices', datetime.now().isoformat(), 'system'],
        ['price_retail', '0.10', 'pricing', 'Price per sq ft for retail', datetime.now().isoformat(), 'system'],
        ['price_medical', '0.12', 'pricing', 'Price per sq ft for medical', datetime.now().isoformat(), 'system'],
        ['price_restaurant', '0.10', 'pricing', 'Price per sq ft for restaurants', datetime.now().isoformat(), 'system'],
        ['price_residential', '0.15', 'pricing', 'Price per sq ft for residential', datetime.now().isoformat(), 'system'],
        
        # Multipliers
        ['multiplier_onetime', '1.5', 'pricing', 'One-time service multiplier', datetime.now().isoformat(), 'system'],
        ['multiplier_weekly', '1.0', 'pricing', 'Weekly service multiplier', datetime.now().isoformat(), 'system'],
        ['multiplier_biweekly', '1.1', 'pricing', 'Bi-weekly service multiplier', datetime.now().isoformat(), 'system'],
        ['multiplier_monthly', '1.2', 'pricing', 'Monthly service multiplier', datetime.now().isoformat(), 'system'],
        
        # Business
        ['minimum_charge', '100', 'business', 'Minimum service charge', datetime.now().isoformat(), 'system'],
        ['business_hours_start', '08:00', 'business', 'Business start time', datetime.now().isoformat(), 'system'],
        ['business_hours_end', '18:00', 'business', 'Business end time', datetime.now().isoformat(), 'system'],
        ['lunch_break_start', '12:00', 'business', 'Lunch break start', datetime.now().isoformat(), 'system'],
        ['lunch_break_duration', '60', 'business', 'Lunch break minutes', datetime.now().isoformat(), 'system'],
        
        # Notifications
        ['email_notifications', 'true', 'notifications', 'Send email notifications', datetime.now().isoformat(), 'system'],
        ['sms_notifications', 'false', 'notifications', 'Send SMS notifications', datetime.now().isoformat(), 'system'],
        ['reminder_hours', '24', 'notifications', 'Hours before job to send reminder', datetime.now().isoformat(), 'system'],
    ]
    
    for setting in default_settings:
        settings_sheet.append_row(setting)
    
    print(f"✅ Initialized {len(default_settings)} default settings")

def save_spreadsheet_id(spreadsheet_id):
    """Save spreadsheet ID to a file for reference"""
    with open('.spreadsheet_id', 'w') as f:
        f.write(spreadsheet_id)

def initialize_if_needed():
    """Initialize database only if needed"""
    try:
        from modules.sheets_db import SheetsDatabase
        db = SheetsDatabase()
        return True
    except:
        return initialize_database()

if __name__ == "__main__":
    initialize_database()