"""
Grama Seva – Smart Gram Panchayat Complaint Management Portal
Flask Backend Application
"""

import os
import sys
import io
import csv

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, send_file, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import (
    get_db_connection, init_db, generate_complaint_id,
    add_notification, add_complaint_history, get_panchayat_settings
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'grama-seva-karnataka-smart-panchayat-secret-key-2026')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB maximum upload size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------------------
# Context Processors & Decorators
# -------------------------------------------------------------

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        g.unread_notifications_count = 0
    else:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        g.user = user

        if user:
            # Count unread notifications
            unread = conn.execute(
                "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0",
                (user_id,)
            ).fetchone()
            g.unread_notifications_count = unread['count'] if unread else 0
        else:
            g.unread_notifications_count = 0
        conn.close()

    # Language setting (default 'en', support 'kn')
    if 'lang' not in session:
        session['lang'] = 'en'
    g.lang = session['lang']


@app.context_processor
def inject_global_data():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    departments = conn.execute("SELECT * FROM departments ORDER BY id ASC").fetchall()
    conn.close()
    gp_settings = get_panchayat_settings()
    villages = [v.strip() for v in gp_settings['villages_list'].split(',') if v.strip()]
    return {
        'now': datetime.now(),
        'all_categories': categories,
        'all_departments': departments,
        'current_lang': session.get('lang', 'en'),
        'gp': gp_settings,
        'villages': villages
    }


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Please log in as an administrator to access this area.", "warning")
            return redirect(url_for('admin_login', next=request.url))
        if g.user['role'] != 'admin':
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------------------------------------
# Language Switcher Route
# -------------------------------------------------------------
@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'kn']:
        session['lang'] = lang
    next_url = request.referrer or url_for('dashboard')
    return redirect(next_url)


# -------------------------------------------------------------
# Authentication Routes (Page 1 & Page 8)
# -------------------------------------------------------------

