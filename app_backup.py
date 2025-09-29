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

# Enhanced Homepage with Chatbot and Video
@app.route('/')
def index():
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{BUSINESS_NAME} - Professional Cleaning Services</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
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
    </style>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <span class="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                        🧹 {BUSINESS_NAME}
                    </span>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="tel:{BUSINESS_PHONE}" class="text-gray-600 hover:text-purple-600 hidden md:block">
                        📞 {BUSINESS_PHONE}
                    </a>
                    <a href="/quote" class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-full font-medium pulse-animation">
                        Get Free Quote
                    </a>
                    <!-- Staff Login Button -->
                    <a href="/login" class="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition flex items-center space-x-1">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                        </svg>
                        <span>Staff</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="gradient-bg text-white">
        <div class="max-w-7xl mx-auto px-4 py-24 sm:px-6 lg:px-8">
            <div class="text-center">
                <h1 class="text-5xl md:text-6xl font-bold mb-6">Your Space, Spotlessly Clean</h1>
                <p class="text-xl mb-2 opacity-90">Professional Cleaning Services for Homes & Businesses</p>
                <p class="text-lg mb-8 opacity-80">Licensed • Insured • Satisfaction Guaranteed</p>
                <div class="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
                    <a href="/quote" class="bg-white text-purple-700 px-8 py-4 rounded-full font-semibold text-lg hover:shadow-xl transition transform hover:scale-105 w-full sm:w-auto">
                        Get Instant Quote →
                    </a>
                    <a href="tel:{BUSINESS_PHONE}" class="border-2 border-white text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white hover:text-purple-700 transition w-full sm:w-auto">
                        📞 Call Now
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Trust Indicators -->
    <div class="bg-white py-8 border-b">
        <div class="max-w-7xl mx-auto px-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                    <div class="text-3xl font-bold text-purple-600">500+</div>
                    <div class="text-sm text-gray-600">Happy Customers</div>
                </div>
                <div>
                    <div class="text-3xl font-bold text-purple-600">10+</div>
                    <div class="text-sm text-gray-600">Years Experience</div>
                </div>
                <div>
                    <div class="text-3xl font-bold text-purple-600">Licensed</div>
                    <div class="text-sm text-gray-600">& Insured</div>
                </div>
                <div>
                    <div class="text-3xl font-bold text-purple-600">100%</div>
                    <div class="text-sm text-gray-600">Satisfaction</div>
                </div>
            </div>
        </div>
    </div>

    <!-- What We Clean Section -->
    <div class="py-16 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold mb-4">We Clean Everything!</h2>
                <p class="text-xl text-gray-600">From small offices to large commercial spaces</p>
            </div>

            <div class="grid md:grid-cols-4 gap-6">
                <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-4xl mb-4">🏢</div>
                    <h3 class="text-xl font-semibold mb-2">Commercial Offices</h3>
                    <p class="text-gray-600 mb-3">Keep your workspace professional</p>
                    <ul class="text-sm text-gray-500 space-y-1">
                        <li>✓ Daily/Weekly Service</li>
                        <li>✓ Desk & Surface Cleaning</li>
                        <li>✓ Restroom Sanitization</li>
                        <li>✓ Trash Removal</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.08/sq ft</p>
                </div>

                <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-4xl mb-4">🏥</div>
                    <h3 class="text-xl font-semibold mb-2">Medical Facilities</h3>
                    <p class="text-gray-600 mb-3">Hospital-grade sanitization</p>
                    <ul class="text-sm text-gray-500 space-y-1">
                        <li>✓ EPA Approved Disinfectants</li>
                        <li>✓ Exam Room Cleaning</li>
                        <li>✓ Waiting Area Service</li>
                        <li>✓ Biohazard Protocols</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.12/sq ft</p>
                </div>

                <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-4xl mb-4">🏠</div>
                    <h3 class="text-xl font-semibold mb-2">Residential Homes</h3>
                    <p class="text-gray-600 mb-3">Your home, perfectly clean</p>
                    <ul class="text-sm text-gray-500 space-y-1">
                        <li>✓ Deep Cleaning</li>
                        <li>✓ Move In/Out Service</li>
                        <li>✓ Regular Maintenance</li>
                        <li>✓ Post-Construction</li>
                    </ul>
                    <p class="text-purple-600 font-bold mt-3">From $0.15/sq ft</p>
                </div>

                <div class="bg-white p-6 rounded-xl shadow-lg card-hover">
                    <div class="text-4xl mb-4">🍽️</div>
                    <h3 class="text-xl font-semibold mb-2">Restaurants</h3>
                    <p class="text-gray-600 mb-3">Food-safe & health compliant</p>
                    <ul class="text-sm text-gray-500 space-y-1">
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

    <!-- Professional Video Section -->
    <div class="py-16 bg-white">
        <div class="max-w-7xl mx-auto px-4">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold mb-4">See Us In Action</h2>
                <p class="text-xl text-gray-600">Professional cleaning that makes a difference</p>
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
                <div class="mt-8 text-center">
                    <p class="text-gray-600 mb-4">Watch how we transform spaces with our professional cleaning services</p>
                    <a href="/quote" class="inline-block bg-purple-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-purple-700 transition">
                        Get Your Free Quote →
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Contact Section -->
    <div class="gradient-bg text-white py-16">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <h2 class="text-3xl font-bold mb-8">Get In Touch</h2>
            <div class="grid md:grid-cols-3 gap-8">
                <div>
                    <div class="text-4xl mb-4">📞</div>
                    <h3 class="text-xl font-semibold mb-2">Call Us</h3>
                    <a href="tel:{BUSINESS_PHONE}" class="text-xl hover:underline">{BUSINESS_PHONE}</a>
                    <p class="text-sm mt-2 opacity-90">Mon-Sat: 8AM-6PM</p>
                </div>
                <div>
                    <div class="text-4xl mb-4">📧</div>
                    <h3 class="text-xl font-semibold mb-2">Email Us</h3>
                    <a href="mailto:{BUSINESS_EMAIL}" class="text-xl hover:underline">{BUSINESS_EMAIL}</a>
                    <p class="text-sm mt-2 opacity-90">24/7 Support</p>
                </div>
                <div>
                    <div class="text-4xl mb-4">📍</div>
                    <h3 class="text-xl font-semibold mb-2">Service Area</h3>
                    <p class="text-xl">Greater Boston Area</p>
                    <p class="text-sm mt-2 opacity-90">15 Mile Radius</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer with discrete staff login -->
    <footer class="bg-gray-900 text-gray-400 py-6">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center">
                <div class="text-sm">
                    © 2024 {BUSINESS_NAME}. All rights reserved.
                </div>
                <div class="text-xs">
                    <a href="/login" class="text-gray-500 hover:text-gray-400 transition">Staff Portal</a>
                </div>
            </div>
        </div>
    </footer>

