"""
Load Test Data
Populates database with sample data for testing
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.sheets_db import SheetsDatabase

def load_test_data():
    """Load sample data into database"""
    
    print("📦 Loading test data...")
    print("=" * 50)
    
    db = SheetsDatabase()
    
    # Sample employees
    employees = [
        {'name': 'John Smith', 'email': 'john@cleanpro.com', 'phone': '555-0101', 
         'username': 'john', 'password': 'password123', 'hourly_rate': 25},
        {'name': 'Maria Garcia', 'email': 'maria@cleanpro.com', 'phone': '555-0102',
         'username': 'maria', 'password': 'password123', 'hourly_rate': 25},
        {'name': 'Mike Johnson', 'email': 'mike@cleanpro.com', 'phone': '555-0103',
         'username': 'mike', 'password': 'password123', 'hourly_rate': 22},
        {'name': 'Sarah Williams', 'email': 'sarah@cleanpro.com', 'phone': '555-0104',
         'username': 'sarah', 'password': 'password123', 'hourly_rate': 22},
    ]
    
    print("Adding employees...")
    for emp in employees:
        emp_id = db.add_employee(
            emp['name'], emp['email'], emp['phone'],
            emp['username'], emp['password'], emp['hourly_rate']
        )
        print(f"  ✅ Added employee: {emp['name']} (Username: {emp['username']})")
    
    # Sample customers
    customers = [
        {'name': 'ABC Corporation', 'email': 'contact@abc.com', 'phone': '555-1001',
         'address': '123 Business Ave, Boston, MA 02101', 'type': 'office', 'sqft': 5000},
        {'name': 'XYZ Medical Center', 'email': 'admin@xyzmed.com', 'phone': '555-1002',
         'address': '456 Health St, Cambridge, MA 02139', 'type': 'medical', 'sqft': 8000},
        {'name': 'Downtown Retail Store', 'email': 'manager@retail.com', 'phone': '555-1003',
         'address': '789 Shopping Blvd, Boston, MA 02116', 'type': 'retail', 'sqft': 3000},
        {'name': 'Tech Startup Inc', 'email': 'office@techstartup.com', 'phone': '555-1004',
         'address': '321 Innovation Way, Cambridge, MA 02142', 'type': 'office', 'sqft': 2500},
        {'name': 'Local Restaurant', 'email': 'owner@restaurant.com', 'phone': '555-1005',
         'address': '654 Dining St, Somerville, MA 02144', 'type': 'restaurant', 'sqft': 2000},
    ]
    
    print("\nAdding customers...")
    customer_ids = []
    for cust in customers:
        cust_id = db.add_customer(
            cust['name'], cust['email'], cust['phone'], cust['address'],
            cust['type'], cust['sqft'], 'weekly'
        )
        customer_ids.append(cust_id)
        print(f"  ✅ Added customer: {cust['name']}")
    
    # Sample jobs for the next 30 days
    print("\nScheduling jobs...")
    job_count = 0
    for i in range(30):
        date = datetime.now() + timedelta(days=i)
        if date.weekday() < 5:  # Weekdays only
            
            # Schedule 2-3 jobs per employee per day
            for emp in employees:
                num_jobs = random.randint(2, 3)
                available_customers = customers.copy()
                random.shuffle(available_customers)
                
                times = ['09:00', '11:00', '14:00', '16:00']
                for j in range(min(num_jobs, len(available_customers))):
                    cust = available_customers[j]
                    time = times[j] if j < len(times) else '10:00'
                    
                    # Calculate price
                    from utils.helpers import calculate_price
                    price = calculate_price(cust['type'], cust['sqft'], 'weekly')
                    
                    job_id = db.add_job(
                        cust['name'],
                        date.strftime('%Y-%m-%d'),
                        time,
                        emp['name'],
                        cust['address'],
                        'weekly',
                        price
                    )
                    job_count += 1
    
    print(f"  ✅ Created {job_count} jobs")
    
    # Sample quotes
    print("\nAdding sample quotes...")
    quotes = [
        {'name': 'Potential Client 1', 'email': 'client1@email.com', 'phone': '555-2001',
         'type': 'office', 'sqft': 4000, 'service': 'weekly'},
        {'name': 'Potential Client 2', 'email': 'client2@email.com', 'phone': '555-2002',
         'type': 'retail', 'sqft': 2500, 'service': 'biweekly'},
        {'name': 'Potential Client 3', 'email': 'client3@email.com', 'phone': '555-2003',
         'type': 'medical', 'sqft': 6000, 'service': 'weekly'},
    ]
    
    for quote in quotes:
        from utils.helpers import calculate_price
        price = calculate_price(quote['type'], quote['sqft'], quote['service'])
        
        quote_id = db.add_quote(
            quote['name'], quote['email'], quote['phone'],
            quote['type'], quote['sqft'], quote['service'], price
        )
        print(f"  ✅ Added quote: {quote['name']} - ${price:.2f}")
    
    # Mark some past jobs as completed
    print("\nMarking some jobs as completed...")
    all_jobs = db.get_all_jobs()
    today = datetime.now().strftime('%Y-%m-%d')
    completed_count = 0
    
    for job in all_jobs:
        if job['Date'] < today:
            if random.random() > 0.1:  # 90% completion rate
                db.complete_job(job['ID'])
                completed_count += 1
    
    print(f"  ✅ Marked {completed_count} jobs as completed")
    
    # Add sample payments for completed jobs
    print("\nAdding sample payments...")
    payment_count = 0
    for cust in customers[:3]:  # Add payments for first 3 customers
        amount = random.randint(500, 2000)
        payment_id = db.add_payment(
            cust['name'],
            amount,
            'card',
            '',
            'Monthly payment'
        )
        payment_count += 1
    
    print(f"  ✅ Added {payment_count} payments")
    
    print("=" * 50)
    print("✅ Test data loaded successfully!")
    print("\nYou can now log in with:")
    print("  Admin: username='admin', password='changeme123'")
    print("  Employee: username='john', password='password123'")
    print("  Customer: email='contact@abc.com'")

if __name__ == "__main__":
    load_test_data()