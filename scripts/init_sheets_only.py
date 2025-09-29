import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def initialize_sheets():
    print("Setting up sheets in existing spreadsheet...")
    print("=" * 50)
    
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    
    creds = Credentials.from_service_account_file('../credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    print("Connected to Google Sheets")
    
    try:
        spreadsheet = client.open('Cleaning_Business_Database')
        print("Found spreadsheet: Cleaning_Business_Database")
    except Exception as e:
        print("Error:", e)
        print("Make sure you:")
        print("1. Created a spreadsheet named 'Cleaning_Business_Database'")
        print("2. Shared it with your service account email")
        return False
    
    sheets_structure = {
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
    
    existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
    
    for sheet_name, headers in sheets_structure.items():
        if sheet_name not in existing_sheets:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)
            worksheet.append_row(headers)
            print("Created sheet:", sheet_name)
        else:
            worksheet = spreadsheet.worksheet(sheet_name)
            if not worksheet.row_values(1):
                worksheet.append_row(headers)
                print("Added headers to:", sheet_name)
            else:
                print("Sheet exists:", sheet_name)
    
    try:
        default_sheet = spreadsheet.worksheet('Sheet1')
        spreadsheet.del_worksheet(default_sheet)
        print("Removed default Sheet1")
    except:
        pass
    
    print("=" * 50)
    print("Database setup complete!")
    print("Your spreadsheet: https://docs.google.com/spreadsheets/d/" + spreadsheet.id)
    return True

if __name__ == "__main__":
    initialize_sheets()
