#!/usr/bin/env python3
"""
WSGI entry point for AWS deployment
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from app import app, init_app

# Initialize the application
init_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Get host from environment variable or default to 0.0.0.0
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Run the application
    app.run(host=host, port=port, debug=False) 