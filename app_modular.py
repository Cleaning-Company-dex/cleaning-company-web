# app_modular.py - NEW FILE, doesn't replace your existing app.py
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Business Info - make it accessible to all blueprints
    app.config['BUSINESS_NAME'] = "Baez Cleaning Services"
    app.config['BUSINESS_PHONE'] = "(555) 123-4567"
    app.config['BUSINESS_EMAIL'] = "info@baezcleaningservices.com"
    
    # Initialize services
    from modules.sheets_db import SheetsDatabase
    from modules.gemini_chat import GeminiChat
    
    app.db = SheetsDatabase()
    app.chat = GeminiChat()
    
    # Register Blueprints
    from routes.public import public_bp
    from routes.admin import admin_bp
    from routes.employee import employee_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)