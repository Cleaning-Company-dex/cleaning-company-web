#!/usr/bin/env python
"""
Cleaning Business Platform - Main Runner
"""

import os
import sys
from app import create_app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("=" * 50)
    print("🧹 Cleaning Business Platform")
    print(f"📍 Running on: http://localhost:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📊 Admin Panel: http://localhost:{port}/admin")
    print(f"👷 Employee Portal: http://localhost:{port}/employee")
    print(f"👤 Customer Portal: http://localhost:{port}/customer")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )