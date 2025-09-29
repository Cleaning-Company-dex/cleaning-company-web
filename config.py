"""
Configuration settings for the Cleaning Business Platform
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_TYPE = 'filesystem'
    
    # File uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Google Configuration
    GOOGLE_SHEETS_CREDS = 'credentials.json'
    SPREADSHEET_NAME = os.environ.get('GOOGLE_SHEETS_NAME', 'Cleaning_Business_Database')
    DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Email Configuration
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_APP_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD')
    EMAIL_USE_TLS = True
    
    # Admin Configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme123')
    
    # Business Configuration
    BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'CleanPro Services')
    BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '(555) 123-4567')
    BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL', 'info@cleanpro.com')
    
    # Pricing Configuration (per square foot)
    PRICING = {
        'office': 0.08,
        'retail': 0.10,
        'medical': 0.12,
        'restaurant': 0.10,
        'residential': 0.15
    }
    
    # Service Frequency Multipliers
    FREQUENCY_MULTIPLIERS = {
        'one_time': 1.5,
        'weekly': 1.0,
        'biweekly': 1.1,
        'monthly': 1.2
    }
    
    # Minimum charge
    MINIMUM_CHARGE = 100.00
    
    # Service Areas
    SERVICE_AREAS = [
        'Boston', 'Cambridge', 'Quincy', 'Newton', 'Brookline',
        'Somerville', 'Watertown', 'Waltham', 'Lexington', 'Arlington'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}