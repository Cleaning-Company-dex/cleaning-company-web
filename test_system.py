#!/usr/bin/env python
"""
Test Script - Verify Everything is Working
"""

import os
import sys

def test_system():
    print("🧪 Testing Cleaning Business Platform Setup")
    print("=" * 50)
    
    # Test 1: Check Python version
    print("1. Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor} - OK")
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Please use Python 3.7+")
        return False
    
    # Test 2: Check required files
    print("\n2. Checking required files...")
    required_files = [
        'app.py',
        'config.py',
        'run.py',
        'requirements.txt',
        '.env'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} - Found")
        else:
            print(f"   ❌ {file} - Missing")
    
    # Test 3: Check credentials
    print("\n3. Checking credentials...")
    if os.path.exists('credentials.json'):
        print("   ✅ credentials.json - Found")
    else:
        print("   ⚠️  credentials.json - Missing (Download from Google Cloud Console)")
    
    # Test 4: Try imports
    print("\n4. Testing imports...")
    try:
        import flask
        print("   ✅ Flask - Installed")
    except ImportError:
        print("   ❌ Flask - Not installed (run: pip install -r requirements.txt)")
    
    try:
        import gspread
        print("   ✅ Google Sheets - Installed")
    except ImportError:
        print("   ❌ Google Sheets - Not installed")
    
    # Test 5: Check folders
    print("\n5. Checking folder structure...")
    folders = ['templates', 'static', 'modules', 'routes', 'utils', 'scripts']
    for folder in folders:
        if os.path.isdir(folder):
            print(f"   ✅ {folder}/ - Found")
        else:
            print(f"   ❌ {folder}/ - Missing (run: python create_structure.py)")
    
    print("\n" + "=" * 50)
    print("✅ Setup verification complete!")
    print("\nNext steps:")
    print("1. Make sure credentials.json is in place")
    print("2. Update .env with your settings")
    print("3. Run: python scripts/init_database.py")
    print("4. Run: python scripts/load_test_data.py")
    print("5. Start the app: python run.py")
    print("\nDefault logins:")
    print("  Admin: admin / changeme123")
    print("  Employee: john / password123")
    print("  Customer: contact@abc.com")

if __name__ == "__main__":
    test_system()