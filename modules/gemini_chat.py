import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiChat:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.initialized = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.initialized = True
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
    
    def get_response(self, user_message):
        """Get response from Gemini or fallback responses"""
        
        # If Gemini is not initialized, provide helpful fallback responses
        if not self.initialized or not self.model:
            return self.get_fallback_response(user_message)
        
        try:
            # Create a focused prompt for cleaning services
            prompt = f"""You are a helpful assistant for Baez Cleaning Services. 
            Answer this question about cleaning services: {user_message}
            
            Keep your response brief, friendly, and focused on cleaning services.
            If asked about pricing: Residential $0.15/sqft, Commercial $0.08/sqft, Medical $0.12/sqft
            If asked about scheduling: Call (555) 123-4567
            If asked about areas: We serve Greater Boston area
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, message):
        """Provide helpful responses without AI"""
        msg = message.lower()
        
        # Service-related responses
        if any(word in msg for word in ['service', 'offer', 'clean', 'what do']):
            return "We offer professional cleaning for homes, offices, medical facilities, and restaurants. Each service includes thorough cleaning, sanitization, and attention to detail. Would you like a free quote?"
        
        # Pricing responses
        elif any(word in msg for word in ['price', 'cost', 'much', 'rate', 'quote']):
            return "Our pricing starts at: Residential $0.15/sqft, Commercial $0.08/sqft, Medical $0.12/sqft. Get an instant quote using our calculator above, or call (555) 123-4567 for a custom estimate!"
        
        # Area/location responses
        elif any(word in msg for word in ['area', 'location', 'where', 'serve', 'boston']):
            return "We proudly serve Greater Boston including: Boston, Cambridge, Quincy, Newton, Brookline, Somerville, and surrounding areas within 15 miles. Call us to confirm service to your location!"
        
        # Scheduling responses
        elif any(word in msg for word in ['schedule', 'book', 'appointment', 'when', 'available']):
            return "We're available Mon-Sat 8AM-6PM. You can schedule service by calling (555) 123-4567 or getting a quote online. Same-day service may be available!"
        
        # Frequency responses
        elif any(word in msg for word in ['often', 'frequency', 'weekly', 'monthly']):
            return "We offer flexible scheduling: Weekly (save 30%), Bi-weekly (save 20%), Monthly (save 10%), or One-time deep cleaning. Regular service gives you the best value!"
        
        # Contact responses
        elif any(word in msg for word in ['contact', 'call', 'phone', 'email']):
            return "Contact us at: Phone: (555) 123-4567 (Mon-Sat 8AM-6PM), Email: info@baezcleaningservices.com. We respond quickly to all inquiries!"
        
        # Quality/guarantee responses
        elif any(word in msg for word in ['guarantee', 'satisfaction', 'quality', 'insured']):
            return "We're fully licensed and insured with 100% satisfaction guarantee! If you're not happy with any area we've cleaned, we'll re-clean it for free. Your satisfaction is our priority!"
        
        # Time/duration responses
        elif any(word in msg for word in ['long', 'time', 'duration', 'hours']):
            return "Typical cleaning times: 1-bedroom (1-2 hours), 2-bedroom (2-3 hours), Office (varies by size). We work efficiently while maintaining high quality standards!"
        
        # Supplies/products responses
        elif any(word in msg for word in ['supply', 'product', 'chemical', 'eco', 'green']):
            return "We use eco-friendly, non-toxic cleaning products that are safe for children and pets. We bring all supplies needed. If you have specific product preferences, just let us know!"
        
        # Default response
        else:
            return "I can help you with questions about our cleaning services, pricing, scheduling, or service areas. You can also call us at (555) 123-4567 or use the quote calculator above for instant pricing!"
