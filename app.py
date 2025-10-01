import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template_string,
                   request, session, url_for)

from modules.gemini_chat import GeminiChat
from modules.sheets_db import SheetsDatabase
# Import the admin blueprint
from routes.admin import admin_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Register the admin blueprint
app.register_blueprint(admin_bp)

# Initialize services
db = SheetsDatabase()
chat = GeminiChat()

# Business Info
BUSINESS_NAME = "Baez Cleaning Services"
BUSINESS_PHONE = "(555) 123-4567"
BUSINESS_EMAIL = "info@baezcleaningservices.com"

# Quote Configuration (matching Google Sheets)
QUOTE_CONFIG = {
    'propertyRates': {
        'office': 0.05,
        'medical': 0.08,
        'retail': 0.04,
        'restaurant': 0.06,
        'warehouse': 0.03,
        'residential': 0.06
    },
    'serviceMultipliers': {
        'regular': 1.0,
        'deep-clean': 2.0,
        'post-construction': 2.5,
        'move-in-out': 1.8
    },
    'frequencyDiscounts': {
        'one-time': 0,
        'daily': 0.25,
        'weekly': 0.20,
        'bi-weekly': 0.15,
        'monthly': 0.10
    },
    'taxRate': 0.0625,
    'defaultProfitMargin': 35
}

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            if db.verify_admin(username, password):
                session['is_admin'] = True
                session.permanent = True
                app.permanent_session_lifetime = timedelta(hours=4)
                flash('Welcome back, Administrator!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid credentials', 'error')
        except Exception as e:
            print(f"Login error: {e}")
            flash('Database connection error. Please try again.', 'error')

    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-red-50 to-orange-50 min-h-screen flex items-center">
    <div class="max-w-md mx-auto px-4 w-full">
        <div class="bg-white rounded-2xl shadow-xl p-8">
            <div class="text-center mb-8">
                <div class="text-5xl mb-4">🔐</div>
                <h2 class="text-3xl font-bold">Admin Login</h2>
            </div>
            <form method="POST" class="space-y-6">
                <input type="text" name="username" placeholder="Username" required
                    class="w-full px-4 py-3 border rounded-lg">
                <input type="password" name="password" placeholder="Password" required
                    class="w-full px-4 py-3 border rounded-lg">
                <button type="submit" class="w-full bg-red-500 text-white py-3 rounded-lg font-semibold">
                    Login
                </button>
            </form>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({'response': 'Please ask a question about our cleaning services!'})

    response = chat.get_response(message)
    return jsonify({'response': response})

