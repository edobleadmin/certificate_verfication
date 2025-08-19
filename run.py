#!/usr/bin/env python3
"""
Certificate Verification and Generation System
Startup script for the Flask application
"""

import os
import sys
from app import app, init_app

def main():
    """Main function to run the application"""
    print("🚀 Starting Certificate Verification System...")
    
    # Ensure upload directory exists
    os.makedirs('uploads', exist_ok=True)
    
    # Initialize the application
    try:
        init_app()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Error initializing application: {e}")
        sys.exit(1)
    
    # Run the application
    print("🌐 Application running at: http://localhost:5000")
    print("👤 Admin login: http://localhost:5000/login")
    print("📝 Default credentials: admin / admin123")
    print("\nPress Ctrl+C to stop the application")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 