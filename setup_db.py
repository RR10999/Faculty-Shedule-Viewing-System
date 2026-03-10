"""
Run this script ONCE to set up the database with sample data.
Usage: python setup_db.py
"""

import pymysql
import random
from werkzeug.security import generate_password_hash

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'BSHitman@999'   # ← Your MySQL password here
DB_NAME = 'faculty_schedule'

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                       charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cur.execute(f"USE {DB_NAME}")

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    student_id VARCHAR(20)
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    dept_short VARCHAR(20),
    designation VARCHAR(100),
    cabin VARCHAR(50),
    status ENUM('Free','Busy','In Class','On Leave') DEFAULT 'Free',
    manual_status VARCHAR(20) DEFAULT 'auto',
    leave_comment VARCHAR(255) DEFAULT ''
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    day_order INT NOT NULL,
    slot_number INT NOT NULL,
    subject VARCHAR(150),
    room VARCHAR(50),
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE,
    UNIQUE KEY unique_slot (faculty_id, day_order, slot_number)
)""")

conn.commit()
print("✓ Tables created")

# ── Admin ───────────────────────────────────────────────────────────────────────
cur.execute("INSERT IGNORE INTO admins (name, email, password) VALUES (%s, %s, %s)",
            ('Admin', 'admin@srm.edu.in', generate_password_hash('admin123')))

# ── Students ────────────────────────────────────────────────────────────────────
# ra2311030010173 = Radheya Rajan, ra2311030010174 = Paul A Mathew
students = [
    ('Mohammed Lazim',     'ra2311030010163@srm.edu.in', 'student123'),
    ('Radheya Rajan',  'ra2311030010173@srm.edu.in', 'student123'),
    ('Paul A Mathew',  'ra2311030010174@srm.edu.in', 'student123'),

]
for name, email, pw in students:
    cur.execute("INSERT IGNORE INTO students (name, email, password) VALUES (%s, %s, %s)",
                (name, email, generate_password_hash(pw)))

# ── Cabin number generator ───────────────────────────────────────────────────────
# Buildings: TP, TP2, UB — 15 floors, rooms 1–20 per floor


def make_cabin(building, floor, room):
    return f"{building} - {floor}{room:02d}"


# ── Faculty ─────────────────────────────────────────────────────────────────────
# (name, email, password, department, dept_short, designation, cabin)
faculty_data = [
    ('Dr. Raman Kumar', 'raman@srm.edu.in', 'faculty123',
     'Network & Communications', 'NWC', 'Associate Professor', make_cabin('TP', 2, 4)),
    ('Dr. Meera Nair', 'meera@srm.edu.in', 'faculty123',
     'Network & Communications', 'NWC', 'Assistant Professor', make_cabin('TP2', 9, 6)),
    ('Dr. Anand S', 'anand@srm.edu.in', 'faculty123',
     'Computing Technologies', 'CTECH', 'Associate Professor', make_cabin('UB', 7, 14)),
    ('Dr. Priya Sharma', 'priya@srm.edu.in', 'faculty123',
     'Computing Technologies', 'CTECH', 'Assistant Professor', make_cabin('TP', 5, 11)),
    ('Dr. Vijay Krishnan', 'vijay@srm.edu.in', 'faculty123',
     'Computational Intelligence', 'CINTEL', 'Associate Professor', make_cabin('TP2', 12, 3)),
    ('Dr. Lakshmi R', 'lakshmi@srm.edu.in', 'faculty123',
     'Network & Communications', 'NWC', 'Assistant Professor', make_cabin('UB', 3, 8)),
    ('Dr. Suresh P', 'suresh@srm.edu.in', 'faculty123',
     'Computing Technologies', 'CTECH', 'Associate Professor', make_cabin('TP', 10, 17)),
    ('Dr. Kavitha M', 'kavitha@srm.edu.in', 'faculty123',
     'Computational Intelligence', 'CINTEL', 'Assistant Professor', make_cabin('TP2', 6, 2)),
]

faculty_ids = []
for name, email, pw, dept, dept_short, designation, cabin in faculty_data:
    cur.execute("""INSERT IGNORE INTO faculty
        (name, email, password, department, dept_short, designation, cabin)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (name, email, generate_password_hash(pw), dept, dept_short, designation, cabin))
    cur.execute("SELECT id, cabin FROM faculty WHERE email=%s", (email,))
    row = cur.fetchone()
    if row:
        faculty_ids.append((row['id'], row['cabin']))

conn.commit()
print("✓ Faculty created")

