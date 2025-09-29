#!/usr/bin/env python
"""
Create complete folder structure for Cleaning Business Platform
Run this first to set up all directories
"""

import os

def create_folders():
    """Create all required folders for the project"""
    
    # Define folder structure
    folders = [
        # Root folders
        'modules',
        'routes', 
        'utils',
        'scripts',
        'tests',
        
        # Templates folders
        'templates',
        'templates/components',
        'templates/public',
        'templates/admin',
        'templates/employee',
        'templates/customer',
        'templates/errors',
        
        # Static folders
        'static',
        'static/css',
        'static/js',
        'static/img',
        'static/img/icons',
        'static/uploads',
    ]
    
    # Create each folder
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created: {folder}/")
    
    # Create __init__.py files for Python packages
    python_packages = ['modules', 'routes', 'utils']
    for package in python_packages:
        init_file = os.path.join(package, '__init__.py')
        with open(init_file, 'w') as f:
            f.write('# Package initialization\n')
        print(f"✅ Created: {init_file}")
    
    # Create .gitignore
    with open('.gitignore', 'w') as f:
        f.write("""# Environment
.env
venv/
env/
*.pyc
__pycache__/

# Credentials
credentials.json
firebase-adminsdk.json
*.pem
*.key

# Uploads
static/uploads/*
!static/uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
""")
    print("✅ Created: .gitignore")
    
    # Create .gitkeep for empty folders
    gitkeep_folders = ['static/uploads', 'static/img/icons']
    for folder in gitkeep_folders:
        gitkeep = os.path.join(folder, '.gitkeep')
        with open(gitkeep, 'w') as f:
            f.write('')
        print(f"✅ Created: {gitkeep}")
    
    print("\n🎉 Folder structure created successfully!")
    print("\nNext steps:")
    print("1. Run: pip install -r requirements.txt")
    print("2. Create your .env file")
    print("3. Add your credentials.json from Google Cloud")
    print("4. Run: python run.py")

if __name__ == "__main__":
    print("🏗️ Creating Cleaning Business Platform folder structure...")
    print("=" * 50)
    create_folders()