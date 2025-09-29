"""
Email Service Module
Handles email notifications for quotes, appointments, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class EmailService:
    def __init__(self):
        """Initialize email service with configuration"""
        from config import Config
        
        self.smtp_host = Config.EMAIL_HOST
        self.smtp_port = Config.EMAIL_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_APP_PASSWORD
        self.from_email = Config.EMAIL_USERNAME
        self.business_name = Config.BUSINESS_NAME
        self.business_phone = Config.BUSINESS_PHONE
    
    def send_email(self, to_email, subject, html_body, text_body=None):
        """Send email with HTML and text content"""
        if not self.username or not self.password:
            print("Email not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.business_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def send_quote_notification(self, name, email, phone, property_type, 
                               square_feet, price, quote_id):
        """Send quote notification to admin and customer"""
        
        # Email to customer
        customer_subject = f"Your Cleaning Quote - {self.business_name}"
        customer_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Thank You for Your Quote Request!</h2>
                <p>Dear {name},</p>
                <p>We've received your request for a cleaning service quote. Here are the details:</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Quote Details</h3>
                    <p><strong>Quote ID:</strong> {quote_id}</p>
                    <p><strong>Property Type:</strong> {property_type.title()}</p>
                    <p><strong>Square Feet:</strong> {square_feet:,}</p>
                    <p><strong>Estimated Price:</strong> ${price:.2f}</p>
                </div>
                
                <p>One of our representatives will contact you within 24 hours to discuss your needs and schedule a service.</p>
                
                <p>If you have any questions, please call us at {self.business_phone}.</p>
                
                <p>Best regards,<br>
                {self.business_name} Team</p>
            </body>
        </html>
        """
        
        self.send_email(email, customer_subject, customer_html)
        
        # Email to admin
        admin_subject = f"New Quote Request - ${price:.2f}"
        admin_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Quote Request</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone:</strong> {phone}</p>
                <p><strong>Property Type:</strong> {property_type}</p>
                <p><strong>Square Feet:</strong> {square_feet:,}</p>
                <p><strong>Estimated Price:</strong> ${price:.2f}</p>
                <p><strong>Quote ID:</strong> {quote_id}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </body>
        </html>
        """
        
        self.send_email(self.from_email, admin_subject, admin_html)
    
    def send_appointment_confirmation(self, customer_email, customer_name, 
                                    date, time, address, employee):
        """Send appointment confirmation to customer"""
        
        subject = f"Appointment Confirmed - {date}"
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Your Cleaning Appointment is Confirmed!</h2>
                <p>Dear {customer_name},</p>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3>Appointment Details</h3>
                    <p><strong>Date:</strong> {date}</p>
                    <p><strong>Time:</strong> {time}</p>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Cleaner:</strong> {employee}</p>
                </div>
                
                <p>Our cleaner will arrive at the scheduled time. Please ensure someone is available to provide access to the property.</p>
                
                <p>If you need to reschedule, please call us at {self.business_phone} at least 24 hours in advance.</p>
                
                <p>Thank you for choosing {self.business_name}!</p>
            </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html)
    
    def send_job_reminder(self, employee_email, employee_name, jobs_today):
        """Send daily job reminder to employee"""
        
        subject = f"Today's Schedule - {len(jobs_today)} Jobs"
        
        job_list = ""
        for job in jobs_today:
            job_list += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <p><strong>{job['Time']}</strong> - {job['Customer_Name']}</p>
                <p>{job['Address']}</p>
                <p>Service: {job['Service_Type']} - ${job['Price']}</p>
            </div>
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Good Morning, {employee_name}!</h2>
                <p>You have {len(jobs_today)} jobs scheduled for today:</p>
                {job_list}
                <p>Have a great day!</p>
            </body>
        </html>
        """
        
        return self.send_email(employee_email, subject, html)