#!/usr/bin/env python3
"""
Financial Analytics Platform - Root Application Entry Point
Delegates to backend.app Flask instance
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app from backend
from backend.app import app

if __name__ == '__main__':
    # Run Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
 