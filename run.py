"""
Convenience entry runner for Grama Seva Portal.
Automatically initializes database and seeds realistic demo data if needed,
then starts the development server.
"""

import sys
import os

# Ensure UTF-8 output encoding for Windows command line compatibility
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import init_db, DB_PATH
from seed_data import seed_all
from app import app

if __name__ == '__main__':
    # Initialize DB and seed demo data if fresh run
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        print("[*] Initializing database and seeding demo data...")
        seed_all()
    else:
        init_db()

    print("\n" + "="*70)
    print("  GRAMA SEVA - Smart Gram Panchayat Complaint Management Portal")
    print("  Official Civic Redressal System - Government Theme")
    print("="*70)
    print("  Website URL:       http://127.0.0.1:5000")
    print("  Citizen Demo:      username: citizen   | password: citizen123")
    print("  Officer Demo:      username: admin     | password: admin123")
    print("="*70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