<!-- AI Chatbot Widget -->
    <div id="chat-widget" class="fixed bottom-4 right-4 z-50">
        <!-- Chat Button with Better Icon -->
        <button id="chat-toggle" class="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all transform hover:scale-110">
            <!-- Chat bubble icon -->
            <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                <circle cx="8" cy="10" r="1"/>
                <circle cx="12" cy="10" r="1"/>
                <circle cx="16" cy="10" r="1"/>
            </svg>
            <span class="absolute -top-1 -right-1 bg-green-500 rounded-full w-3 h-3 animate-pulse"></span>
        </button>

        <!-- Chat Box -->
        <div id="chat-box" class="hidden absolute bottom-20 right-0 w-96 bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div class="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4">
                <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-2">
                        <div class="bg-white/20 rounded-full p-2">
                            <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="font-bold">Baez Assistant</h3>
                            <p class="text-xs opacity-90">✨ Always here to help</p>
                        </div>
                    </div>
                    <button id="chat-close" class="text-white/80 hover:text-white transition">
                        <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
            </div>

            <div id="chat-messages" class="h-96 overflow-y-auto p-4 space-y-3 bg-gray-50">
                <div class="bg-white p-4 rounded-xl shadow-sm">
                    <p class="text-sm font-medium text-purple-600 mb-2">👋 Welcome to Baez Cleaning!</p>
                    <p class="text-sm text-gray-700">I can help you with:</p>
                    <ul class="text-sm text-gray-600 mt-2 space-y-1">
                        <li>💰 Instant pricing information</li>
                        <li>🧹 Our cleaning services</li>
                        <li>📅 Scheduling & availability</li>
                        <li>📍 Service areas</li>
                        <li>✨ Cleaning tips & advice</li>
                    </ul>
                    <p class="text-sm text-gray-700 mt-3">What would you like to know?</p>
                </div>
            </div>

            <div class="border-t bg-white p-4">
                <div class="flex space-x-2">
                    <input
                        type="text"
                        id="chat-input"
                        placeholder="Type your question..."
                        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                        onkeypress="if(event.key === 'Enter') sendMessage()">
                    <button
                        onclick="sendMessage()"
                        class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                    <button onclick="quickQuestion('What are your prices?')"
                        class="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        💰 Pricing
                    </button>
                    <button onclick="quickQuestion('What services do you offer?')"
                        class="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        🧹 Services
                    </button>
                    <button onclick="quickQuestion('What areas do you serve?')"
                        class="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full hover:bg-purple-200 transition">
                        📍 Areas
                    </button>
                    <button onclick="quickQuestion('How do I schedule?')"
                        class="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full hover:bg-purple-200 transition">
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
                messageDiv.className = 'bg-purple-100 p-3 rounded-xl ml-8';
                messageDiv.innerHTML = `<p class="text-sm text-gray-800">👤 ${{text}}</p>`;
            }} else {{
                messageDiv.className = 'bg-white p-3 rounded-xl mr-8 shadow-sm';
                messageDiv.innerHTML = `<p class="text-sm text-gray-700">✨ ${{text}}</p>`;
            }}
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function addTypingIndicator() {{
            const id = 'typing-' + Date.now();
            const typingDiv = document.createElement('div');
            typingDiv.id = id;
            typingDiv.className = 'bg-white p-3 rounded-xl mr-8 shadow-sm';
            typingDiv.innerHTML = '<p class="text-sm text-gray-500">✨ <span class="inline-flex space-x-1"><span class="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></span><span class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></span><span class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></span></span></p>';
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

# Dynamic Quote Calculator
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
    </style>
</head>
<body class="bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-8">
        <!-- Progress Bar -->
        <div class="mb-8">
            <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Getting Started</span>
                <span id="progress-text">Step 1 of 5</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
                <div id="progress-bar" class="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-500" style="width: 20%"></div>
            </div>
        </div>

        <div class="bg-white rounded-3xl shadow-2xl p-8">
            <!-- Live Price Display -->
            <div class="fixed top-20 right-4 bg-white rounded-xl shadow-lg p-4 z-50 hidden md:block">
                <div class="text-sm text-gray-600">Your Estimate</div>
                <div id="live-price" class="text-3xl font-bold text-purple-600">$0</div>
                <div class="text-xs text-gray-500">per service</div>
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
                    </div>

                    <div id="room-details" class="space-y-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Number of Rooms</label>
                        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                            <div>
                                <label class="text-sm text-gray-600">Bedrooms</label>
                                <select id="bedrooms" onchange="updatePrice()" class="w-full p-2 border rounded-lg">
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
                                <select id="bathrooms" onchange="updatePrice()" class="w-full p-2 border rounded-lg">
                                    <option value="1">1</option>
                                    <option value="2" selected>2</option>
                                    <option value="3">3</option>
                                    <option value="4">4+</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-sm text-gray-600">Kitchen</label>
                                <select id="kitchen" onchange="updatePrice()" class="w-full p-2 border rounded-lg">
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

            <!-- Step 3: Services Needed -->
            <div id="step3" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">What Services Do You Need? ✨</h2>
                <p class="text-gray-600 mb-8">Select all that apply - we do it all!</p>

                <div class="grid md:grid-cols-2 gap-4">
                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="dusting" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🪶</span>
                                <div>
                                    <div class="font-semibold">Dusting & Surfaces</div>
                                    <div class="text-sm text-gray-600">All surfaces, furniture, fixtures</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="vacuum" onchange="updatePrice()" class="sr-only peer" checked>
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
                        <input type="checkbox" value="mop" onchange="updatePrice()" class="sr-only peer" checked>
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
                        <input type="checkbox" value="bathroom" onchange="updatePrice()" class="sr-only peer" checked>
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
                        <input type="checkbox" value="kitchen" onchange="updatePrice()" class="sr-only peer" checked>
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
                        <input type="checkbox" value="windows" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">🪟</span>
                                <div>
                                    <div class="font-semibold">Window Cleaning</div>
                                    <div class="text-sm text-gray-600">Interior windows (+$30)</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="laundry" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">👔</span>
                                <div>
                                    <div class="font-semibold">Laundry Service</div>
                                    <div class="text-sm text-gray-600">Wash & fold (+$40)</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="service-option cursor-pointer">
                        <input type="checkbox" value="organizing" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-lg p-4 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex items-center">
                                <span class="text-2xl mr-3">📦</span>
                                <div>
                                    <div class="font-semibold">Organizing</div>
                                    <div class="text-sm text-gray-600">Declutter & organize (+$50)</div>
                                </div>
                            </div>
                        </div>
                    </label>
                </div>

                <button onclick="nextStep()" class="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition">
                    Continue →
                </button>
            </div>

            <!-- Step 4: Frequency -->
            <div id="step4" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">How Often? 📅</h2>
                <p class="text-gray-600 mb-8">Regular service saves you money!</p>

                <div class="space-y-4">
                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="weekly" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">Weekly Service</div>
                                    <div class="text-gray-600">Best value - Save 30%!</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-2xl font-bold text-green-600">BEST DEAL</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="biweekly" onchange="updatePrice()" class="sr-only peer" checked>
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">Bi-Weekly Service</div>
                                    <div class="text-gray-600">Most popular - Save 20%!</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-xl font-bold text-purple-600">POPULAR</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="monthly" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">Monthly Service</div>
                                    <div class="text-gray-600">Regular maintenance - Save 10%</div>
                                </div>
                            </div>
                        </div>
                    </label>

                    <label class="cursor-pointer">
                        <input type="radio" name="frequency" value="onetime" onchange="updatePrice()" class="sr-only peer">
                        <div class="border-2 border-gray-200 rounded-xl p-6 peer-checked:border-purple-600 peer-checked:bg-purple-50 transition">
                            <div class="flex justify-between items-center">
                                <div>
                                    <div class="text-xl font-semibold">One-Time Deep Clean</div>
                                    <div class="text-gray-600">Perfect for special occasions</div>
                                </div>
                            </div>
                        </div>
                    </label>
                </div>

                <button onclick="nextStep()" class="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition">
                    Get My Quote →
                </button>
            </div>

            <!-- Step 5: Contact Info -->
            <div id="step5" class="step fade-in">
                <h2 class="text-3xl font-bold mb-2">Almost Done! 🎉</h2>
                <div class="bg-green-50 border-2 border-green-500 rounded-xl p-6 mb-6">
                    <div class="text-sm text-green-600 mb-1">Your Customized Quote</div>
                    <div id="final-price" class="text-5xl font-bold text-green-600 price-pop">$0</div>
                    <div class="text-green-600">per cleaning service</div>
                </div>

                <p class="text-gray-600 mb-6">Just need your contact info to send the detailed quote:</p>

                <form method="POST" action="/quote-submit" class="space-y-4">
                    <input type="hidden" id="final-property-type" name="property_type">
                    <input type="hidden" id="final-sqft" name="sqft">
                    <input type="hidden" id="final-services" name="services">
                    <input type="hidden" id="final-frequency" name="frequency">
                    <input type="hidden" id="final-price-value" name="price">

                    <div class="grid md:grid-cols-2 gap-4">
                        <input type="text" name="name" placeholder="Your Name" required
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">
                        <input type="tel" name="phone" placeholder="Phone Number" required
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">
                    </div>
                    <input type="email" name="email" placeholder="Email Address" required
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600">

                    <button type="submit" class="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-4 rounded-lg font-bold text-lg hover:shadow-lg transition">
                        Lock In This Price! 🔒
                    </button>
                </form>

                <div class="mt-6 text-center text-sm text-gray-600">
                    <p>✅ No hidden fees &nbsp; ✅ Cancel anytime &nbsp; ✅ 100% Satisfaction Guaranteed</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentStep = 1;
        let quoteData = {{
            propertyType: '',
            baseRate: 0,
            sqft: 2000,
            services: [],
            frequency: 'biweekly',
            rooms: {{ bedrooms: 2, bathrooms: 2 }}
        }};

        function selectPropertyType(type, rate) {{
            document.querySelectorAll('.property-card').forEach(card => card.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            quoteData.propertyType = type;
            quoteData.baseRate = rate;

            // Show/hide room details based on property type
            document.getElementById('room-details').style.display = type === 'residential' ? 'block' : 'none';

            setTimeout(() => nextStep(), 500);
        }}

        function updateSqft(value) {{
            document.getElementById('sqft-display').textContent = value + ' sq ft';
            quoteData.sqft = parseInt(value);
            updatePrice();
        }}

        function nextStep() {{
            if (currentStep < 5) {{
                document.getElementById('step' + currentStep).classList.remove('active');
                currentStep++;
                document.getElementById('step' + currentStep).classList.add('active');

                // Update progress bar
                const progress = (currentStep / 5) * 100;
                document.getElementById('progress-bar').style.width = progress + '%';
                document.getElementById('progress-text').textContent = 'Step ' + currentStep + ' of 5';

                // Update final step values
                if (currentStep === 5) {{
                    document.getElementById('final-price').textContent = document.getElementById('live-price').textContent;
                    document.getElementById('final-property-type').value = quoteData.propertyType;
                    document.getElementById('final-sqft').value = quoteData.sqft;
                    document.getElementById('final-services').value = getSelectedServices().join(',');
                    document.getElementById('final-frequency').value = getSelectedFrequency();
                    document.getElementById('final-price-value').value = calculatePrice();
                }}

                updatePrice();
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
            return checked ? checked.value : 'biweekly';
        }}

        function calculatePrice() {{
            let price = quoteData.sqft * quoteData.baseRate;

            // Room multipliers for residential
            if (quoteData.propertyType === 'residential') {{
                const bathrooms = parseInt(document.getElementById('bathrooms')?.value || 2);
                price += bathrooms * 25;
            }}

            // Service add-ons
            const services = getSelectedServices();
            if (services.includes('windows')) price += 30;
            if (services.includes('laundry')) price += 40;
            if (services.includes('organizing')) price += 50;

            // Frequency discounts
            const frequency = getSelectedFrequency();
            if (frequency === 'weekly') price *= 0.7;
            else if (frequency === 'biweekly') price *= 0.8;
            else if (frequency === 'monthly') price *= 0.9;
            else if (frequency === 'onetime') price *= 1.3;

            // Minimum charge
            price = Math.max(price, 75);

            return Math.round(price);
        }}

        function updatePrice() {{
            const price = calculatePrice();
            const priceElement = document.getElementById('live-price');
            priceElement.textContent = '$' + price;
            priceElement.classList.add('price-pop');
            setTimeout(() => priceElement.classList.remove('price-pop'), 500);
        }}

        // Initialize
        updatePrice();
    </script>
</body>
</html>
    '''

# Quote submission handler
@app.route('/quote-submit', methods=['POST'])
def quote_submit():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    property_type = request.form.get('property_type')
    sqft = request.form.get('sqft')
    services = request.form.get('services')
    frequency = request.form.get('frequency')
    price = request.form.get('price')

    # Generate quote ID
    quote_id = f"QUOTE{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Save to database (if available)
    try:
        db.add_quote(name, email, phone, property_type, sqft, frequency, price)
    except:
        pass

    # Store in session for result page
    session['quote_result'] = {
        'name': name,
        'email': email,
        'phone': phone,
        'property_type': property_type,
        'sqft': sqft,
        'services': services,
        'frequency': frequency,
        'price': price,
        'quote_id': quote_id
    }

    return redirect('/quote-result')

# Enhanced Quote Result Page
@app.route('/quote-result')
def quote_result():
    result = session.get('quote_result')
    if not result:
        return redirect('/quote')

    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Quote - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes confetti {{ 0% {{ transform: translateY(-100vh) rotate(0deg); opacity: 1; }} 100% {{ transform: translateY(100vh) rotate(720deg); opacity: 0; }} }}
        .confetti {{ animation: confetti 3s ease-in-out; }}
    </style>
</head>
<body class="bg-gradient-to-br from-green-50 to-blue-50 min-h-screen flex items-center">
    <div class="max-w-2xl mx-auto px-4 w-full">
        <div class="bg-white rounded-3xl shadow-2xl p-8 text-center">
            <div class="text-6xl mb-4">🎉</div>
            <h2 class="text-3xl font-bold mb-2">Awesome! Your Custom Quote is Ready!</h2>
            <p class="text-gray-600 mb-6">We've locked in your special price:</p>

            <div class="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl p-8 mb-6">
                <div class="text-6xl font-bold mb-2">${result['price']}</div>
                <div class="text-xl">{result['frequency'].title()} Cleaning Service</div>
                <div class="mt-4 text-sm opacity-90">
                    Quote ID: {result['quote_id']}
                </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4 mb-6 text-left">
                <div class="bg-gray-50 rounded-lg p-4">
                    <div class="text-sm text-gray-600">Property Type</div>
                    <div class="font-semibold">{result['property_type'].title()}</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4">
                    <div class="text-sm text-gray-600">Square Footage</div>
                    <div class="font-semibold">{result['sqft']} sq ft</div>
                </div>
            </div>

            <div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-4 mb-6">
                <div class="text-yellow-800 font-semibold mb-1">🎁 Limited Time Offer!</div>
                <div class="text-yellow-700">Book within 24 hours and get your first cleaning for 20% OFF!</div>
            </div>

            <div class="space-y-3">
                <a href="tel:{BUSINESS_PHONE}" class="block w-full bg-green-500 text-white py-4 rounded-lg font-bold text-lg hover:bg-green-600 transition">
                    📞 Call Now to Schedule: {BUSINESS_PHONE}
                </a>
                <a href="/" class="block w-full bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition">
                    Back to Home
                </a>
            </div>

            <p class="text-sm text-gray-600 mt-6">
                We'll also send your quote to <strong>{result['email']}</strong>
            </p>
        </div>
    </div>
</body>
</html>
    '''

# Staff Portal Landing Page
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

# Admin Login Page
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if db.verify_admin(username, password):
            session['is_admin'] = True
            return redirect('/admin-dashboard')

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

# Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect('/admin-login')

    stats = db.get_dashboard_stats()
    employees = db.get_all_employees()
    customers = db.get_all_customers()

    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - {BUSINESS_NAME}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="bg-white shadow p-4">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-bold">{BUSINESS_NAME} Dashboard</h1>
            <a href="/logout" class="bg-gray-500 text-white px-4 py-2 rounded">Logout</a>
        </div>
    </div>
    <div class="p-8">
        <div class="grid grid-cols-4 gap-4 mb-8">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-gray-600">Customers</div>
                <div class="text-3xl font-bold">{stats.get('total_customers', 0)}</div>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-gray-600">Employees</div>
                <div class="text-3xl font-bold">{stats.get('active_employees', 0)}</div>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-gray-600">Jobs Today</div>
                <div class="text-3xl font-bold">{stats.get('jobs_today', 0)}</div>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-gray-600">Pending</div>
                <div class="text-3xl font-bold">{stats.get('pending_quotes', 0)}</div>
            </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-bold mb-4">Employees</h2>
                <table class="w-full">
                    {"".join([f'<tr><td>{e["Name"]}</td><td>{e["Active"]}</td></tr>' for e in employees])}
                </table>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-bold mb-4">Recent Customers</h2>
                <table class="w-full">
                    {"".join([f'<tr><td>{c["Name"]}</td><td>{c["Business_Type"]}</td></tr>' for c in customers[:5]])}
                </table>
            </div>
        </div>
    </div>
</body>
</html>
    '''

# Employee Login Page
@app.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        employee = db.verify_employee(username, password)
        if employee:
            session['employee'] = employee
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

# Employee Dashboard
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
</body>
</html>
    '''

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)