@app.route('/')
def index():
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{BUSINESS_NAME} - Professional Cleaning Services</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            overflow-x: hidden;
            width: 100%;
        }}
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .card-hover {{ transition: all 0.3s; }}
        .card-hover:hover {{ transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }}
        @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}
        .pulse-animation {{ animation: pulse 2s infinite; }}
        .typing-dots span {{
            animation: blink 1.4s infinite;
        }}
        .typing-dots span:nth-child(2) {{
            animation-delay: 0.2s;
        }}
        .typing-dots span:nth-child(3) {{
            animation-delay: 0.4s;
        }}
        @keyframes blink {{
            0%, 60%, 100% {{ opacity: 0; }}
            30% {{ opacity: 1; }}
        }}

        /* Prevent horizontal scroll */
        html, body {{
            max-width: 100%;
            overflow-x: hidden;
        }}

        /* Fix for mobile chat widget */
        @media (max-width: 640px) {{
            #chat-widget {{
                right: 10px !important;
                bottom: 10px !important;
            }}
            #chat-box {{
                width: calc(100vw - 20px) !important;
                right: -10px !important;
                max-width: 380px !important;
            }}
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Navigation - Mobile Optimized -->
    <nav class="bg-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo - Responsive Size -->
                <div class="flex items-center">
                    <span class="text-lg sm:text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                        🧹 {BUSINESS_NAME}
                    </span>
                </div>

                <!-- Right Nav - Mobile Responsive -->
                <div class="flex items-center gap-2">
                    <!-- Phone - Hidden on very small screens -->
                    <a href="tel:{BUSINESS_PHONE}" class="hidden sm:flex text-gray-600 hover:text-purple-600 text-sm">
                        📞 <span class="hidden md:inline">{BUSINESS_PHONE}</span>
                    </a>

                    <!-- Get Quote Button - Responsive -->
                    <a href="/quote" class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 sm:px-6 py-2 rounded-full font-medium text-sm sm:text-base pulse-animation">
                        <span class="hidden sm:inline">Get Free</span> Quote
                    </a>

                    <!-- Staff Button - Responsive -->
                    <a href="/login" class="bg-gray-100 text-gray-700 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition flex items-center gap-1">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" class="flex-shrink-0">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                        </svg>
                        <span>Staff</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section - Mobile Optimized -->
    <div class="gradient-bg text-white">
        <div class="max-w-7xl mx-auto px-4 py-12 sm:py-24 sm:px-6 lg:px-8">
            <div class="text-center">
                <h1 class="text-3xl sm:text-5xl md:text-6xl font-bold mb-4 sm:mb-6">Your Space, Spotlessly Clean</h1>
                <p class="text-lg sm:text-xl mb-2 opacity-90">Professional Cleaning Services for Homes & Businesses</p>
                <p class="text-base sm:text-lg mb-6 sm:mb-8 opacity-80">Licensed • Insured • Satisfaction Guaranteed</p>

                <!-- CTA Buttons - Stack on Mobile -->
                <div class="flex flex-col sm:flex-row justify-center items-center gap-4 px-4">
                    <a href="/quote" class="bg-white text-purple-700 px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold text-base sm:text-lg hover:shadow-xl transition transform hover:scale-105 w-full sm:w-auto max-w-xs">
                        Get Instant Quote →
                    </a>
                    <a href="tel:{BUSINESS_PHONE}" class="border-2 border-white text-white px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold text-base sm:text-lg hover:bg-white hover:text-purple-700 transition w-full sm:w-auto max-w-xs">
                        📞 Call Now
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Trust Indicators - Mobile Grid -->
    <div class="bg-white py-6 sm:py-8 border-b">
        <div class="max-w-7xl mx-auto px-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                    <div class="text-2xl sm:text-3xl font-bold text-purple-600">500+</div>
                    <div class="text-xs sm:text-sm text-gray-600">Happy Customers</div>
                </div>
                <div>
                    <div class="text-2xl sm:text-3xl font-bold text-purple-600">10+</div>
                    <div class="text-xs sm:text-sm text-gray-600">Years Experience</div>
                </div>
                <div>
                    <div class="text-2xl sm:text-3xl font-bold text-purple-600">Licensed</div>
                    <div class="text-xs sm:text-sm text-gray-600">& Insured</div>
                </div>
                <div>
                    <div class="text-2xl sm:text-3xl font-bold text-purple-600">100%</div>
                    <div class="text-xs sm:text-sm text-gray-600">Satisfaction</div>
                </div>
            </div>
        </div>
    </div>

    <!-- What We Clean Section - Mobile Responsive -->
    <div class="py-12 sm:py-16 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4">
            <div class="text-center mb-8 sm:mb-12">
                <h2 class="text-3xl sm:text-4xl font-bold mb-3 sm:mb-4">We Clean Everything!</h2>
                <p class="text-lg sm:text-xl text-gray-600">From small offices to large commercial spaces</p>
            </div>

            <!-- Service Cards - Responsive Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                <div class="bg-white p-5 sm:p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">🏢</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Commercial Offices</h3>
                    <p class="text-sm sm:text-base text-gray-600 mb-3">Keep your workspace professional</p>
                    <ul class="text-xs sm:text-sm text-gray-500 space-y-1">
                        <li>✓ Daily/Weekly Service</li>
                        <li>✓ Desk & Surface Cleaning</li>
                        <li>✓ Restroom Sanitization</li>
                        <li>✓ Trash Removal</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.08/sq ft</p>
                </div>

                <div class="bg-white p-5 sm:p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">🏥</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Medical Facilities</h3>
                    <p class="text-sm sm:text-base text-gray-600 mb-3">Hospital-grade sanitization</p>
                    <ul class="text-xs sm:text-sm text-gray-500 space-y-1">
                        <li>✓ EPA Approved Disinfectants</li>
                        <li>✓ Exam Room Cleaning</li>
                        <li>✓ Waiting Area Service</li>
                        <li>✓ Biohazard Protocols</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.12/sq ft</p>
                </div>

                <div class="bg-white p-5 sm:p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">🏠</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Residential Homes</h3>
                    <p class="text-sm sm:text-base text-gray-600 mb-3">Your home, perfectly clean</p>
                    <ul class="text-xs sm:text-sm text-gray-500 space-y-1">
                        <li>✓ Deep Cleaning</li>
                        <li>✓ Move In/Out Service</li>
                        <li>✓ Regular Maintenance</li>
                        <li>✓ Post-Construction</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.15/sq ft</p>
                </div>

                <div class="bg-white p-5 sm:p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">🍽️</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Restaurants</h3>
                    <p class="text-sm sm:text-base text-gray-600 mb-3">Food-safe & health compliant</p>
                    <ul class="text-xs sm:text-sm text-gray-500 space-y-1">
                        <li>✓ Kitchen Deep Clean</li>
                        <li>✓ Dining Area Service</li>
                        <li>✓ Grease Trap Cleaning</li>
                        <li>✓ Health Code Compliance</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.10/sq ft</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Professional Video Section - Mobile Responsive -->
    <div class="py-12 sm:py-16 bg-white">
        <div class="max-w-7xl mx-auto px-4">
            <div class="text-center mb-8 sm:mb-12">
                <h2 class="text-3xl sm:text-4xl font-bold mb-3 sm:mb-4">See Us In Action</h2>
                <p class="text-lg sm:text-xl text-gray-600">Professional cleaning that makes a difference</p>
            </div>
            <div class="max-w-4xl mx-auto">
                <div class="relative" style="padding-bottom: 56.25%; height: 0;">
                    <iframe
                        src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                        class="absolute top-0 left-0 w-full h-full rounded-xl shadow-2xl"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>
                </div>
                <div class="mt-6 sm:mt-8 text-center">
                    <p class="text-sm sm:text-base text-gray-600 mb-4">Watch how we transform spaces with our professional cleaning services</p>
                    <a href="/quote" class="inline-block bg-purple-600 text-white px-6 sm:px-8 py-2 sm:py-3 rounded-full font-semibold hover:bg-purple-700 transition">
                        Get Your Free Quote →
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Contact Section - Mobile Optimized -->
    <div class="gradient-bg text-white py-12 sm:py-16">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <h2 class="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8">Get In Touch</h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8">
                <div>
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">📞</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Call Us</h3>
                    <a href="tel:{BUSINESS_PHONE}" class="text-base sm:text-xl hover:underline">{BUSINESS_PHONE}</a>
                    <p class="text-xs sm:text-sm mt-2 opacity-90">Mon-Sat: 8AM-6PM</p>
                </div>
                <div>
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">📧</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Email Us</h3>
                    <a href="mailto:{BUSINESS_EMAIL}" class="text-base sm:text-xl hover:underline break-all">{BUSINESS_EMAIL}</a>
                    <p class="text-xs sm:text-sm mt-2 opacity-90">24/7 Support</p>
                </div>
                <div>
                    <div class="text-3xl sm:text-4xl mb-3 sm:mb-4">📍</div>
                    <h3 class="text-lg sm:text-xl font-semibold mb-2">Service Area</h3>
                    <p class="text-base sm:text-xl">Greater Boston Area</p>
                    <p class="text-xs sm:text-sm mt-2 opacity-90">15 Mile Radius</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer - Mobile Friendly -->
    <footer class="bg-gray-900 text-gray-400 py-4 sm:py-6">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex flex-col sm:flex-row justify-between items-center gap-2">
                <div class="text-xs sm:text-sm text-center sm:text-left">
                    © 2024 {BUSINESS_NAME}. All rights reserved.
                </div>
                <div class="text-xs">
                    <a href="/login" class="text-gray-500 hover:text-gray-400 transition">Staff Portal</a>
                </div>
            </div>
        </div>
    </footer>

    <!-- AI Chatbot Widget - Mobile Responsive -->
    <div id="chat-widget" class="fixed bottom-4 right-4 z-50">
        <!-- Chat Button -->
        <button id="chat-toggle" class="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full p-3 sm:p-4 shadow-lg hover:shadow-xl transition-all transform hover:scale-110">
            <svg width="24" height="24" class="sm:w-7 sm:h-7" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                <circle cx="8" cy="10" r="1"/>
                <circle cx="12" cy="10" r="1"/>
                <circle cx="16" cy="10" r="1"/>
            </svg>
            <span class="absolute -top-1 -right-1 bg-green-500 rounded-full w-3 h-3 animate-pulse"></span>
        </button>

        <!-- Chat Box - Mobile Responsive -->
        <div id="chat-box" class="hidden fixed sm:absolute bottom-16 sm:bottom-20 left-2 right-2 sm:left-auto sm:right-0 sm:w-96 bg-white rounded-2xl shadow-2xl overflow-hidden max-w-[calc(100vw-1rem)] sm:max-w-none">
            <div class="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-3 sm:p-4">
                <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-2">
                        <div class="bg-white/20 rounded-full p-1.5 sm:p-2">
                            <svg width="16" height="16" class="sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="font-bold text-sm sm:text-base">Baez Assistant</h3>
                            <p class="text-xs opacity-90">✨ Always here to help</p>
                        </div>
                    </div>
                    <button id="chat-close" class="text-white/80 hover:text-white transition p-1">
                        <svg width="20" height="20" class="sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
            </div>

            <div id="chat-messages" class="h-64 sm:h-96 overflow-y-auto p-3 sm:p-4 space-y-3 bg-gray-50">
                <div class="bg-white p-3 sm:p-4 rounded-xl shadow-sm">
                    <p class="text-xs sm:text-sm font-medium text-purple-600 mb-2">👋 Welcome to Baez Cleaning!</p>
                    <p class="text-xs sm:text-sm text-gray-700">I can help you with:</p>
                    <ul class="text-xs sm:text-sm text-gray-600 mt-2 space-y-1">
                        <li>💰 Instant pricing information</li>
                        <li>🧹 Our cleaning services</li>
                        <li>📅 Scheduling & availability</li>
                        <li>📍 Service areas</li>
                        <li>✨ Cleaning tips & advice</li>
                    </ul>
                    <p class="text-xs sm:text-sm text-gray-700 mt-3">What would you like to know?</p>
                </div>
            </div>

            <div class="border-t bg-white p-3 sm:p-4">
                <div class="flex space-x-2">
                    <input
                        type="text"
                        id="chat-input"
                        placeholder="Type your question..."
                        class="flex-1 px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                        onkeypress="if(event.key === 'Enter') sendMessage()">
                    <button
                        onclick="sendMessage()"
                        class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 sm:px-4 py-2 rounded-lg hover:shadow-lg transition">
                        <svg width="16" height="16" class="sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                    <button onclick="quickQuestion('What are your prices?')"
                        class="text-xs bg-purple-100 text-purple-700 px-2 sm:px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        💰 Pricing
                    </button>
                    <button onclick="quickQuestion('What services do you offer?')"
                        class="text-xs bg-purple-100 text-purple-700 px-2 sm:px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        🧹 Services
                    </button>
                    <button onclick="quickQuestion('What areas do you serve?')"
                        class="text-xs bg-purple-100 text-purple-700 px-2 sm:px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        📍 Areas
                    </button>
                    <button onclick="quickQuestion('How do I schedule?')"
                        class="text-xs bg-purple-100 text-purple-700 px-2 sm:px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        📅 Schedule
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Chat Widget Toggle
        const chatToggle = document.getElementById('chat-toggle');
        const chatBox = document.getElementById('chat-box');
        const chatClose = document.getElementById('chat-close');
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');

        chatToggle.addEventListener('click', () => {{
            chatBox.classList.toggle('hidden');
            if (!chatBox.classList.contains('hidden')) {{
                chatInput.focus();
            }}
        }});

        chatClose.addEventListener('click', () => {{
            chatBox.classList.add('hidden');
        }});

        // Chat Functions
        async function sendMessage() {{
            const message = chatInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, 'user');
            chatInput.value = '';

            // Show typing indicator
            const typingId = addTypingIndicator();

            try {{
                const response = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ message: message }})
                }});

                const data = await response.json();
                removeTypingIndicator(typingId);
                addMessage(data.response, 'bot');
            }} catch (error) {{
                removeTypingIndicator(typingId);
                addMessage('I can help you with pricing, services, and scheduling! For immediate assistance, call us at (555) 123-4567', 'bot');
            }}
        }}

        function quickQuestion(question) {{
            chatInput.value = question;
            sendMessage();
        }}

        function addMessage(text, sender) {{
            const messageDiv = document.createElement('div');
            if (sender === 'user') {{
                messageDiv.className = 'bg-purple-100 p-2 sm:p-3 rounded-xl ml-4 sm:ml-8';
                messageDiv.innerHTML = `<p class="text-xs sm:text-sm text-gray-800">👤 ${{text}}</p>`;
            }} else {{
                messageDiv.className = 'bg-white p-2 sm:p-3 rounded-xl mr-4 sm:mr-8 shadow-sm';
                messageDiv.innerHTML = `<p class="text-xs sm:text-sm text-gray-700">✨ ${{text}}</p>`;
            }}
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function addTypingIndicator() {{
            const id = 'typing-' + Date.now();
            const typingDiv = document.createElement('div');
            typingDiv.id = id;
            typingDiv.className = 'bg-white p-2 sm:p-3 rounded-xl mr-4 sm:mr-8 shadow-sm';
            typingDiv.innerHTML = '<p class="text-xs sm:text-sm text-gray-500">✨ <span class="inline-flex space-x-1"><span class="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></span><span class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></span><span class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></span></span></p>';
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return id;
        }}

        function removeTypingIndicator(id) {{
            const element = document.getElementById(id);
            if (element) element.remove();
        }}
    </script>
</body>
</html>
    '''

@app.route('/quote')
def quote():
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get Your Custom Quote - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .step {{ display: none; }}
        .step.active {{ display: block; }}
        .fade-in {{ animation: fadeIn 0.3s ease-in; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .selected {{ border-color: #9333ea !important; background: #f3e8ff !important; }}
        .price-pop {{ animation: pricePop 0.5s ease-out; }}
        @keyframes pricePop {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.2); }} 100% {{ transform: scale(1); }} }}
        .photo-preview {{
            width: 100px;
            height: 100px;
            object-fit: cover;
            border-radius: 8px;
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-8">
        <!-- Progress Bar -->
        <div class="mb-8">
            <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Getting Started</span>
                <span id="progress-text">Step 1 of 6</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
                <div id="progress-bar" class="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-500" style="width: 16.66%"></div>
            </div>
        </div>

        <div class="bg-white rounded-3xl shadow-2xl p-8">
            <!-- PERSONALIZED SERVICE NOTICE -->
            <div class="bg-blue-50 border-2 border-blue-400 rounded-xl p-4 mb-6">
                <div class="flex items-start">
                    <span class="text-2xl mr-3">✨</span>
                    <div>
                        <h3 class="font-bold text-blue-800 mb-1">Personalized Quotes Only</h3>
                        <p class="text-sm text-blue-700">
                            We believe every space is unique! That's why we provide customized quotes after understanding your specific needs.
                        </p>
                        <ul class="text-sm text-blue-700 mt-2 space-y-1">
                            <li>• Tell us about your space</li>
                            <li>• We'll contact you within 24 hours</li>
                            <li>• Receive a FREE on-site assessment</li>
                            <li>• Get a detailed quote tailored to your exact requirements</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Quote Status Display -->
            <div class="fixed top-20 right-4 bg-white rounded-xl shadow-lg p-4 z-50 hidden md:block">
                <div class="text-xs text-gray-500">Quote Status</div>
                <div class="text-xl font-bold text-purple-600">In Progress</div>
                <div class="text-xs text-green-500">We'll contact you soon!</div>
            </div>

            <!-- Step 1: Property Type -->
            <div id="step1" class="step active fade-in">
                <h2 class="text-3xl font-bold mb-2">Let's Get Started! 🏢</h2>
                <p class="text-gray-600 mb-8">What type of space needs our magic touch?</p>

                <div class="grid md:grid-cols-2 gap-4">
                    <div onclick="selectPropertyType('residential', 0.15)" class="property-card cursor-pointer border-2 border-gray-200 rounded-xl p-6 hover:border-purple-400 transition">
                        <div class="text-4xl mb-3">🏠</div>
                        <h3 class="text-xl font-semibold mb-2">Residential</h3>
                        <p class="text-gray-600 text-sm">Homes, Apartments, Condos</p>
                        <p class="text-purple-600 font-semibold mt-2">Most Popular!</p>
                    </div>
                    <div onclick="selectPropertyType('commercial', 0.08)" class="property-card cursor-pointer border-2 border-gray-200 rounded-xl p-6 hover:border-purple-400 transition">
                        <div class="text-4xl mb-3">🏢</div>
                        <h3 class="text-xl font-semibold mb-2">Commercial</h3>
                        <p class="text-gray-600 text-sm">Offices, Retail, Warehouses</p>
                        <p class="text-green-600 font-semibold mt-2">Best Value!</p>
                    </div>
                    <div onclick="selectPropertyType('medical', 0.12)" class="property-card cursor-pointer border-2 border-gray-200 rounded-xl p-6 hover:border-purple-400 transition">
                        <div class="text-4xl mb-3">🏥</div>
                        <h3 class="text-xl font-semibold mb-2">Medical</h3>
                        <p class="text-gray-600 text-sm">Clinics, Dental, Medical Offices</p>
                        <p class="text-blue-600 font-semibold mt-2">Specialized Cleaning</p>
                    </div>
                    <div onclick="selectPropertyType('restaurant', 0.10)" class="property-card cursor-pointer border-2 border-gray-200 rounded-xl p-6 hover:border-purple-400 transition">
                        <div class="text-4xl mb-3">🍽️</div>
                        <h3 class="text-xl font-semibold mb-2">Restaurant</h3>
                        <p class="text-gray-600 text-sm">Restaurants, Cafes, Kitchens</p>
                        <p class="text-orange-600 font-semibold mt-2">Health Code Compliant</p>
                    </div>
                </div>
            </div>

            <!-- Step 2: Size and Rooms -->
            <div id="step2" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">Tell Us About Your Space 📏</h2>
                <p class="text-gray-600 mb-8">The more we know, the better we can serve you!</p>

                <div class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Approximate Square Footage</label>
                        <input type="range" id="sqft-slider" min="500" max="10000" value="2000" oninput="updateSqft(this.value)"
                            class="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer">
                        <div class="flex justify-between text-sm text-gray-600 mt-2">
                            <span>500 sq ft</span>
                            <span id="sqft-display" class="text-2xl font-bold text-purple-600">2000 sq ft</span>
                            <span>10,000 sq ft</span>
                        </div>
                        <p class="text-xs text-gray-500 mt-2">
                            This helps us estimate the time and resources needed for your space
                        </p>
                    </div>

                    <div id="room-details" class="space-y-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Number of Rooms (Approximate)</label>
                        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                            <div>
                                <label class="text-sm text-gray-600">Bedrooms</label>
                                <select id="bedrooms" class="w-full p-2 border rounded-lg">
                                    <option value="0">0</option>
                                    <option value="1">1</option>
                                    <option value="2" selected>2</option>
                                    <option value="3">3</option>
                                    <option value="4">4</option>
                                    <option value="5">5+</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-sm text-gray-600">Bathrooms</label>
                                <select id="bathrooms" class="w-full p-2 border rounded-lg">
                                    <option value="1">1</option>
                                    <option value="2" selected>2</option>
                                    <option value="3">3</option>
                                    <option value="4">4+</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-sm text-gray-600">Kitchen</label>
                                <select id="kitchen" class="w-full p-2 border rounded-lg">
                                    <option value="1" selected>Yes</option>
                                    <option value="0">No</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <button onclick="nextStep()" class="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition">
                    Continue →
                </button>
            </div>

            <!-- Step 3: Property Photos -->
            <div id="step3" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">Show Us Your Space 📸</h2>
                <p class="text-gray-600 mb-2">Upload photos to help us provide a more accurate estimate</p>
                <p class="text-sm text-red-600 mb-6">Required: Photos help us assess the actual cleaning needs</p>

                <div class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center">
                    <div class="text-4xl mb-4">📷</div>
                    <p class="text-gray-600 mb-4">Upload photos of areas to be cleaned</p>

                    <input type="file" id="photo-upload" accept="image/*" multiple onchange="handlePhotoUpload(event)" class="hidden">
                    <label for="photo-upload" class="bg-purple-600 text-white px-6 py-3 rounded-lg cursor-pointer hover:bg-purple-700 transition inline-block">
                        Choose Photos
                    </label>

                    <p class="text-xs text-gray-500 mt-4">
                        Upload 3-10 photos showing different areas (living spaces, kitchen, bathrooms, etc.)
                    </p>
                </div>

                <div id="photo-preview" class="grid grid-cols-4 gap-4 mt-6"></div>

                <div class="bg-blue-50 border border-blue-300 rounded-lg p-4 mt-6">
                    <p class="text-sm text-blue-800">
                        <strong>Why photos matter:</strong> They help us identify special cleaning requirements,
                        assess current condition, and provide you with the most accurate pricing possible.
                    </p>
                </div>

                <button onclick="nextStep()" class="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition">
                    Continue →
                </button>
            </div>

            <!-- Step 4: Services Needed -->
            <div id="step4" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">What Services Do You Need? ✨</h2>
                <p class="text-gray-600 mb-8">Select all that apply - we do it all!</p>

                <div class="grid md:grid-cols-2 gap-4">
                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="vacuum" class="sr-only peer" checked>
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🔌</span>
                                <div>
                                    <div class="font-semibold">Vacuum & Carpets</div>
                                    <div class="text-sm text-gray-600">All carpeted areas</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="mop" class="sr-only peer" checked>
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🧽</span>
                                <div>
                                    <div class="font-semibold">Mopping & Floors</div>
                                    <div class="text-sm text-gray-600">All hard floor surfaces</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="bathroom" class="sr-only peer" checked>
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🚿</span>
                                <div>
                                    <div class="font-semibold">Bathroom Deep Clean</div>
                                    <div class="text-sm text-gray-600">Sanitize & disinfect</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="kitchen" class="sr-only peer" checked>
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🍳</span>
                                <div>
                                    <div class="font-semibold">Kitchen Deep Clean</div>
                                    <div class="text-sm text-gray-600">Appliances, counters, sink</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="windows" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🪟</span>
                                <div>
                                    <div class="font-semibold">Window Cleaning</div>
                                    <div class="text-sm text-gray-600">Interior windows</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="laundry" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">👔</span>
                                <div>
                                    <div class="font-semibold">Laundry Service</div>
                                    <div class="text-sm text-gray-600">Wash & fold service</div>
                                </div>
                            </div>
                        </div>
                    </label>
                </div>

                <button onclick="nextStep()" class="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition">
                    Continue →
                </button>
            </div>

            <!-- Step 5: Frequency -->
            <div id="step5" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">How Often? 📅</h2>
                <p class="text-gray-600 mb-8">Choose your preferred cleaning schedule</p>

                <div class="space-y-4">
                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="weekly" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">Weekly Service</div>
                                    <div class="text-gray-600">Perfect for busy offices and high-traffic areas</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-2xl font-bold text-green-600">MOST THOROUGH</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="bi-weekly" class="sr-only peer" checked>
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">Bi-Weekly Service</div>
                                    <div class="text-gray-600">Great balance of cleanliness and value</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-xl font-bold text-purple-600">MOST POPULAR</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="monthly" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">Monthly Service</div>
                                    <div class="text-gray-600">Ideal for regular maintenance cleaning</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="one-time" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">One-Time Deep Clean</div>
                                    <div class="text-gray-600">Perfect for special occasions or move-in/out</div>
                                </div>
                            </div>
                        </div>
                    </label>
                </div>

                <button onclick="nextStep()" class="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition">
                    Continue to Contact Info →
                </button>
            </div>

            <!-- Step 6: Contact Info & Location -->
            <div id="step6" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">Almost Done! 🎉</h2>

                <!-- Personal Service Notice -->
                <div class="bg-blue-50 border-2 border-blue-400 rounded-xl p-4 mb-6">
                    <div class="flex items-start">
                        <span class="text-xl mr-2">✨</span>
                        <div>
                            <h3 class="font-bold text-blue-800">Personalized Quote Coming Your Way!</h3>
                            <p class="text-sm text-blue-700 mt-1">
                                We believe every space is unique and deserves a customized cleaning plan.
                            </p>
                            <ul class="text-sm text-blue-700 mt-2 space-y-1">
                                <li>✅ Our team will review your requirements within 24 hours</li>
                                <li>✅ We'll contact you to schedule a FREE on-site assessment</li>
                                <li>✅ You'll receive a detailed, personalized quote</li>
                                <li>✅ No surprises - transparent pricing tailored to your needs</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <p class="text-gray-600 mb-6">Please provide your contact information so we can prepare your personalized quote:</p>

                <form method="POST" action="/quote-submit" enctype="multipart/form-data" class="space-y-4">
                    <input type="hidden" id="final-property-type" name="property_type">
                    <input type="hidden" id="final-sqft" name="sqft">
                    <input type="hidden" id="final-services" name="services">
                    <input type="hidden" id="final-frequency" name="frequency">
                    <input type="hidden" id="uploaded-photos" name="photos">

                    <div class="grid md:grid-cols-2 gap-4">
                        <input type="text" name="name" placeholder="Your Name" required
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">
                        <input type="tel" name="phone" placeholder="Phone Number" required
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">
                    </div>

                    <input type="email" name="email" placeholder="Email Address" required
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">

                    <!-- Location Field -->
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            📍 Service Location
                        </label>
                        <input type="text" name="city" placeholder="City (e.g., Boston, Cambridge, Quincy)" required
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 mb-2">
                        <input type="text" name="address" placeholder="Full Address (Street, City, State, ZIP)" required
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">
                        <p class="text-xs text-gray-600 mt-2">
                            Your location helps us assign the best team for your area.
                        </p>
                    </div>

                    <!-- Additional Information -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Additional Information (Optional)
                        </label>
                        <textarea name="additional_info" rows="3"
                            placeholder="Tell us about any specific cleaning needs, preferred times, or special requirements..."
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600"></textarea>
                    </div>

                    <div class="flex items-start mb-4">
                        <input type="checkbox" id="agree-terms" required class="mt-1 mr-2">
                        <label for="agree-terms" class="text-sm text-gray-600">
                            I understand that I will receive a personalized quote after an assessment, and there is no obligation to proceed with services.
                        </label>
                    </div>

                    <button type="submit" class="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-4 rounded-lg font-bold text-lg hover:shadow-lg transition">
                        Request Your Free Quote 📋
                    </button>
                </form>

                <div class="mt-6 text-center text-xs text-gray-600">
                    <p>✅ Free consultation &nbsp; ✅ No obligation &nbsp; ✅ Personalized service plan</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentStep = 1;
        let totalSteps = 6;
        let uploadedPhotos = [];
        let quoteData = {{
            propertyType: '',
            baseRate: 0,
            sqft: 2000,
            services: [],
            frequency: 'bi-weekly',
            rooms: {{ bedrooms: 2, bathrooms: 2 }},
            photos: []
        }};

        function handlePhotoUpload(event) {{
            const files = event.target.files;
            const preview = document.getElementById('photo-preview');
            preview.innerHTML = '';
            uploadedPhotos = [];

            for (let i = 0; i < files.length && i < 10; i++) {{
                const file = files[i];
                const reader = new FileReader();

                reader.onload = function(e) {{
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'photo-preview border-2 border-gray-300';
                    preview.appendChild(img);
                    uploadedPhotos.push(e.target.result);
                }};

                reader.readAsDataURL(file);
            }}

            quoteData.photos = uploadedPhotos;
        }}

        function selectPropertyType(type, rate) {{
            document.querySelectorAll('.property-card').forEach(card => card.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            quoteData.propertyType = type;
            quoteData.baseRate = rate;

            document.getElementById('room-details').style.display = type === 'residential' ? 'block' : 'none';
            setTimeout(() => nextStep(), 500);
        }}

        function updateSqft(value) {{
            document.getElementById('sqft-display').textContent = value + ' sq ft';
            quoteData.sqft = parseInt(value);
            updatePrice();
        }}

        function nextStep() {{
            if (currentStep < totalSteps) {{
                document.getElementById('step' + currentStep).classList.remove('active');
                currentStep++;
                document.getElementById('step' + currentStep).classList.add('active');

                const progress = (currentStep / totalSteps) * 100;
                document.getElementById('progress-bar').style.width = progress + '%';
                document.getElementById('progress-text').textContent = 'Step ' + currentStep + ' of ' + totalSteps;

                if (currentStep === totalSteps) {{
                    // Prepare final data without pricing
                    document.getElementById('final-property-type').value = quoteData.propertyType;
                    document.getElementById('final-sqft').value = quoteData.sqft;
                    document.getElementById('final-services').value = getSelectedServices().join(',');
                    document.getElementById('final-frequency').value = getSelectedFrequency();
                    document.getElementById('uploaded-photos').value = JSON.stringify(uploadedPhotos);
                }}
            }}
        }}

        function getSelectedServices() {{
            const services = [];
            document.querySelectorAll('.service-option input:checked').forEach(input => {{
                services.push(input.value);
            }});
            return services;
        }}

        function getSelectedFrequency() {{
            const checked = document.querySelector('input[name="frequency"]:checked');
            return checked ? checked.value : 'bi-weekly';
        }}

        // Simplified functions without pricing
        function updateSqft(value) {{
            document.getElementById('sqft-display').textContent = value + ' sq ft';
            quoteData.sqft = parseInt(value);
        }}

        function selectPropertyType(type, rate) {{
            document.querySelectorAll('.property-card').forEach(card => card.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            quoteData.propertyType = type;
            quoteData.baseRate = rate;

            document.getElementById('room-details').style.display = type === 'residential' ? 'block' : 'none';
            setTimeout(() => nextStep(), 500);
        }}
    </script>
</body>
</html>
    '''

# Complete Flask Quote Route - Replace your existing /quote-submit route with this

@app.route('/quote-submit', methods=['POST'])
def quote_submit():
    """Submit quote to Google Sheets matching exact Apps Script structure"""
    try:
        # Generate quote ID matching Apps Script format
        quote_id = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Collect all form data with proper defaults
        form_data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'state': 'MA',  # Default to Massachusetts
            'zip': request.form.get('zip', '').strip(),
            'property_type': request.form.get('property_type', 'commercial'),
            'sqft': float(request.form.get('sqft', 2000)),
            'services': request.form.get('services', ''),
            'frequency': request.form.get('frequency', 'monthly'),
            'additional_info': request.form.get('additional_info', ''),
            'bedrooms': int(request.form.get('bedrooms', 0)),
            'bathrooms': int(request.form.get('bathrooms', 2)),
            'kitchen': int(request.form.get('kitchen', 1))
        }

        # ==================== PROPERTY DATA STRUCTURE ====================
        # This must match the Google Apps Script properties structure exactly
        properties_data = [{
            'id': 1,
            'name': f"{form_data['property_type'].title()} Property",
            'facilityType': form_data['property_type'],
            'squareFeet': form_data['sqft'],
            'restrooms': form_data['bathrooms'],
            'windows': 10,  # Default estimate
            'rooms': form_data['bedrooms'] + form_data['bathrooms'] + form_data['kitchen'],
            'floors': 1
        }]

        # ==================== MATERIALS DATA STRUCTURE ====================
        # Parse selected materials/supplies from the form
        materials_data = []
        if 'vacuum' in form_data['services']:
            materials_data.append({
                'id': 'MAT001',
                'quantity': 1
            })

        # ==================== SERVICES DATA STRUCTURE ====================
        # Parse selected services from the form
        services_data = []
        services_list = form_data['services'].split(',') if form_data['services'] else []

        service_mapping = {
            'vacuum': {'id': 'SRV001', 'name': 'Vacuum Service'},
            'mop': {'id': 'SRV002', 'name': 'Mopping Service'},
            'bathroom': {'id': 'SRV010', 'name': 'Restroom Deep Clean'},
            'kitchen': {'id': 'SRV009', 'name': 'Kitchen Deep Clean'},
            'windows': {'id': 'SRV002', 'name': 'Window Washing'},
            'laundry': {'id': 'SRV008', 'name': 'Supply Restocking'}
        }

        for service_key in services_list:
            service_key = service_key.strip()
            if service_key in service_mapping:
                services_data.append({
                    'id': service_mapping[service_key]['id'],
                    'quantity': 1
                })

        # ==================== PRICING CALCULATIONS ====================
        # Get base rate from property type
        base_rates = {
            'office': 0.05,
            'medical': 0.08,
            'retail': 0.04,
            'restaurant': 0.06,
            'warehouse': 0.03,
            'school': 0.04,
            'residential': 0.06,
            'industrial': 0.035,
            'gym': 0.045,
            'bank': 0.055,
            'church': 0.04,
            'government': 0.065
        }

        # Service type multipliers
        service_multipliers = {
            'regular': 1.0,
            'deep-clean': 2.0,
            'post-construction': 2.5,
            'move-in-out': 1.8,
            'disinfection': 1.5,
            'emergency': 3.0,
            'one-time': 1.3
        }

        # Frequency discounts
        frequency_discounts = {
            'one-time': 0,
            'daily': 0.25,
            'weekly': 0.20,
            'bi-weekly': 0.15,
            'monthly': 0.10,
            'quarterly': 0.05
        }

        # Calculate base pricing
        base_rate = base_rates.get(form_data['property_type'], 0.05)
        service_multiplier = service_multipliers.get('regular', 1.0)  # Default to regular
        frequency_discount = frequency_discounts.get(form_data['frequency'], 0)

        # Property base cost
        property_cost = form_data['sqft'] * base_rate * service_multiplier
        property_cost = property_cost * (1 - frequency_discount)

        # Labor calculations
        labor_hours = max(2, form_data['sqft'] / 3000)  # Estimate hours based on sqft
        labor_rate = 25  # $25/hour default
        labor_cost = labor_hours * labor_rate

        # Material cost estimate
        material_cost = form_data['sqft'] * 0.01  # $0.01 per sqft for supplies

        # Service cost additions
        service_cost = 0
        if 'windows' in services_list:
            service_cost += 30
        if 'laundry' in services_list:
            service_cost += 40
        if 'bathroom' in services_list:
            service_cost += form_data['bathrooms'] * 25
        if 'kitchen' in services_list:
            service_cost += 50

        # Travel cost (if provided mileage)
        travel_cost = 0  # Can be calculated if distance is known

        # Calculate totals
        base_cost = property_cost + labor_cost + material_cost + service_cost + travel_cost

        # Apply minimum charge
        minimum_charge = 75
        base_cost = max(base_cost, minimum_charge)

        # Profit and tax calculations
        profit_margin = 35  # 35% default profit margin
        profit_amount = base_cost * (profit_margin / 100)
        subtotal = base_cost + profit_amount
        tax_rate = 0.0625  # 6.25% MA sales tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount

        # ==================== CREATE GOOGLE SHEETS ROW ====================
        # This MUST be exactly 37 columns in the exact order
        sheet_row = [
            quote_id,                                              # 1. ID
            datetime.now().isoformat(),                           # 2. Date_Created
            form_data['name'],                                    # 3. Customer_Name
            form_data['email'],                                   # 4. Customer_Email
            form_data['phone'],                                   # 5. Customer_Phone
            form_data['address'],                                 # 6. Customer_Address
            form_data['city'],                                    # 7. Customer_City
            form_data['state'],                                   # 8. Customer_State
            form_data['zip'],                                     # 9. Customer_Zip
            json.dumps(properties_data),                          # 10. Properties (JSON string)
            json.dumps(materials_data),                           # 11. Materials (JSON string)
            json.dumps(services_data),                            # 12. Services (JSON string)
            json.dumps([]),                                       # 13. Employees (empty array)
            round(labor_hours, 2),                                # 14. Labor_Hours
            round(labor_cost, 2),                                 # 15. Labor_Cost
            round(material_cost, 2),                              # 16. Material_Cost
            round(service_cost, 2),                               # 17. Service_Cost
            round(travel_cost, 2),                                # 18. Travel_Cost
            round(base_cost, 2),                                  # 19. Base_Cost
            profit_margin,                                        # 20. Profit_Margin
            round(profit_amount, 2),                              # 21. Profit_Amount
            round(subtotal, 2),                                   # 22. Subtotal
            round(tax_amount, 2),                                 # 23. Tax_Amount
            round(total_amount, 2),                               # 24. Total_Amount
            'pending',                                            # 25. Status (MUST be 'pending')
            (datetime.now() + timedelta(days=30)).isoformat(),   # 26. Valid_Until (30 days from now)
            form_data.get('additional_info', ''),                # 27. Notes (customer visible)
            f"Web quote from {form_data['property_type']} property - {form_data['sqft']} sqft - {form_data['frequency']} service", # 28. Internal_Notes
            'Web Form',                                           # 29. Created_By
            '',                                                    # 30. Assigned_To (empty for now)
            '',                                                    # 31. Follow_Up_Date (empty for now)
            '',                                                    # 32. Customer_ID (empty, will be assigned if converted)
            '',                                                    # 33. Converted_Date (empty until accepted)
            '',                                                    # 34. Decline_Reason (empty unless declined)
            'regular',                                            # 35. Service_Type
            form_data['frequency'],                              # 36. Frequency
            0                                                      # 37. Mileage
        ]

        # ==================== SAVE TO GOOGLE SHEETS ====================
        print(f"Submitting quote {quote_id} with {len(sheet_row)} columns")

        # Validate we have exactly 37 columns
        if len(sheet_row) != 37:
            raise ValueError(f"Quote data must have exactly 37 columns, got {len(sheet_row)}")

        # Save to Google Sheets via the database module
        result = db.add_quote_full(sheet_row)

        if not result.get('success'):
            # Log error but continue to show confirmation to user
            print(f"Warning: Failed to save to Google Sheets: {result.get('error')}")
            flash('Quote submitted but there was an issue saving. Our team will contact you.', 'warning')
        else:
            print(f"Quote {quote_id} successfully saved to Google Sheets")

        # ==================== STORE SESSION DATA FOR CONFIRMATION ====================
        session['quote_result'] = {
            'quote_id': quote_id,
            'name': form_data['name'],
            'email': form_data['email'],
            'phone': form_data['phone'],
            'property_type': form_data['property_type'],
            'sqft': form_data['sqft'],
            'services': ', '.join(services_list) if services_list else 'Basic Cleaning',
            'frequency': form_data['frequency'],
            'city': form_data['city'],
            'address': form_data['address'],
            'estimated_price': f"${round(total_amount, 2):,.2f}",
            'status': 'pending',
            'base_cost': f"${round(base_cost, 2):,.2f}",
            'profit': f"${round(profit_amount, 2):,.2f}",
            'tax': f"${round(tax_amount, 2):,.2f}"
        }

        # ==================== SEND NOTIFICATION EMAIL (OPTIONAL) ====================
        try:
            # You can add email notification here if needed
            # Example: send_admin_notification(quote_id, form_data, total_amount)
            pass
        except Exception as e:
            print(f"Email notification failed: {e}")
            # Don't fail the whole process for email issues

        return redirect('/quote-result')

    except ValueError as ve:
        print(f"Validation error in quote submission: {ve}")
        flash(f'There was a validation error: {str(ve)}', 'error')
        return redirect('/quote')

    except Exception as e:
        print(f"Error in quote submission: {e}")
        import traceback
        traceback.print_exc()

        # Still try to show confirmation even if save failed
        session['quote_result'] = {
            'quote_id': f"TEMP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': request.form.get('name', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'property_type': request.form.get('property_type', 'commercial'),
            'sqft': request.form.get('sqft', '0'),
            'frequency': request.form.get('frequency', 'monthly'),
            'status': 'error',
            'error_message': 'There was an issue processing your quote, but we received your information. Our team will contact you shortly.'
        }

        return redirect('/quote-result')


# ==================== HELPER FUNCTION FOR TESTING ====================
@app.route('/test-quote-structure')
def test_quote_structure():
    """Test endpoint to verify the quote structure matches Google Sheets"""
    test_data = {
        'name': 'Test Customer',
        'email': 'test@example.com',
        'phone': '555-0123',
        'address': '123 Test St',
        'city': 'Boston',
        'property_type': 'office',
        'sqft': 2500,
        'frequency': 'weekly'
    }

    # Generate test quote structure
    quote_id = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"

    properties = [{
        'id': 1,
        'name': 'Test Office',
        'facilityType': 'office',
        'squareFeet': 2500,
        'restrooms': 2,
        'windows': 10,
        'rooms': 5,
        'floors': 1
    }]

    test_row = [
        quote_id,                                    # 1. ID
        datetime.now().isoformat(),                  # 2. Date_Created
        test_data['name'],                          # 3. Customer_Name
        test_data['email'],                         # 4. Customer_Email
        test_data['phone'],                         # 5. Customer_Phone
        test_data['address'],                       # 6. Customer_Address
        test_data['city'],                          # 7. Customer_City
        'MA',                                        # 8. Customer_State
        '02101',                                     # 9. Customer_Zip
        json.dumps(properties),                     # 10. Properties
        '[]',                                        # 11. Materials
        '[]',                                        # 12. Services
        '[]',                                        # 13. Employees
        2.5,                                         # 14. Labor_Hours
        62.50,                                       # 15. Labor_Cost
        25.00,                                       # 16. Material_Cost
        0,                                           # 17. Service_Cost
        0,                                           # 18. Travel_Cost
        187.50,                                      # 19. Base_Cost
        35,                                          # 20. Profit_Margin
        65.63,                                       # 21. Profit_Amount
        253.13,                                      # 22. Subtotal
        15.82,                                       # 23. Tax_Amount
        268.95,                                      # 24. Total_Amount
        'pending',                                   # 25. Status
        (datetime.now() + timedelta(days=30)).isoformat(), # 26. Valid_Until
        'Test quote',                                # 27. Notes
        'Internal test',                             # 28. Internal_Notes
        'Test System',                               # 29. Created_By
        '',                                          # 30. Assigned_To
        '',                                          # 31. Follow_Up_Date
        '',                                          # 32. Customer_ID
        '',                                          # 33. Converted_Date
        '',                                          # 34. Decline_Reason
        'regular',                                   # 35. Service_Type
        'weekly',                                    # 36. Frequency
        0                                            # 37. Mileage
    ]

    return jsonify({
        'column_count': len(test_row),
        'expected_columns': 37,
        'matches': len(test_row) == 37,
        'data': test_row
    })

@app.route('/quote-result')
def quote_result():
    result = session.get('quote_result')
    if not result:
        return redirect('/quote')

    # Clear the session data after displaying
    session.pop('quote_result', None)

    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quote Request Received - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-green-50 to-blue-50 min-h-screen flex items-center">
    <div class="max-w-2xl mx-auto px-4 w-full">
        <div class="bg-white rounded-3xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">✅</div>
            <h2 class="text-3xl font-bold mb-2">Quote Request Received!</h2>
            <p class="text-gray-600 mb-6">Thank you for choosing Baez Cleaning Services</p>

            <div class="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl p-8 mb-6">
                <div class="text-lg mb-2">Request ID: <strong>{result['quote_id']}</strong></div>
                <div class="text-sm mb-4">Status: <span class="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full">PENDING REVIEW</span></div>

                <div class="mt-4 text-white/90">
                    <p class="text-lg mb-2">We're preparing your personalized quote for:</p>
                    <div class="bg-white/10 rounded-lg p-4 mt-3">
                        <div class="text-xl font-bold">{result['property_type'].title()} Property</div>
                        <div>{result['sqft']} Square Feet</div>
                        <div>{result['frequency'].replace('-', ' ').title()} Service</div>
                    </div>
                </div>
            </div>

            <div class="bg-blue-50 border border-blue-300 rounded-lg p-4 mb-6">
                <h3 class="font-bold text-blue-900 mb-2">What Happens Next?</h3>
                <div class="text-left space-y-2 text-sm text-blue-800">
                    <div class="flex items-start">
                        <span class="text-green-500 mr-2">✓</span>
                        <div>
                            <strong>Within 24 Hours:</strong> Our team will review your requirements and contact you
                        </div>
                    </div>
                    <div class="flex items-start">
                        <span class="text-green-500 mr-2">✓</span>
                        <div>
                            <strong>Free Assessment:</strong> We'll schedule a quick on-site visit at your convenience
                        </div>
                    </div>
                    <div class="flex items-start">
                        <span class="text-green-500 mr-2">✓</span>
                        <div>
                            <strong>Personalized Quote:</strong> Receive a detailed quote tailored to your exact needs
                        </div>
                    </div>
                    <div class="flex items-start">
                        <span class="text-green-500 mr-2">✓</span>
                        <div>
                            <strong>No Obligation:</strong> Review your quote with zero pressure to commit
                        </div>
                    </div>
                </div>
            </div>

            <div class="space-y-3">
                <div class="bg-purple-50 rounded-lg p-4">
                    <p class="text-purple-900 font-semibold mb-2">Need Immediate Assistance?</p>
                    <a href="tel:{BUSINESS_PHONE}" class="block w-full bg-purple-600 text-white py-3 rounded-lg font-bold text-lg hover:bg-purple-700 transition">
                        📞 Call Us Now: {BUSINESS_PHONE}
                    </a>
                </div>

                <p class="text-sm text-gray-600">
                    We'll contact you at <strong>{result['email']}</strong> and <strong>{result['phone']}</strong>
                </p>

                <a href="/" class="block w-full bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition">
                    Return to Homepage
                </a>
            </div>

            <div class="mt-6 pt-6 border-t border-gray-200">
                <p class="text-xs text-gray-500">
                    Quote requests are typically processed within 1-2 business days.
                    Our business hours are Monday-Saturday 8AM-6PM EST.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    '''.format(
        BUSINESS_NAME=BUSINESS_NAME,
        BUSINESS_PHONE=BUSINESS_PHONE,
        result=result
    )

@app.route('/login')
def login():
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-50 to-pink-50 min-h-screen flex items-center">
    <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-4xl font-bold text-center mb-12">Staff Portal</h2>

        <div class="grid md:grid-cols-2 gap-8">
            <!-- Admin Portal -->
            <div class="bg-white rounded-2xl shadow-xl p-8 transform transition hover:scale-105">
                <div class="text-5xl mb-4 text-center">👨‍💼</div>
                <h3 class="text-2xl font-bold text-center mb-4">Admin Portal</h3>
                <p class="text-gray-600 text-center mb-6">
                    Manage your business, employees, and settings
                </p>
                <a href="/admin-login"
                    class="block w-full bg-red-500 text-white py-3 rounded-lg text-center hover:bg-red-600 transition">
                    Admin Login
                </a>
            </div>

            <!-- Employee Portal -->
            <div class="bg-white rounded-2xl shadow-xl p-8 transform transition hover:scale-105">
                <div class="text-5xl mb-4 text-center">👷</div>
                <h3 class="text-2xl font-bold text-center mb-4">Employee Portal</h3>
                <p class="text-gray-600 text-center mb-6">
                    View schedule, manage jobs, track hours
                </p>
                <a href="/employee-login"
                    class="block w-full bg-green-500 text-white py-3 rounded-lg text-center hover:bg-green-600 transition">
                    Employee Login
                </a>
            </div>
        </div>

        <div class="text-center mt-8">
            <a href="/" class="text-gray-600 hover:text-gray-800">← Back to Home</a>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        employee = db.verify_employee(username, password)
        if employee:
            session['employee'] = employee
            session['user_type'] = 'employee'
            return redirect('/employee-dashboard')

    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Employee Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-green-50 to-blue-50 min-h-screen flex items-center">
    <div class="max-w-md mx-auto px-4 w-full">
        <div class="bg-white rounded-2xl shadow-xl p-8">
            <div class="text-center mb-8">
                <div class="text-5xl mb-4">👷</div>
                <h2 class="text-3xl font-bold">Employee Login</h2>
            </div>
            <form method="POST" class="space-y-6">
                <input type="text" name="username" placeholder="Username" required
                    class="w-full px-4 py-3 border rounded-lg">
                <input type="password" name="password" placeholder="Password" required
                    class="w-full px-4 py-3 border rounded-lg">
                <button type="submit" class="w-full bg-green-500 text-white py-3 rounded-lg font-semibold">
                    Login
                </button>
            </form>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/employee-dashboard')
def employee_dashboard():
    if 'employee' not in session or session.get('user_type') != 'employee':
        flash('Please log in to access the dashboard.', 'error')
        return redirect('/employee-login')

    employee = session['employee']

    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Employee Dashboard - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="bg-white shadow p-4">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-bold">Welcome, {employee['Name']}!</h1>
            <div class="flex space-x-2">
                <span class="text-gray-600">Employee Portal</span>
                <a href="/logout" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition">Logout</a>
            </div>
        </div>

        <div class="p-8">
            <div class="grid md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="text-gray-600 text-sm">Today's Jobs</div>
                    <div class="text-3xl font-bold text-green-600">3</div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="text-gray-600 text-sm">This Week</div>
                    <div class="text-3xl font-bold text-blue-600">12</div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="text-gray-600 text-sm">Hours Worked</div>
                    <div class="text-3xl font-bold text-purple-600">32.5</div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold mb-4">Today's Schedule</h2>
                <div class="space-y-3">
                    <div class="border-l-4 border-green-500 pl-4 py-2">
                        <div class="font-semibold">9:00 AM - Smith Residence</div>
                        <div class="text-gray-600 text-sm">123 Main St - Regular Cleaning</div>
                    </div>
                    <div class="border-l-4 border-blue-500 pl-4 py-2">
                        <div class="font-semibold">1:00 PM - Johnson Office</div>
                        <div class="text-gray-600 text-sm">456 Business Ave - Deep Clean</div>
                    </div>
                    <div class="border-l-4 border-purple-500 pl-4 py-2">
                        <div class="font-semibold">4:00 PM - Brown Apartment</div>
                        <div class="text-gray-600 text-sm">789 Oak St - Move-out Cleaning</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/logout')

def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)