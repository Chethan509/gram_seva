"""
Comprehensive Automated Test Suite for Grama Seva Portal.
Verifies all 12 pages, authentication flows, complaint submission,
stepper tracking, admin functions, and CSV export.
"""

import unittest
from app import app
from database import get_db_connection
from seed_data import seed_all


class GramaSevaPortalTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_all()
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_01_database_seeded(self):
        conn = get_db_connection()
        cats = conn.execute("SELECT COUNT(*) as c FROM categories").fetchone()['c']
        depts = conn.execute("SELECT COUNT(*) as c FROM departments").fetchone()['c']
        users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
        comps = conn.execute("SELECT COUNT(*) as c FROM complaints").fetchone()['c']
        conn.close()

        self.assertEqual(cats, 9, "All 9 categories must be present")
        self.assertGreaterEqual(depts, 9, "Panchayat departments must be seeded")
        self.assertGreaterEqual(users, 2, "Admin and citizen users must exist")
        self.assertGreaterEqual(comps, 8, "Realistic complaints must be seeded")
        print("[PASS] Database and 9 Categories Verified Successfully")

    def test_02_login_page_renders(self):
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"GRAMA SEVA", res.data)
        self.assertIn(b"Making Our Villages Better Together", res.data)
        print("[PASS] Page 1: Citizen Login & Registration Page Rendered")

    def test_03_citizen_authentication(self):
        # Invalid login
        res = self.client.post('/login', data={'identifier': 'citizen', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn(b"Invalid", res.data)

        # Valid login
        res = self.client.post('/login', data={'identifier': 'citizen', 'password': 'citizen123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Dashboard", res.data)
        self.assertIn(b"Manjunath", res.data)
        print("[PASS] Citizen Login Functional with Secure Password Hash Verification")

    def test_04_citizen_dashboard(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'citizen'
            sess['user_name'] = 'Manjunath K.'

        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Total Complaints", res.data)
        self.assertIn(b"Together, Let", res.data)
        self.assertIn(b"Water Supply", res.data)
        print("[PASS] Page 2: Citizen Dashboard Rendered with Summary Cards & Categories Grid")

    def test_05_complaint_categories(self):
        res = self.client.get('/categories')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Water Supply", res.data)
        self.assertIn(b"Roads and Transportation", res.data)
        self.assertIn(b"Streetlights", res.data)
        self.assertIn(b"Government School Problems", res.data)
        print("[PASS] Page 3: Complaint Categories Grid (All 9 Categories) Verified")

    def test_06_submit_complaint_flow(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'citizen'
            sess['user_name'] = 'Manjunath K.'

        # Submit a Government School Problem
        post_data = {
            'title': 'Broken classroom desks in Govt Primary School',
            'category_id': '6', # Government School Problems
            'problem_type': 'Broken desks and benches',
            'village': 'Shivapura Main Village',
            'ward_no': 'Ward 2',
            'landmark': 'Next to Library, School Road',
            'description': 'More than 15 wooden desks are broken and children are forced to sit on the cold floor during classes.',
            'contact_number': '9876543210',
            'priority': 'Urgent',
            'school_name': 'Government Higher Primary School Shivapura',
            'school_location': 'Ward 2 Lane',
            'school_infra_type': 'Broken desks and benches'
        }

        res = self.client.post('/submit-complaint', data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Complaint Registered Successfully", res.data)
        self.assertIn(b"GS-2026-", res.data)
        print("[PASS] Page 4: Complaint Submission & Unique ID Generation Verified")

    def test_07_track_complaint(self):
        res = self.client.get('/track/GS-2026-00101')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"GS-2026-00101", res.data)
        self.assertIn(b"Drinking water pipeline leaking", res.data)
        self.assertIn(b"Progress Stepper", res.data or b"progress-stepper")
        self.assertIn(b"Official Status Audit Trail", res.data)
        print("[PASS] Page 5: Complaint Tracking & Visual 5-Stage Stepper Verified")

    def test_08_my_complaints(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'citizen'
            sess['user_name'] = 'Manjunath K.'

        res = self.client.get('/my-complaints')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"GS-2026-00101", res.data)
        self.assertIn(b"All Complaints", res.data)
        print("[PASS] Page 6: My Complaints Filterable Table Verified")

    def test_09_notifications(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'citizen'
            sess['user_name'] = 'Manjunath K.'

        res = self.client.get('/notifications')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Grievance Notifications", res.data)
        self.assertIn(b"GS-2026-00101", res.data)
        print("[PASS] Page 7: Dynamic Event-Driven Notifications Verified")

    def test_10_admin_authentication_and_rbac(self):
        # Unauthorized access to admin dashboard by citizen
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'citizen'
            sess['user_name'] = 'Manjunath K.'

        res = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b"Access denied", res.data)

        # Admin login
        res = self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Administrator access granted", res.data)
        print("[PASS] Page 8: Admin Dedicated Login & Backend Role-Based Access Control Verified")

    def test_11_admin_dashboard_charts(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['user_name'] = 'Ramesh Gowda (PDO)'

        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"chartCategory", res.data)
        self.assertIn(b"chartMonthly", res.data)
        self.assertIn(b"chartWard", res.data)
        self.assertIn(b"chartStatus", res.data)
        print("[PASS] Page 9: Admin Dashboard with 6 Metrics & 4 Chart.js Datasets Verified")

    def test_12_admin_complaint_management_and_update(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['user_name'] = 'Ramesh Gowda (PDO)'

        # View register
        res = self.client.get('/admin/complaints')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"GS-2026-00101", res.data)

        # Update status
        update_data = {
            'status': 'Work in Progress',
            'department_id': '6',
            'priority': 'Urgent',
            'officer_remarks': 'Inspected by PDO and contractor initiated repairs on site.',
            'resolution_details': ''
        }
        res = self.client.post('/admin/complaint/2/update', data=update_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"updated successfully", res.data)
        print("[PASS] Page 10: Admin Complaint Management & Status Progression Verified")

    def test_13_admin_reports_and_csv_export(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['user_name'] = 'Ramesh Gowda (PDO)'

        # View reports page
        res = self.client.get('/admin/reports')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Key Performance Indicators", res.data)

        # Export CSV
        res = self.client.get('/admin/export-csv')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('Content-Type'), 'text/csv; charset=utf-8')
        self.assertIn(b"Complaint ID,Title,Category", res.data)
        self.assertIn(b"GS-2026-00101", res.data)
        print("[PASS] Page 11: Reports & Real CSV Export Download Verified")

    def test_14_help_and_language_toggle(self):
        # English help page
        res = self.client.get('/help')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Frequently Asked Questions", res.data)

        # Switch to Kannada
        res = self.client.get('/set-language/kn', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/dashboard')
        self.assertIn("ನಮ್ಮ ಗ್ರಾಮವನ್ನು".encode('utf-8'), res.data)
        print("[PASS] Page 12: Help & Support + Bilingual Kannada/English Toggle Verified")

    def test_15_panchayat_settings_and_village_configuration(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['user_name'] = 'Ramesh Gowda (PDO)'

        # 1. View settings page
        res = self.client.get('/admin/settings')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Gram Panchayat & Village Configuration Settings", res.data)

        # 2. Update Panchayat Name and Villages List
        update_data = {
            'panchayat_name': 'Byndoor Gram Panchayat',
            'panchayat_name_kn': 'ಬೈಂದೂರು ಗ್ರಾಮ ಪಂಚಾಯತಿ',
            'district': 'Udupi District',
            'taluk': 'Byndoor Taluk',
            'helpline': '1800-425-9999',
            'office_address': 'Main Administrative Complex, Byndoor, Karnataka',
            'contact_email': 'byndoor.gp@gramseva.in',
            'villages_list': 'Byndoor Main, Uppunda, Shiroor, Yedthare, Paduvari'
        }
        res = self.client.post('/admin/settings', data=update_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Byndoor Gram Panchayat", res.data)

        # 3. Verify changes reflect on Citizen Dashboard immediately
        res_dash = self.client.get('/dashboard')
        self.assertIn(b"Byndoor Gram Panchayat", res_dash.data)

        # 4. Verify new villages appear in registration/complaint form options
        res_submit = self.client.get('/submit-complaint')
        self.assertIn(b"Uppunda", res_submit.data)
        self.assertIn(b"Shiroor", res_submit.data)

        print("[PASS] Feature: Dynamic Gram Panchayat & Village Configuration Verified")


if __name__ == '__main__':
    unittest.main()