@app.route('/')
def home():
    if g.user:
        if g.user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash("Please enter both mobile number/username and password.", "danger")
            return render_template('login.html', identifier=identifier)

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE (username = ? OR mobile = ?)",
            (identifier, identifier)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['user_name'] = user['full_name']

            flash(f"Welcome back, {user['full_name']}!", "success")
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid mobile number/username or password. Please try again.", "danger")

    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if g.user and g.user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Please enter your administrator credentials.", "danger")
            return render_template('admin_login.html')

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE (username = ? OR mobile = ?) AND role = 'admin'",
            (username, username)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['user_name'] = user['full_name']

            flash(f"Administrator access granted. Welcome, {user['full_name']}.", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid administrator credentials or unauthorized account.", "danger")

    return render_template('admin_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        village = request.form.get('village', '').strip()
        ward_no = request.form.get('ward_no', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            errors.append("Valid 10-digit mobile number is required.")
        if not village:
            errors.append("Village name is required.")
        if not ward_no:
            errors.append("Ward number is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('login.html', is_register=True, form_data=request.form)

        conn = get_db_connection()
        existing_user = conn.execute(
            "SELECT id FROM users WHERE username = ? OR mobile = ?",
            (mobile, mobile)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("An account with this mobile number already exists. Please login.", "warning")
            return render_template('login.html', is_register=False, identifier=mobile)

        pwd_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (full_name, username, mobile, email, village, ward_no, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'citizen')
        """, (full_name, mobile, mobile, email, village, ward_no, pwd_hash))
        new_user_id = cursor.lastrowid
        conn.commit()

        # Send welcome notification
        add_notification(
            new_user_id,
            "Welcome to Grama Seva!",
            "Your citizen account has been successfully created. You can now submit and track village civic complaints online.",
            None,
            "success"
        )
        conn.close()

        # Auto-login
        session.clear()
        session['user_id'] = new_user_id
        session['role'] = 'citizen'
        session['user_name'] = full_name

        flash(f"Welcome {full_name}! Your account has been registered successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('login.html', is_register=True)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        if not mobile or len(mobile) != 10:
            flash("Please enter a valid 10-digit registered mobile number.", "danger")
            return render_template('login.html', is_forgot=True)

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE mobile = ?", (mobile,)).fetchone()
        conn.close()

        if user:
            flash("Password reset link / OTP has been sent to your registered mobile number (Demo prototype simulation: Temporary password is 'citizen123').", "info")
            return redirect(url_for('login'))
        else:
            flash("No account registered with this mobile number in Shivapura Gram Panchayat.", "warning")

    return render_template('login.html', is_forgot=True)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))


# -------------------------------------------------------------
# Citizen Portal Routes (Pages 2 - 7, 12)
# -------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    user_id = g.user['id']

    # Citizen complaint counts
    stats = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('Submitted', 'Under Review') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status IN ('Assigned', 'Work in Progress') THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved
        FROM complaints
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    # Recent complaints by citizen
    recent_complaints = conn.execute("""
        SELECT c.*, cat.name_en as cat_name_en, cat.name_kn as cat_name_kn,
               cat.icon as cat_icon, cat.color as cat_color
        FROM complaints c
        JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
        LIMIT 5
    """, (user_id,)).fetchall()

    # Categories for quick submission cards
    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    conn.close()

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_complaints=recent_complaints,
        categories=categories
    )


@app.route('/categories')
@login_required
def categories():
    conn = get_db_connection()
    all_cats = conn.execute("""
        SELECT c.*, d.name_en as dept_name,
               (SELECT COUNT(*) FROM complaints WHERE category_id = c.id) as complaint_count
        FROM categories c
        LEFT JOIN departments d ON c.default_dept_id = d.id
        ORDER BY c.id ASC
    """).fetchall()
    conn.close()
    return render_template('categories.html', categories=all_cats)


@app.route('/submit-complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    preselected_cat = request.args.get('category')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        problem_type = request.form.get('problem_type', '').strip()
        village = request.form.get('village', '').strip()
        ward_no = request.form.get('ward_no', '').strip()
        landmark = request.form.get('landmark', '').strip()
        description = request.form.get('description', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        priority = request.form.get('priority', 'Medium')

        # Conditional School Fields
        school_name = request.form.get('school_name', '').strip()
        school_location = request.form.get('school_location', '').strip()
        school_infra_type = request.form.get('school_infra_type', '').strip()

        # Validation
        errors = []
        if not title:
            errors.append("Complaint title is required.")
        if not category_id:
            errors.append("Please select a complaint category.")
        if not problem_type:
            errors.append("Specific problem type is required.")
        if not village:
            errors.append("Village name is required.")
        if not ward_no:
            errors.append("Ward number is required.")
        if not landmark:
            errors.append("Exact location or landmark is required.")
        if not description or len(description) < 15:
            errors.append("Please provide a detailed problem description (at least 15 characters).")
        if not contact_number:
            errors.append("Contact number is required.")

        # Photo upload handling
        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add unique timestamp prefix to prevent name collisions
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    photo_url = f"/static/images/uploads/{unique_filename}"
                else:
                    errors.append("Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP.")

        if errors:
            for err in errors:
                flash(err, "danger")
            conn = get_db_connection()
            categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
            conn.close()
            return render_template(
                'submit_complaint.html',
                categories=categories,
                form_data=request.form,
                preselected_cat=category_id
            )

        # Database insertion
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch category default department
        cat_info = cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
        dept_id = cat_info['default_dept_id'] if cat_info else 1

        complaint_id = generate_complaint_id(cursor)

        cursor.execute("""
            INSERT INTO complaints (
                complaint_id, user_id, category_id, title, problem_type,
                village, ward_no, landmark, description, photo_url,
                contact_number, priority, status, department_id,
                school_name, school_location, school_infra_type,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            complaint_id, g.user['id'], category_id, title, problem_type,
            village, ward_no, landmark, description, photo_url,
            contact_number, priority, dept_id,
            school_name if school_name else None,
            school_location if school_location else None,
            school_infra_type if school_infra_type else None
        ))
        db_complaint_id = cursor.lastrowid

        # Insert history entry
        cursor.execute("""
            INSERT INTO complaint_history (complaint_id, status, remarks, action_by)
            VALUES (?, 'Submitted', 'Complaint submitted successfully by citizen.', ?)
        """, (db_complaint_id, g.user['full_name']))

        # Insert notification for user
        cursor.execute("""
            INSERT INTO notifications (user_id, complaint_id, title, message, type)
            VALUES (?, ?, ?, ?, 'success')
        """, (
            g.user['id'],
            db_complaint_id,
            f"Complaint Registered: {complaint_id}",
            f"Your complaint '{title}' has been successfully registered. You can track its progress with ID {complaint_id}."
        ))

        conn.commit()
        conn.close()

        flash(f"Complaint registered successfully! Your tracking ID is {complaint_id}", "success")
        return render_template(
            'submit_complaint.html',
            success=True,
            complaint_id=complaint_id,
            complaint_title=title
        )

    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    conn.close()
    return render_template(
        'submit_complaint.html',
        categories=categories,
        preselected_cat=preselected_cat,
        form_data={'village': g.user['village'], 'ward_no': g.user['ward_no'], 'contact_number': g.user['mobile']}
    )


@app.route('/track')
@app.route('/track/<complaint_id>')
def track(complaint_id=None):
    search_id = complaint_id or request.args.get('complaint_id', '').strip()
    complaint = None
    history = []
    category = None
    department = None

    if search_id:
        conn = get_db_connection()
        complaint = conn.execute("""
            SELECT c.*, u.full_name as citizen_name, u.mobile as citizen_mobile,
                   cat.name_en as cat_name_en, cat.name_kn as cat_name_kn,
                   cat.icon as cat_icon, cat.color as cat_color,
                   d.name_en as dept_name_en, d.name_kn as dept_name_kn,
                   d.officer_name, d.officer_contact
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN categories cat ON c.category_id = cat.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.complaint_id = ?
        """, (search_id,)).fetchone()

        if complaint:
            history = conn.execute("""
                SELECT * FROM complaint_history
                WHERE complaint_id = ?
                ORDER BY created_at ASC
            """, (complaint['id'],)).fetchall()
        else:
            flash(f"No complaint found matching ID '{search_id}'. Please check the ID and try again.", "warning")
        conn.close()

    return render_template('track.html', search_id=search_id, complaint=complaint, history=history)


@app.route('/my-complaints')
@login_required
def my_complaints():
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '').strip()

    conn = get_db_connection()
    query = """
        SELECT c.*, cat.name_en as cat_name_en, cat.name_kn as cat_name_kn,
               cat.icon as cat_icon, cat.color as cat_color,
               d.name_en as dept_name
        FROM complaints c
        JOIN categories cat ON c.category_id = cat.id
        LEFT JOIN departments d ON c.department_id = d.id
        WHERE c.user_id = ?
    """
    params = [g.user['id']]

    if status_filter == 'pending':
        query += " AND c.status IN ('Submitted', 'Under Review')"
    elif status_filter == 'in_progress':
        query += " AND c.status IN ('Assigned', 'Work in Progress')"
    elif status_filter == 'resolved':
        query += " AND c.status = 'Resolved'"
    elif status_filter == 'rejected':
        query += " AND c.status = 'Rejected'"

    if search_query:
        query += " AND (c.complaint_id LIKE ? OR c.title LIKE ? OR c.landmark LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    query += " ORDER BY c.created_at DESC"
    complaints = conn.execute(query, params).fetchall()

    # Counts for filter pills
    counts = conn.execute("""
        SELECT
            COUNT(*) as all_count,
            SUM(CASE WHEN status IN ('Submitted', 'Under Review') THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN status IN ('Assigned', 'Work in Progress') THEN 1 ELSE 0 END) as in_progress_count,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count,
            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected_count
        FROM complaints
        WHERE user_id = ?
    """, (g.user['id'],)).fetchone()

    conn.close()

    return render_template(
        'my_complaints.html',
        complaints=complaints,
        status_filter=status_filter,
        search_query=search_query,
        counts=counts
    )


@app.route('/notifications')
@login_required
def notifications():
    conn = get_db_connection()
    # Fetch notifications for current user
    notifs = conn.execute("""
        SELECT n.*, c.complaint_id as ref_complaint_id
        FROM notifications n
        LEFT JOIN complaints c ON n.complaint_id = c.id
        WHERE n.user_id = ?
        ORDER BY n.created_at DESC
    """, (g.user['id'],)).fetchall()

    # Mark all as read when opening notifications page
    conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (g.user['id'],))
    conn.commit()
    conn.close()

    return render_template('notifications.html', notifications=notifs)


@app.route('/notifications/clear', methods=['POST'])
@login_required
def clear_notifications():
    conn = get_db_connection()
    conn.execute("DELETE FROM notifications WHERE user_id = ?", (g.user['id'],))
    conn.commit()
    conn.close()
    flash("Notifications cleared.", "info")
    return redirect(url_for('notifications'))


@app.route('/help')
def help_support():
    return render_template('help.html')


@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    rating = request.form.get('rating', type=int)
    comments = request.form.get('comments', '').strip()
    complaint_id_str = request.form.get('complaint_id', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash("Please provide a valid rating from 1 to 5 stars.", "danger")
        return redirect(url_for('help_support'))

    conn = get_db_connection()
    complaint_ref = None
    if complaint_id_str:
        c = conn.execute("SELECT id FROM complaints WHERE complaint_id = ?", (complaint_id_str,)).fetchone()
        if c:
            complaint_ref = c['id']

    conn.execute("""
        INSERT INTO citizen_feedback (user_id, complaint_id, rating, comments)
        VALUES (?, ?, ?, ?)
    """, (g.user['id'], complaint_ref, rating, comments))
    conn.commit()
    conn.close()

    flash("Thank you for your valuable feedback! It helps improve Gram Panchayat public services.", "success")
    return redirect(url_for('help_support'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        village = request.form.get('village', '').strip()
        ward_no = request.form.get('ward_no', '').strip()

        if not full_name or not village or not ward_no:
            flash("Full name, village and ward number are required.", "danger")
            return redirect(url_for('profile'))

        conn = get_db_connection()
        conn.execute("""
            UPDATE users
            SET full_name = ?, email = ?, village = ?, ward_no = ?
            WHERE id = ?
        """, (full_name, email, village, ward_no, g.user['id']))
        conn.commit()
        conn.close()

        flash("Profile updated successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html')


# -------------------------------------------------------------
# Admin Portal Routes (Pages 9 - 11, Departments, Users)
# -------------------------------------------------------------

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()

    # 1. Metric Counts
    metrics = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as new_complaints,
            SUM(CASE WHEN status IN ('Submitted', 'Under Review') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status IN ('Assigned', 'Work in Progress') THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN status NOT IN ('Resolved', 'Rejected') AND created_at <= datetime('now', '-7 days') THEN 1 ELSE 0 END) as overdue
        FROM complaints
    """).fetchone()

    # 2. Complaints by Category (for Chart.js doughnut)
    cat_stats = conn.execute("""
        SELECT cat.name_en, cat.color, COUNT(c.id) as count
        FROM categories cat
        LEFT JOIN complaints c ON cat.id = c.category_id
        GROUP BY cat.id
        ORDER BY count DESC
    """).fetchall()

    # 3. Monthly complaint trends (last 6 months)
    monthly_stats = conn.execute("""
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved
        FROM complaints
        GROUP BY month
        ORDER BY month ASC
        LIMIT 6
    """).fetchall()

    # 4. Ward-wise complaint distribution
    ward_stats = conn.execute("""
        SELECT ward_no, COUNT(*) as count
        FROM complaints
        GROUP BY ward_no
        ORDER BY ward_no ASC
    """).fetchall()

    # 5. Status distribution
    status_stats = conn.execute("""
        SELECT status, COUNT(*) as count
        FROM complaints
        GROUP BY status
    """).fetchall()

    # 6. Recent 5 complaints requiring attention
    recent_complaints = conn.execute("""
        SELECT c.*, cat.name_en as cat_name_en, cat.icon as cat_icon,
               u.full_name as citizen_name
        FROM complaints c
        JOIN categories cat ON c.category_id = cat.id
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        'admin/dashboard.html',
        metrics=metrics,
        cat_stats=[dict(c) for c in cat_stats],
        monthly_stats=[dict(m) for m in monthly_stats],
        ward_stats=[dict(w) for w in ward_stats],
        status_stats=[dict(s) for s in status_stats],
        recent_complaints=recent_complaints
    )


@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    status = request.args.get('status', 'all')
    category_id = request.args.get('category')
    priority = request.args.get('priority')
    ward_no = request.args.get('ward')
    search = request.args.get('search', '').strip()

    conn = get_db_connection()
    query = """
        SELECT c.*, u.full_name as citizen_name, u.mobile as citizen_mobile,
               cat.name_en as cat_name_en, cat.name_kn as cat_name_kn,
               cat.icon as cat_icon, cat.color as cat_color,
               d.name_en as dept_name, d.officer_name
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        JOIN categories cat ON c.category_id = cat.id
        LEFT JOIN departments d ON c.department_id = d.id
        WHERE 1=1
    """
    params = []

    if status and status != 'all':
        query += " AND c.status = ?"
        params.append(status)

    if category_id:
        query += " AND c.category_id = ?"
        params.append(category_id)

    if priority:
        query += " AND c.priority = ?"
        params.append(priority)

    if ward_no:
        query += " AND c.ward_no = ?"
        params.append(ward_no)

    if search:
        query += " AND (c.complaint_id LIKE ? OR c.title LIKE ? OR u.full_name LIKE ? OR c.landmark LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY c.created_at DESC"
    complaints = conn.execute(query, params).fetchall()

    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    departments = conn.execute("SELECT * FROM departments ORDER BY id ASC").fetchall()
    wards = conn.execute("SELECT DISTINCT ward_no FROM complaints ORDER BY ward_no ASC").fetchall()

    conn.close()

    return render_template(
        'admin/complaints.html',
        complaints=complaints,
        categories=categories,
        departments=departments,
        wards=wards,
        current_status=status,
        current_category=category_id,
        current_priority=priority,
        current_ward=ward_no,
        search_query=search
    )


@app.route('/admin/complaint/<int:id>/update', methods=['POST'])
@admin_required
def admin_update_complaint(id):
    status = request.form.get('status')
    department_id = request.form.get('department_id')
    priority = request.form.get('priority')
    officer_remarks = request.form.get('officer_remarks', '').strip()
    resolution_details = request.form.get('resolution_details', '').strip()

    conn = get_db_connection()
    c = conn.execute("SELECT * FROM complaints WHERE id = ?", (id,)).fetchone()

    if not c:
        conn.close()
        flash("Complaint not found.", "danger")
        return redirect(url_for('admin_complaints'))

    resolved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status == 'Resolved' else c['resolved_at']

    conn.execute("""
        UPDATE complaints
        SET status = ?, department_id = ?, priority = ?,
            officer_remarks = ?, resolution_details = ?,
            resolved_at = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, department_id, priority, officer_remarks, resolution_details, resolved_at, id))

    # Add to status history if status changed or remarks added
    history_msg = officer_remarks or f"Status updated to '{status}' by {g.user['full_name']}."
    conn.execute("""
        INSERT INTO complaint_history (complaint_id, status, remarks, action_by)
        VALUES (?, ?, ?, ?)
    """, (id, status, history_msg, g.user['full_name']))

    # Generate Notification for Citizen
    notif_msg = f"Your complaint {c['complaint_id']} status has been updated to '{status}'."
    if officer_remarks:
        notif_msg += f" Remarks: {officer_remarks}"
    notif_type = 'success' if status == 'Resolved' else ('warning' if status == 'Rejected' else 'info')

    conn.execute("""
        INSERT INTO notifications (user_id, complaint_id, title, message, type)
        VALUES (?, ?, ?, ?, ?)
    """, (c['user_id'], id, f"Complaint Update: {c['complaint_id']}", notif_msg, notif_type))

    conn.commit()
    conn.close()

    flash(f"Complaint {c['complaint_id']} updated successfully. Citizen has been notified.", "success")
    return redirect(request.referrer or url_for('admin_complaints'))


@app.route('/admin/reports')
@admin_required
def admin_reports():
    conn = get_db_connection()

    # 1. Overall Key Performance Indicators (KPIs)
    kpis = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count,
            SUM(CASE WHEN status IN ('Submitted', 'Under Review') THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected_count,
            ROUND(AVG(CASE WHEN status = 'Resolved' THEN
                (julianday(resolved_at) - julianday(created_at)) * 24 ELSE NULL END), 1) as avg_resolution_hours
        FROM complaints
    """).fetchone()

    # Calculate percentage
    resolved_pct = 0
    if kpis['total'] and kpis['total'] > 0:
        resolved_pct = round((kpis['resolved_count'] / kpis['total']) * 100, 1)

    # 2. Category Performance Breakdown
    cat_breakdown = conn.execute("""
        SELECT cat.name_en, cat.icon, cat.color,
               COUNT(c.id) as total_count,
               SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count,
               SUM(CASE WHEN c.status IN ('Submitted', 'Under Review', 'Assigned', 'Work in Progress') THEN 1 ELSE 0 END) as pending_count
        FROM categories cat
        LEFT JOIN complaints c ON cat.id = c.category_id
        GROUP BY cat.id
        ORDER BY total_count DESC
    """).fetchall()

    # 3. Department Workload
    dept_breakdown = conn.execute("""
        SELECT d.name_en, d.officer_name, d.officer_contact,
               COUNT(c.id) as total_assigned,
               SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
               SUM(CASE WHEN c.status NOT IN ('Resolved', 'Rejected') THEN 1 ELSE 0 END) as active
        FROM departments d
        LEFT JOIN complaints c ON d.id = c.department_id
        GROUP BY d.id
        ORDER BY active DESC
    """).fetchall()

    # 4. Ward-wise distribution
    ward_breakdown = conn.execute("""
        SELECT ward_no,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
               SUM(CASE WHEN status != 'Resolved' THEN 1 ELSE 0 END) as pending
        FROM complaints
        GROUP BY ward_no
        ORDER BY ward_no ASC
    """).fetchall()

    conn.close()

    return render_template(
        'admin/reports.html',
        kpis=kpis,
        resolved_pct=resolved_pct,
        cat_breakdown=cat_breakdown,
        dept_breakdown=dept_breakdown,
        ward_breakdown=ward_breakdown
    )


@app.route('/admin/export-csv')
@admin_required
def admin_export_csv():
    conn = get_db_connection()
    complaints = conn.execute("""
        SELECT c.complaint_id, c.title, cat.name_en as category,
               c.problem_type, c.village, c.ward_no, c.landmark,
               u.full_name as citizen_name, c.contact_number,
               c.priority, c.status, d.name_en as department,
               c.officer_remarks, c.school_name,
               c.created_at, c.resolved_at
        FROM complaints c
        JOIN categories cat ON c.category_id = cat.id
        JOIN users u ON c.user_id = u.id
        LEFT JOIN departments d ON c.department_id = d.id
        ORDER BY c.created_at DESC
    """).fetchall()
    conn.close()

    si = io.StringIO()
    cw = csv.writer(si)

    # Header Row
    cw.writerow([
        'Complaint ID', 'Title', 'Category', 'Problem Type',
        'Village', 'Ward No', 'Landmark', 'Citizen Name',
        'Contact Number', 'Priority', 'Current Status',
        'Assigned Department', 'Officer Remarks', 'School Name (If applicable)',
        'Submission Date', 'Resolved Date'
    ])

    # Data Rows
    for row in complaints:
        cw.writerow([
            row['complaint_id'],
            row['title'],
            row['category'],
            row['problem_type'],
            row['village'],
            row['ward_no'],
            row['landmark'],
            row['citizen_name'],
            row['contact_number'],
            row['priority'],
            row['status'],
            row['department'] or 'Unassigned',
            row['officer_remarks'] or '',
            row['school_name'] or '',
            row['created_at'],
            row['resolved_at'] or ''
        ])

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8-sig')) # UTF-8 with BOM for Excel compatibility
    output.seek(0)

    filename = f"Grama_Seva_Complaints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/admin/departments')
@admin_required
def admin_departments():
    conn = get_db_connection()
    depts = conn.execute("""
        SELECT d.*,
               COUNT(c.id) as total_complaints,
               SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count,
               SUM(CASE WHEN c.status IN ('Assigned', 'Work in Progress') THEN 1 ELSE 0 END) as active_count
        FROM departments d
        LEFT JOIN complaints c ON d.id = c.department_id
        GROUP BY d.id
        ORDER BY d.id ASC
    """).fetchall()
    conn.close()
    return render_template('admin/departments.html', departments=depts)


@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    all_users = conn.execute("""
        SELECT u.*,
               COUNT(c.id) as complaint_count
        FROM users u
        LEFT JOIN complaints c ON u.id = c.user_id
        GROUP BY u.id
        ORDER BY u.role ASC, u.created_at DESC
    """).fetchall()
    conn.close()
    return render_template('admin/users.html', users=all_users)


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    conn = get_db_connection()
    if request.method == 'POST':
        panchayat_name = request.form.get('panchayat_name', '').strip()
        panchayat_name_kn = request.form.get('panchayat_name_kn', '').strip()
        district = request.form.get('district', '').strip()
        taluk = request.form.get('taluk', '').strip()
        helpline = request.form.get('helpline', '').strip()
        office_address = request.form.get('office_address', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        villages_list = request.form.get('villages_list', '').strip()

        if not panchayat_name or not villages_list:
            flash("Gram Panchayat name and village list cannot be empty.", "danger")
        else:
            conn.execute("""
                UPDATE panchayat_settings
                SET panchayat_name = ?, panchayat_name_kn = ?, district = ?, taluk = ?,
                    helpline = ?, office_address = ?, contact_email = ?, villages_list = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (panchayat_name, panchayat_name_kn, district, taluk, helpline, office_address, contact_email, villages_list))
            conn.commit()
            flash("Gram Panchayat configuration updated successfully! Changes are live across the entire website.", "success")
            conn.close()
            return redirect(url_for('admin_settings'))

    settings = get_panchayat_settings()
    conn.close()
    return render_template('admin/settings.html', settings=settings)


# -------------------------------------------------------------
# REST API Endpoints for interactive modal & Chart.js data
# -------------------------------------------------------------

@app.route('/api/complaint/<complaint_id>')
def api_get_complaint(complaint_id):
    conn = get_db_connection()
    complaint = conn.execute("""
        SELECT c.*, u.full_name as citizen_name, u.mobile as citizen_mobile,
               cat.name_en as cat_name_en, cat.name_kn as cat_name_kn,
               cat.icon as cat_icon, cat.color as cat_color,
               d.name_en as dept_name_en, d.officer_name, d.officer_contact
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        JOIN categories cat ON c.category_id = cat.id
        LEFT JOIN departments d ON c.department_id = d.id
        WHERE c.complaint_id = ?
    """, (complaint_id,)).fetchone()

    if not complaint:
        conn.close()
        return jsonify({'error': 'Not found'}), 404

    history = conn.execute("""
        SELECT * FROM complaint_history
        WHERE complaint_id = ?
        ORDER BY created_at ASC
    """, (complaint['id'],)).fetchall()

    conn.close()

    return jsonify({
        'complaint': dict(complaint),
        'history': [dict(h) for h in history]
    })


@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    cat_stats = conn.execute("""
        SELECT cat.name_en, cat.color, COUNT(c.id) as count
        FROM categories cat
        LEFT JOIN complaints c ON cat.id = c.category_id
        GROUP BY cat.id
    """).fetchall()

    ward_stats = conn.execute("""
        SELECT ward_no, COUNT(*) as count
        FROM complaints
        GROUP BY ward_no
        ORDER BY ward_no ASC
    """).fetchall()

    status_stats = conn.execute("""
        SELECT status, COUNT(*) as count
        FROM complaints
        GROUP BY status
    """).fetchall()

    monthly_stats = conn.execute("""
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM complaints
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()

    conn.close()

    return jsonify({
        'categories': [dict(c) for c in cat_stats],
        'wards': [dict(w) for w in ward_stats],
        'status': [dict(s) for s in status_stats],
        'monthly': [dict(m) for m in monthly_stats]
    })


# -------------------------------------------------------------
# Main Application Entry Point
# -------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    print("==================================================================")
    print("  Grama Seva – Smart Gram Panchayat Complaint Management Portal  ")
    print("  Running on http://127.0.0.1:5000                                ")
    print("  Demo Admin:    username: admin   | password: admin123           ")
    print("  Demo Citizen:  username: citizen | password: citizen123         ")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
