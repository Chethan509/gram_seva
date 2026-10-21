"""
Database module for Grama Seva Portal.
Handles SQLite connection, schema initialization, and transactional queries.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grama_seva.db')


def get_db_connection():
    """Returns a SQLite connection with Row factory enabled for dictionary-style access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates the SQLite database schema if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        mobile TEXT NOT NULL,
        email TEXT,
        village TEXT NOT NULL,
        ward_no TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'citizen', -- 'citizen', 'admin'
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Departments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name_en TEXT NOT NULL,
        name_kn TEXT NOT NULL,
        officer_name TEXT NOT NULL,
        officer_contact TEXT NOT NULL,
        email TEXT
    );
    """)

    # 3. Complaint Categories Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name_en TEXT NOT NULL,
        name_kn TEXT NOT NULL,
        icon TEXT NOT NULL,
        color TEXT NOT NULL,
        description_en TEXT NOT NULL,
        description_kn TEXT NOT NULL,
        examples_en TEXT NOT NULL,
        examples_kn TEXT NOT NULL,
        default_dept_id INTEGER,
        FOREIGN KEY (default_dept_id) REFERENCES departments(id)
    );
    """)

    # 4. Complaints Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        problem_type TEXT NOT NULL,
        village TEXT NOT NULL,
        ward_no TEXT NOT NULL,
        landmark TEXT NOT NULL,
        description TEXT NOT NULL,
        photo_url TEXT,
        contact_number TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium', -- 'Low', 'Medium', 'High', 'Urgent'
        status TEXT DEFAULT 'Submitted', -- 'Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Rejected'
        department_id INTEGER,
        officer_remarks TEXT,
        resolution_details TEXT,
        school_name TEXT,
        school_location TEXT,
        school_infra_type TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    );
    """)

    # 5. Complaint Status History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        remarks TEXT,
        action_by TEXT NOT NULL DEFAULT 'System',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
    );
    """)

    # 6. Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        complaint_id INTEGER,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info', -- 'info', 'success', 'warning', 'error'
        is_read INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE SET NULL
    );
    """)

    # 7. Citizen Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizen_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        complaint_id INTEGER,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        comments TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE SET NULL
    );
    """)

    # 8. Panchayat Global Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS panchayat_settings (
        id INTEGER PRIMARY KEY,
        panchayat_name TEXT NOT NULL,
        panchayat_name_kn TEXT NOT NULL,
        district TEXT NOT NULL,
        taluk TEXT NOT NULL,
        state TEXT NOT NULL DEFAULT 'Karnataka',
        helpline TEXT NOT NULL,
        office_address TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        villages_list TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed default settings if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO panchayat_settings (
            id, panchayat_name, panchayat_name_kn, district, taluk, state,
            helpline, office_address, contact_email, villages_list
        ) VALUES (
            1, 'Shivapura Gram Panchayat', 'ಶಿವಪುರ ಗ್ರಾಮ ಪಂಚಾಯತಿ', 'Mandya District', 'Mandya Taluk', 'Karnataka',
            '1800-425-3456', 'Gram Panchayat Karyalaya, Main Road, Beside Postal Sub-Office, Shivapura',
            'helpdesk@gramseva.kar.gov.in',
            'Shivapura Main Village, Shivapura Gollarahatti, Shivapura Kerekoppalu, Shivapura Harijanawada'
        )
    """)

    conn.commit()
    conn.close()
    print("Database schema initialized successfully.")


def get_panchayat_settings():
    """Fetches global Gram Panchayat configuration settings."""
    conn = get_db_connection()
    settings = conn.execute("SELECT * FROM panchayat_settings WHERE id = 1").fetchone()
    if not settings:
        conn.execute("""
            INSERT OR IGNORE INTO panchayat_settings (
                id, panchayat_name, panchayat_name_kn, district, taluk, state,
                helpline, office_address, contact_email, villages_list
            ) VALUES (
                1, 'Shivapura Gram Panchayat', 'ಶಿವಪುರ ಗ್ರಾಮ ಪಂಚಾಯತಿ', 'Mandya District', 'Mandya Taluk', 'Karnataka',
                '1800-425-3456', 'Gram Panchayat Karyalaya, Main Road, Beside Postal Sub-Office, Shivapura',
                'helpdesk@gramseva.kar.gov.in',
                'Shivapura Main Village, Shivapura Gollarahatti, Shivapura Kerekoppalu, Shivapura Harijanawada'
            )
        """)
        conn.commit()
        settings = conn.execute("SELECT * FROM panchayat_settings WHERE id = 1").fetchone()
    conn.close()
    return settings


def generate_complaint_id(cursor):
    """Generates unique sequential complaint ID formatted like GS-2026-00101."""
    year = datetime.now().year
    cursor.execute("SELECT COUNT(*) as count FROM complaints")
    count = cursor.fetchone()['count'] + 101
    return f"GS-{year}-{count:05d}"


def add_notification(user_id, title, message, complaint_id=None, n_type='info'):
    """Helper to create a notification for a user."""
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO notifications (user_id, complaint_id, title, message, type)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, complaint_id, title, message, n_type))
    conn.commit()
    conn.close()


def add_complaint_history(complaint_db_id, status, remarks, action_by='Administrator'):
    """Helper to record status transition in complaint history."""
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO complaint_history (complaint_id, status, remarks, action_by)
        VALUES (?, ?, ?, ?)
    """, (complaint_db_id, status, remarks, action_by))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