# ── Subject pools per faculty ─────────────────────────────────────────────────
SUBJECTS = {
    0: [  # Dr. Raman Kumar - NWC
        ('Data Structures & Algorithms',        'TP - 204'),
        ('Design & Analysis of Algorithms',     'TP - 204'),
        ('Computer Networks',                   'NLH - 301'),
        ('Network Protocols & Architecture',    'Lab - NW1'),
    ],
    1: [  # Dr. Meera Nair - NWC
        ('Computer Networks',                   'TP2 - 906'),
        ('Wireless & Mobile Networks',          'TP2 - 906'),
        ('Network Security',                    'Lab - NW2'),
        ('Internet of Things',                  'NLH - 105'),
    ],
    2: [  # Dr. Anand S - CSE
        ('Operating Systems',                   'UB - 714'),
        ('Cloud Computing',                     'UB - 714'),
        ('Distributed Systems',                 'Lab - CS3'),
        ('Software Engineering & Project Mgmt', 'NLH - 304'),
    ],
    3: [  # Dr. Priya Sharma - CSE
        ('Database Management Systems',         'TP - 511'),
        ('Data Warehousing & Mining',           'TP - 511'),
        ('Big Data Analytics',                  'Lab - CS1'),
        ('Machine Learning',                    'NLH - 203'),
    ],
    4: [  # Dr. Vijay Krishnan - CYS
        ('Cyber Security & Ethical Hacking',    'TP2 - 1203'),
        ('Cryptography & Network Security',     'TP2 - 1203'),
        ('Penetration Testing',                 'Lab - CY1'),
        ('Firewall & Intrusion Detection Sys',  'NLH - 402'),
    ],
    5: [  # Dr. Lakshmi R - NWC
        ('Computer Networks',                   'UB - 308'),
        ('Network Administration',              'UB - 308'),
        ('Software Defined Networking',         'Lab - NW3'),
        ('5G & Next-Gen Networks',              'NLH - 106'),
    ],
    6: [  # Dr. Suresh P - CSE
        ('Data Structures & Algorithms',        'TP - 1017'),
        ('Compiler Design',                     'TP - 1017'),
        ('Theory of Computation',               'Lab - CS2'),
        ('Artificial Intelligence',             'NLH - 501'),
    ],
    7: [  # Dr. Kavitha M - CYS
        ('Cyber Security Fundamentals',         'TP2 - 602'),
        ('Digital Forensics',                   'TP2 - 602'),
        ('Malware Analysis',                    'Lab - CY2'),
        ('Risk & Compliance Management',        'NLH - 205'),
    ],
}

TIMETABLE_LAYOUTS = [
    [(1, 1, 0), (1, 3, 1), (1, 5, 2),  (2, 2, 0), (2, 4, 3), (2, 7, 1),  (3, 1, 2), (3, 4, 0), (3, 8, 3),
     (4, 2, 1), (4, 5, 2), (4, 9, 0),  (5, 1, 3), (5, 3, 0), (5, 5, 1)],
    [(1, 2, 0), (1, 4, 1), (1, 8, 2),  (2, 1, 0), (2, 5, 3), (2, 9, 1),  (3, 3, 2), (3, 5, 0), (3, 7, 3),
     (4, 1, 1), (4, 4, 2), (4, 8, 0),  (5, 2, 3), (5, 4, 1), (5, 7, 2)],
    [(1, 1, 0), (1, 5, 1), (1, 9, 2),  (2, 3, 0), (2, 7, 3), (2, 10, 1), (3, 2, 2), (3, 4, 0), (3, 8, 3),
     (4, 3, 1), (4, 7, 2), (4, 9, 0),  (5, 1, 3), (5, 5, 0), (5, 8, 1)],
    [(1, 3, 0), (1, 7, 1), (1, 10, 2), (2, 2, 0), (2, 5, 3), (2, 8, 1),  (3, 1, 2), (3, 4, 0), (3, 9, 3),
     (4, 2, 1), (4, 5, 2), (4, 7, 0),  (5, 3, 3), (5, 8, 0), (5, 9, 1)],
    [(1, 2, 0), (1, 5, 1), (1, 8, 2),  (2, 1, 0), (2, 4, 3), (2, 9, 1),  (3, 3, 2), (3, 7, 0), (3, 10, 3),
     (4, 1, 1), (4, 4, 2), (4, 8, 0),  (5, 2, 3), (5, 5, 1), (5, 7, 2)],
    [(1, 1, 0), (1, 4, 1), (1, 7, 2),  (2, 2, 0), (2, 5, 3), (2, 8, 1),  (3, 1, 2), (3, 3, 0), (3, 9, 3),
     (4, 4, 1), (4, 7, 2), (4, 10, 0), (5, 2, 3), (5, 4, 0), (5, 8, 1)],
    [(1, 3, 0), (1, 5, 1), (1, 9, 2),  (2, 1, 0), (2, 4, 3), (2, 7, 1),  (3, 2, 2), (3, 5, 0), (3, 8, 3),
     (4, 1, 1), (4, 3, 2), (4, 9, 0),  (5, 4, 3), (5, 7, 0), (5, 10, 1)],
    [(1, 2, 0), (1, 4, 1), (1, 10, 2), (2, 3, 0), (2, 7, 3), (2, 9, 1),  (3, 1, 2), (3, 5, 0), (3, 8, 3),
     (4, 2, 1), (4, 4, 2), (4, 7, 0),  (5, 1, 3), (5, 5, 1), (5, 9, 2)],
]

for fi, (fid, cabin) in enumerate(faculty_ids):
    if fi >= len(TIMETABLE_LAYOUTS):
        break
    # Lunch slot 6 — all 5 days
    for day in range(1, 6):
        cur.execute("INSERT IGNORE INTO timetable (faculty_id, day_order, slot_number, subject, room) VALUES (%s,%s,%s,%s,%s)",
                    (fid, day, 6, 'LUNCH', ''))
    # Class slots
    for day, slot, subj_idx in TIMETABLE_LAYOUTS[fi]:
        if subj_idx < len(SUBJECTS[fi]):
            subj_name, room = SUBJECTS[fi][subj_idx]
            cur.execute("INSERT IGNORE INTO timetable (faculty_id, day_order, slot_number, subject, room) VALUES (%s,%s,%s,%s,%s)",
                        (fid, day, slot, subj_name, room))

conn.commit()
cur.close()
conn.close()

print("✓ Timetables inserted")
print("\n✅ Database setup complete!")
print("\nLogin Credentials:")
print("  Admin   → admin@srm.edu.in / admin123")
print("  Faculty → raman@srm.edu.in / faculty123")
print("  Student → ra2311030010174@srm.edu.in / student123  (Paul A Mathew)")
print("  Student → ra2311030010173@srm.edu.in / student123  (Radheya Rajan)")
