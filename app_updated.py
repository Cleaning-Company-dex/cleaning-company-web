from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
import os
from modules.sheets_db import SheetsDatabase
from modules.gemini_chat import GeminiChat
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize services
db = SheetsDatabase()
chat = GeminiChat()

# Business Info
BUSINESS_NAME = "Baez Cleaning Services"
BUSINESS_PHONE = "(555) 123-4567"
BUSINESS_EMAIL = "info@baezcleaningservices.com"

# Chatbot API endpoint
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'response': 'Please ask a question about our cleaning services!'})
    
    response = chat.get_response(message)
    return jsonify({'response': response})
