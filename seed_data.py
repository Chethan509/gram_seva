"""
Seed realistic demo data for Grama Seva Portal.
Includes Gram Panchayat administrative departments, 9 official categories,
demo users (admin & citizens), and representative complaints with status histories.
"""

from werkzeug.security import generate_password_hash
from database import get_db_connection, init_db
from datetime import datetime, timedelta


def seed_all():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing demo data
    cursor.execute("DELETE FROM citizen_feedback")
    cursor.execute("DELETE FROM notifications")
    cursor.execute("DELETE FROM complaint_history")
    cursor.execute("DELETE FROM complaints")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM departments")
    cursor.execute("DELETE FROM users")

    # Reset SQLite autoincrement sequence
    cursor.execute("DELETE FROM sqlite_sequence")

    # 1. Seed Departments
    departments_data = [
        ("RWSS", "Rural Water Supply & Sanitation", "ಗ್ರಾಮೀಣ ಕುಡಿಯುವ ನೀರು ಸರಬರಾಜು", "K. Suresh (AE)", "9845011001", "rwss.shivapura@gramseva.in"),
        ("PWD", "Roads & Village Infrastructure (PWD)", "ರಸ್ತೆಗಳು ಮತ್ತು ಮೂಲಸೌಕರ್ಯ", "H. Venkatesh (JE)", "9845011002", "pwd.shivapura@gramseva.in"),
        ("ELEC", "Electrical & Street Lighting Cell", "ವಿದ್ಯುತ್ ಮತ್ತು ಬೀದಿದೀಪ ವಿಭಾಗ", "Anand Kumar (Lineman)", "9845011003", "electrical.shivapura@gramseva.in"),
        ("SWM", "Solid Waste Management & Sanitation", "ಘನತ್ಯಾಜ್ಯ ನಿರ್ವಹಣೆ ಮತ್ತು ನೈರ್ಮಲ್ಯ", "Chennamma (Health Supervisor)", "9845011004", "swm.shivapura@gramseva.in"),
        ("DRAIN", "Underground Drainage & Sewerage", "ಒಳಚರಂಡಿ ಮತ್ತು ನೈರ್ಮಲ್ಯ ವಿಭಾಗ", "Ravi Patil (Supervisor)", "9845011005", "drainage.shivapura@gramseva.in"),
        ("EDU", "Panchayat Education Committee / BEO", "ಪಂಚಾಯತ್ ಶಿಕ್ಷಣ ಸಮಿತಿ / ಬಿ.ಇ.ಒ", "Smt. Shailaja (Block Resource Coord.)", "9845011006", "education.shivapura@gramseva.in"),
        ("HEALTH", "Public Health Center (PHC) & Ayush", "ಸಾರ್ವಜನಿಕ ಪ್ರಾಥಮಿಕ ಆರೋಗ್ಯ ಕೇಂದ್ರ", "Dr. Raghavendra (MO)", "9845011007", "phc.shivapura@gramseva.in"),
        ("CIVIC", "Village Assets & Community Spaces", "ಗ್ರಾಮ ಆಸ್ತಿ ಮತ್ತು ಸಮುದಾಯ ಭವನ", "Pradeep N. (Revenue Inspector)", "9845011008", "assets.shivapura@gramseva.in"),
        ("ADMIN", "Gram Panchayat General Administration", "ಗ್ರಾಮ ಪಂಚಾಯತಿ ಸಾರ್ವಜನಿಕ ಆಡಳಿತ", "Ramesh Gowda (PDO)", "9845011009", "pdo.shivapura@gramseva.in")
    ]

    cursor.executemany("""
        INSERT INTO departments (code, name_en, name_kn, officer_name, officer_contact, email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, departments_data)

    # 2. Seed Categories (9 specific required categories)
    categories_data = [
        (
            "water",
            "Water Supply",
            "ಕುಡಿಯುವ ನೀರು ಸರಬರಾಜು",
            "fa-solid fa-droplet",
            "#0284c7",
            "Report drinking water shortages, leaking main supply pipelines, contaminated water, or damaged public borewells/taps.",
            "ಕುಡಿಯುವ ನೀರಿನ ಕೊರತೆ, ಪೈಪ್‌ಲೈನ್ ಸೋರಿಕೆ, ಕಲುಷಿತ ನೀರು ಅಥವಾ ಸಾರ್ವಜನಿಕ ನಲ್ಲಿಗಳ ದುರಸ್ತಿ ಬಗ್ಗೆ ದೂರು ಸಲ್ಲಿಸಿ.",
            "Water shortage, leaking pipes, damaged water taps, low water pressure",
            "ನೀರಿನ ಕೊರತೆ, ಪೈಪ್ ಒಡೆದಿರುವುದು, ನಲ್ಲಿ ಮುರಿದಿರುವುದು",
            1
        ),
        (
            "roads",
            "Roads and Transportation",
            "ರಸ್ತೆಗಳು ಮತ್ತು ಸಾರಿಗೆ",
            "fa-solid fa-road",
            "#ea580c",
            "Report dangerous potholes, broken concrete roads, lack of street signs, or obstructed village pathways.",
            "ರಸ್ತೆ ಗುಂಡಿಗಳು, ಹಾಳಾದ ಕಾಂಕ್ರೀಟ್ ರಸ್ತೆಗಳು, ಸಾರಿಗೆ ಅಡಚಣೆಗಳ ಬಗ್ಗೆ ದೂರು ದಾಖಲಿಸಿ.",
            "Potholes, damaged roads, unsafe village roads, unpaved muddy road",
            "ಗುಂಡಿಗಳು ಬಿದ್ದ ರಸ್ತೆ, ಹಾಳಾದ ಚರಂಡಿ ಪಕ್ಕದ ರಸ್ತೆ",
            2
        ),
        (
            "streetlights",
            "Streetlights",
            "ಬೀದಿದೀಪಗಳು",
            "fa-solid fa-lightbulb",
            "#eab308",
            "Report non-functioning streetlights, fused bulbs, broken light poles, or dark stretches requiring new lighting.",
            "ಬೆಳಗದ ಬೀದಿದೀಪಗಳು, ಮುರಿದ ಕಂಬಗಳು, ಹೊಸ ಬೀದಿದೀಪ ಅಳವಡಿಕೆ ಬಗ್ಗೆ ದೂರು ಸಲ್ಲಿಸಿ.",
            "Streetlights not working, damaged streetlight poles, flickering bulbs",
            "ಬೀದಿದೀಪ ಬೆಳಗುತ್ತಿಲ್ಲ, ಮುರಿದ ವಿದ್ಯುತ್ ಕಂಬ, ವೈರ್ ತುಂಡಾಗಿದೆ",
            3
        ),
        (
            "garbage",
            "Garbage Collection",
            "ಕಸ ವಿಲೇವಾರಿ ಮತ್ತು ನೈರ್ಮಲ್ಯ",
            "fa-solid fa-trash-can",
            "#16a34a",
            "Report uncollected garbage heaps, overflowing community waste bins, littering, or illegal dumping on roadsides.",
            "ಕಸ ಸಂಗ್ರಹವಾಗದಿರುವುದು, ತುಂಬಿ ತುಳುಕುತ್ತಿರುವ ಕಸದ ತೊಟ್ಟಿಗಳು, ಎಲ್ಲೆಂದರಲ್ಲಿ ಕಸ ಎಸೆಯುವ ಬಗ್ಗೆ ದೂರು ನೀಡಿ.",
            "Uncollected garbage, overflowing public bins, open dumping, animal scavengers",
            "ಸಮಯಕ್ಕೆ ಕಸ ವಿಲೇವಾರಿ ಆಗದಿರುವುದು, ರಸ್ತೆಯಲ್ಲಿ ಕಸ ಸಂಗ್ರಹ",
            4
        ),
        (
            "drainage",
            "Drainage and Sanitation",
            "ಒಳಚರಂಡಿ ಮತ್ತು ಸ್ವಚ್ಛತೆ",
            "fa-solid fa-faucet-drip",
            "#0d9488",
            "Report clogged storm drains, overflowing sewage lines, stagnant dirty water creating mosquito menace.",
            "ಮುಚ್ಚಿಹೋದ ಚರಂಡಿಗಳು, ರಸ್ತೆಗೆ ಹರಿಯುವ ಕೊಳಚೆ ನೀರು, ಸೊಳ್ಳೆಗಳ ಕಾಟದ ಬಗ್ಗೆ ವರದಿ ಮಾಡಿ.",
            "Blocked drains, overflowing sewage, poor sanitation, foul smell",
            "ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ, ಕೊಳಚೆ ನೀರು ರಸ್ತೆಗೆ ಹರಿಯುವುದು",
            5
        ),
        (
            "schools",
            "Government School Problems",
            "ಸರ್ಕಾರಿ ಶಾಲೆಗಳ ಸಮಸ್ಯೆಗಳು",
            "fa-solid fa-school",
            "#8b5cf6",
            "Report school infrastructure issues: broken classrooms, leaking roofs, damaged compound walls, dirty toilets, or lack of drinking water.",
            "ಸರ್ಕಾರಿ ಶಾಲೆಗಳ ಕೊಠಡಿ ದುರಸ್ತಿ, ಮುರಿದ ಬೆಂಚುಗಳು, ಸ್ವಚ್ಛ ಶೌಚಾಲಯ ಮತ್ತು ಕುಡಿಯುವ ನೀರಿನ ಸಮಸ್ಯೆಗಳನ್ನು ದಾಖಲಿಸಿ.",
            "Damaged classrooms/roofs, broken/unclean school toilets, lack of drinking water, electricity faults, broken desks and benches, damaged compound walls",
            "ಶಾಲೆ ಕೊಠಡಿ ಸೋರಿಕೆ, ಶೌಚಾಲಯ ಸ್ವಚ್ಛತೆ ಇಲ್ಲದಿರುವುದು, ಕುಡಿಯುವ ನೀರಿಲ್ಲ, ಮುರಿದ ಬೆಂಚು-ಡೆಸ್ಕ್",
            6
        ),
        (
            "health",
            "Public Health Facilities",
            "ಸಾರ್ವಜನಿಕ ಆರೋಗ್ಯ ಕೇಂದ್ರಗಳು",
            "fa-solid fa-notes-medical",
            "#ef4444",
            "Report issues at Village Sub-Center/PHC: lack of basic medicines, sanitation problems, unavailable staff, or unhygienic premises.",
            "ಗ್ರಾಮ ಆರೋಗ್ಯ ಕೇಂದ್ರ, ಉಪಕೇಂದ್ರಗಳಲ್ಲಿ ಔಷಧ ಕೊರತೆ, ಅಶುಚಿತ್ವ, ಮೂಲಸೌಕರ್ಯ ಕೊರತೆ ಬಗ್ಗೆ ದೂರು ನೀಡಿ.",
            "Damaged public health facilities, sanitation problems in clinics, lack of clean water in PHC",
            "ಆರೋಗ್ಯ ಕೇಂದ್ರದಲ್ಲಿ ನೀರಿಲ್ಲದಿರುವುದು, ಅಶುಚಿತ್ವ, ಸೌಲಭ್ಯಗಳ ಕೊರತೆ",
            7
        ),
        (
            "facilities",
            "Public Facilities",
            "ಸಾರ್ವಜನಿಕ ಸಮುದಾಯ ಸೌಲಭ್ಯಗಳು",
            "fa-solid fa-landmark",
            "#6366f1",
            "Report damaged community halls, village library infrastructure, public bus shelters, anganwadi centers, or parks.",
            "ಸಮುದಾಯ ಭವನ, ಗ್ರಾಮ ಗ್ರಂಥಾಲಯ, ಬಸ್ ನಿಲ್ದಾಣ ಆಶ್ರಯ ತಾಣ, ಅಂಗನವಾಡಿ ಕೇಂದ್ರಗಳ ಸಮಸ್ಯೆಗಳು.",
            "Damaged public spaces, broken bus stand shelter, damaged community hall, anganwadi issues",
            "ಹಾಳಾದ ಸಮುದಾಯ ಭವನ, ಬಸ್ ತಂಗುದಾಣದ ಛಾವಣಿ ಮುರಿದಿರುವುದು",
            8
        ),
        (
            "other",
            "Other Problems",
            "ಇತರ ಸಾರ್ವಜನಿಕ ಸಮಸ್ಯೆಗಳು",
            "fa-solid fa-file-circle-question",
            "#64748b",
            "Report civic complaints, stray cattle/animal menace, encroachment of village grazing land, or unlisted issues.",
            "ಮೇಲಿನ ಯಾವುದೇ ವಿಭಾಗಕ್ಕೆ ಸೇರದ ಇತರೆ ನಾಗರಿಕ ಮತ್ತು ಪಂಚಾಯತಿ ಸಮಸ್ಯೆಗಳ ಬಗ್ಗೆ ದೂರು ಸಲ್ಲಿಸಿ.",
            "Problems that do not fit other categories, stray animals, encroachment, noise issues",
            "ಇತರ ಸಾರ್ವಜನಿಕ ತೊಂದರೆಗಳು, ದಾರಿ ಒತ್ತುವರಿ, ಜಾನುವಾರು ಸಮಸ್ಯೆ",
            9
        )
    ]

    cursor.executemany("""
        INSERT INTO categories (code, name_en, name_kn, icon, color, description_en, description_kn, examples_en, examples_kn, default_dept_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, categories_data)

    # 3. Seed Users
    # Admin user: username 'admin', password 'admin123'
    # Citizen user 1: username 'citizen' (or '9876543210'), password 'citizen123'
    # Citizen user 2: username '9876543211', password 'citizen123'
    # Citizen user 3: username '9876543212', password 'citizen123'

    admin_pwd = generate_password_hash("admin123")
    citizen_pwd = generate_password_hash("citizen123")

    users_data = [
        ("Ramesh Gowda (PDO)", "admin", "9845012345", "pdo.shivapura@gramseva.in", "Shivapura Main Village", "Ward 1", admin_pwd, "admin"),
        ("Manjunath K.", "citizen", "9876543210", "manjunath.k@gmail.com", "Shivapura Main Village", "Ward 2", citizen_pwd, "citizen"),
        ("Lakshmi Devi", "9876543211", "9876543211", "lakshmi.devi@gmail.com", "Shivapura Gollarahatti", "Ward 3", citizen_pwd, "citizen"),
        ("Basavaraju S.", "9876543212", "9876543212", "basavaraj.s@yahoo.com", "Shivapura Kerekoppalu", "Ward 1", citizen_pwd, "citizen"),
        ("Anitha Bai", "9876543213", "9876543213", "anitha.bai@gmail.com", "Shivapura Harijanawada", "Ward 4", citizen_pwd, "citizen")
    ]

    cursor.executemany("""
        INSERT INTO users (full_name, username, mobile, email, village, ward_no, password_hash, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    # 4. Seed Realistic Complaints
    now = datetime.now()
    d1 = (now - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")
    d2 = (now - timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S")
    d3 = (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")
    d4 = (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")
    d5 = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    d6 = (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    d7 = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    complaints_data = [
        (
            "GS-2026-00101",
            2, # Manjunath
            1, # Water Supply
            "Drinking water pipeline leaking near Anjaneya Temple",
            "Leaking pipes",
            "Shivapura Main Village",
            "Ward 2",
            "Near Anjaneya Temple Main Circle",
            "The main underground pipeline connecting the overhead tank has ruptured. Clean drinking water is overflowing onto the street for 3 days and households are facing acute water pressure shortage in the morning.",
            "/static/images/uploads/sample_water_leak.svg",
            "9876543210",
            "High",
            "Resolved",
            1, # RWSS
            "Pipeline repaired and replacement coupling installed. Water supply pressure restored to normal.",
            "Gram Panchayat water linemen inspected the leak on Oct 11, dug up the faulty segment, replaced a 10-foot PVC 4-inch pipe, and re-tested water flow successfully.",
            None, None, None,
            d1, (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            "GS-2026-00102",
            2, # Manjunath
            6, # Government School Problems
            "Damaged classroom roof and broken window panes in Govt Primary School",
            "Damaged classrooms or school buildings",
            "Shivapura Main Village",
            "Ward 2",
            "Opposite Panchayat Library, School Road",
            "Classroom 4 and 5 in the Government Higher Primary School have severe roof plaster peeling, causing rainwater seepage. 3 window panes are shattered, posing a physical danger to children during class hours.",
            "/static/images/uploads/sample_school_issue.svg",
            "9876543210",
            "Urgent",
            "In Progress",
            6, # Education Committee
            "Inspected jointly by Panchayat Junior Engineer and BEO representative. Contractor work order issued under Gram Panchayat Special Education Maintenance Fund.",
            None,
            "Government Higher Primary School, Shivapura",
            "Near Post Office, School Lane, Ward 2",
            "Damaged classroom ceiling & shattered window panes",
            d2, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), None
        ),
        (
            "GS-2026-00103",
            2, # Manjunath
            3, # Streetlights
            "3 Streetlights not glowing on Temple Street for over a week",
            "Streetlights not working",
            "Shivapura Main Village",
            "Ward 2",
            "Pole Nos. SP-24, SP-25 near Basaveshwara Temple",
            "Three consecutive street lights on the main temple street are completely dark. Women and senior citizens are feeling unsafe walking in the dark after 7 PM due to stray dogs.",
            "/static/images/uploads/sample_streetlight.svg",
            "9876543210",
            "Medium",
            "Assigned",
            3, # Electrical Cell
            "Assigned to electrical lineman Anand Kumar. Replacement 45W LED fixtures indented from taluk sub-station.",
            None,
            None, None, None,
            d3, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), None
        ),
        (
            "GS-2026-00104",
            3, # Lakshmi Devi
            4, # Garbage Collection
            "Overflowing public waste bin and uncollected garbage near Weekly Haat",
            "Overflowing public bins",
            "Shivapura Gollarahatti",
            "Ward 3",
            "Near Shandy Market Gate / Dairy Union",
            "The community garbage bin has not been cleared for 5 days. Debris is scattered all over the roadside and cows/dogs are rummaging through plastic bags. Strong foul odor entering surrounding homes.",
            "/static/images/uploads/sample_garbage.svg",
            "9876543211",
            "Medium",
            "Resolved",
            4, # SWM
            "Tractor collection vehicle cleared the spot and bleaching powder was sprinkled across the vicinity.",
            "Panchayat sanitation vehicle visited on Oct 18, cleared 2.5 tons of wet and dry waste, and instructed market vendors to use designated bins.",
            None, None, None,
            d4, (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        ),
        (
            "GS-2026-00105",
            4, # Basavaraju
            2, # Roads and Transportation
            "Deep potholes on Shivapura - Kerekoppalu connecting road",
            "Potholes",
            "Shivapura Kerekoppalu",
            "Ward 1",
            "Near Milk Dairy Collection Center curve",
            "A series of 4 deep potholes have formed on the main asphalt road after heavy rains. Two two-wheeler riders suffered minor falls yesterday night. Immediate gravel and cold-mix patch work required.",
            "/static/images/uploads/sample_potholes.svg",
            "9876543212",
            "High",
            "Under Review",
            2, # PWD
            "Field survey scheduled by Assistant Engineer tomorrow morning for estimating patch work cost.",
            None,
            None, None, None,
            d5, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), None
        ),
        (
            "GS-2026-00106",
            5, # Anitha Bai
            5, # Drainage and Sanitation
            "Blocked stone drain causing foul water stagnation near Anganwadi",
            "Blocked drains",
            "Shivapura Harijanawada",
            "Ward 4",
            "Behind Government Anganwadi Center 2",
            "The roadside drain is completely blocked with silt, plastic, and tree branches. Wastewater is overflowing into the open courtyard where children play. Urgent de-silting is required.",
            "/static/images/uploads/sample_drainage.svg",
            "9876543213",
            "High",
            "In Progress",
            5, # Drainage
            "Sanitation crew mobilized with safety equipment for complete desilting of 60 meters drain.",
            None,
            None, None, None,
            d6, (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"), None
        ),
        (
            "GS-2026-00107",
            2, # Manjunath
            7, # Public Health Facilities
            "Damaged gate and lack of potable drinking water in Village Health Sub-Center",
            "Damaged public facilities and sanitation problems",
            "Shivapura Main Village",
            "Ward 2",
            "Next to Veterinary Hospital",
            "The handpump at the Health Sub-Center has been defunct for two weeks. Pregnant mothers and infants coming for immunization have no drinking water facility. Stray goats entering through broken gate.",
            "/static/images/uploads/sample_clinic.svg",
            "9876543210",
            "Medium",
            "Submitted",
            7, # Health
            None,
            None,
            None, None, None,
            d7, d7, None
        ),
        (
            "GS-2026-00108",
            3, # Lakshmi Devi
            6, # Government School Problems
            "Lack of functional drinking water tap and broken toilets in Govt High School",
            "Broken or unclean school toilets",
            "Shivapura Gollarahatti",
            "Ward 3",
            "Near Grama Chavadikatte, High School Campus",
            "Girls toilet block has broken doors and no running tap water. Water filter installed last year has stopped functioning. Students are forced to return home during interval.",
            "/static/images/uploads/sample_school_issue.svg",
            "9876543211",
            "Urgent",
            "Assigned",
            6, # Education Committee
            "Referred urgently to Gram Panchayat Education Sub-Committee and RWSS section for immediate pipe connection.",
            None,
            "Government High School, Shivapura Gollarahatti",
            "Campus Ground, Ward 3",
            "Broken toilet doors and defunct RO water unit",
            (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), None
        ),
        (
            "GS-2026-00109",
            4, # Basavaraju
            8, # Public Facilities
            "Damaged roof tiles on Community Hall (Samudaya Bhavana)",
            "Damaged public spaces and community facilities",
            "Shivapura Kerekoppalu",
            "Ward 1",
            "Dr. B.R. Ambedkar Samudaya Bhavana",
            "Several Mangalore clay tiles on the community hall roof slipped during recent storm winds. Water leaked inside damaging wooden stage and chairs. Community meetings cannot be held.",
            None,
            "9876543212",
            "Low",
            "Under Review",
            8, # Village Assets
            "Inspected by Revenue Inspector. Repair work estimated at Rs. 14,500 under 15th Finance Commission grant.",
            None,
            None, None, None,
            (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), None
        ),
        (
            "GS-2026-00110",
            5, # Anitha Bai
            9, # Other Problems
            "Private construction debris blocking public cart track / Rajakaluve path",
            "Problems that do not fit other categories",
            "Shivapura Harijanawada",
            "Ward 4",
            "Survey No. 42 / Raja Kaluve boundary",
            "A private landholder has dumped granite boulders and soil onto the public pathway leading to agricultural fields, preventing bullock carts and tractors from passing.",
            None,
            "9876543213",
            "Medium",
            "Rejected",
            9, # General Admin
            "After spot inspection by Village Accountant, the dispute was determined to be a private boundary civil litigation pending before the Taluk Tahsildar Court. Outside Gram Panchayat executive jurisdiction.",
            "Complainant advised to approach Tahsildar / Revenue Court for survey demarcation.",
            None, None, None,
            (now - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"), None
        )
    ]

    cursor.executemany("""
        INSERT INTO complaints (
            complaint_id, user_id, category_id, title, problem_type, village, ward_no,
            landmark, description, photo_url, contact_number, priority, status,
            department_id, officer_remarks, resolution_details,
            school_name, school_location, school_infra_type,
            created_at, updated_at, resolved_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, complaints_data)

    # 5. Seed Status History for Complaints
    # Complaint 1 history (GS-2026-00101)
    histories = [
        (1, "Submitted", "Complaint registered online by citizen Manjunath K.", "Citizen", d1),
        (1, "Under Review", "Complaint verified by Panchayat Development Officer (PDO). Urgent water line failure confirmed.", "Ramesh Gowda (PDO)", (now - timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S")),
        (1, "Assigned", "Assigned to Rural Water Supply & Sanitation (RWSS) Section.", "Ramesh Gowda (PDO)", (now - timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S")),
        (1, "Work in Progress", "Water linemen dispatched with replacement pipes and trenching tools.", "K. Suresh (AE)", (now - timedelta(days=10, hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
        (1, "Resolved", "Pipeline replacement completed and water flow tested successfully. Area restored.", "K. Suresh (AE)", (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),

        # Complaint 2 history (GS-2026-00102)
        (2, "Submitted", "Complaint registered regarding Govt Primary School infrastructure.", "Citizen", d2),
        (2, "Under Review", "Verified by Panchayat PDO and marked for Education Committee coordination.", "Ramesh Gowda (PDO)", (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")),
        (2, "Assigned", "Assigned to Panchayat Education Committee & PWD JE for technical estimate.", "Ramesh Gowda (PDO)", (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
        (2, "Work in Progress", "Technical estimate sanctioned. Repair materials arrived at school site.", "Smt. Shailaja (BEO)", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),

        # Complaint 3 history (GS-2026-00103)
        (3, "Submitted", "Complaint registered regarding 3 non-working streetlights.", "Citizen", d3),
        (3, "Under Review", "Reviewed by Village Electrician cell.", "Ramesh Gowda (PDO)", (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        (3, "Assigned", "Assigned to Electrical Lineman Anand Kumar.", "Ramesh Gowda (PDO)", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),

        # Complaint 4 history (GS-2026-00104)
        (4, "Submitted", "Complaint submitted for uncollected waste near Shandy Market.", "Citizen", d4),
        (4, "Under Review", "Verified by Health Supervisor Chennamma.", "Ramesh Gowda (PDO)", (now - timedelta(days=3, hours=10)).strftime("%Y-%m-%d %H:%M:%S")),
        (4, "Work in Progress", "Sanitation auto-tipper and JCB mobilized for mass clearing.", "Chennamma (Health Sup.)", (now - timedelta(days=3, hours=6)).strftime("%Y-%m-%d %H:%M:%S")),
        (4, "Resolved", "Waste cleared, site disinfected with bleaching powder, warning banner placed.", "Chennamma (Health Sup.)", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),

        # Complaint 5 history (GS-2026-00105)
        (5, "Submitted", "Complaint submitted for potholes on Kerekoppalu road.", "Citizen", d5),
        (5, "Under Review", "Assistant Engineer scheduled site visit for measurements.", "H. Venkatesh (JE)", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),

        # Complaint 6 history (GS-2026-00106)
        (6, "Submitted", "Complaint submitted for drain blockage near Anganwadi.", "Citizen", d6),
        (6, "Assigned", "Assigned to Drainage & Sanitation crew.", "Ramesh Gowda (PDO)", (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")),
        (6, "Work in Progress", "Laborers started desilting drain channel.", "Ravi Patil (Supervisor)", (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")),

        # Complaint 7 history (GS-2026-00107)
        (7, "Submitted", "Complaint submitted for Health Sub-center water issue.", "Citizen", d7),

        # Complaint 10 history (GS-2026-00110)
        (10, "Submitted", "Complaint submitted regarding road blockage.", "Citizen", (now - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")),
        (10, "Under Review", "Spot inquiry conducted with Revenue Inspector and Village Accountant.", "Ramesh Gowda (PDO)", (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")),
        (10, "Rejected", "Rejected: Private title dispute in revenue civil court outside Gram Panchayat scope.", "Ramesh Gowda (PDO)", (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
    ]

    cursor.executemany("""
        INSERT INTO complaint_history (complaint_id, status, remarks, action_by, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, histories)

    # 6. Seed Notifications for Citizen (User ID 2: Manjunath)
    notifications_data = [
        (2, 1, "Complaint Resolved: GS-2026-00101", "Your complaint regarding 'Water pipeline leaking' has been successfully resolved by the RWSS team.", "success", 0, (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
        (2, 2, "Status Updated: GS-2026-00102", "Work has started on your complaint regarding Government Primary School roof repairs. Contractor is on site.", "info", 0, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        (2, 3, "Assigned: GS-2026-00103", "Your streetlight complaint has been assigned to Electrical Lineman Anand Kumar.", "info", 1, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
        (2, 7, "Complaint Registered: GS-2026-00107", "Your complaint regarding Health Sub-Center has been registered with ID GS-2026-00107.", "info", 1, d7)
    ]

    cursor.executemany("""
        INSERT INTO notifications (user_id, complaint_id, title, message, type, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, notifications_data)

    # 7. Seed Citizen Feedback
    feedback_data = [
        (2, 1, 5, "Prompt response by Panchayat within 2 days! The water pipeline was neatly repaired. Thank you Grama Seva.", (now - timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S")),
        (3, 4, 4, "Garbage was cleaned and bleaching powder was put. Very happy with the online tracking.", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
    ]

    cursor.executemany("""
        INSERT INTO citizen_feedback (user_id, complaint_id, rating, comments, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, feedback_data)

    conn.commit()
    conn.close()
    print("Realistic demo data seeded successfully!")


if __name__ == '__main__':
    seed_all()
