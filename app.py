from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'faculty_schedule_secret_2025'


@app.context_processor
def inject_session():
    from flask import session as _session
    return dict(session=_session)


# ── UPDATE YOUR MYSQL PASSWORD HERE ────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'BSHitman@999',   # ← put your MySQL password here
    'database': 'faculty_schedule',
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4',
}


def get_db():
    return pymysql.connect(**DB_CONFIG)


TIME_SLOTS = [
    {'id': 1,  'label': '08:00 – 08:50'},
    {'id': 2,  'label': '08:50 – 09:40'},
    {'id': 3,  'label': '09:45 – 10:35'},
    {'id': 4,  'label': '10:40 – 11:30'},
    {'id': 5,  'label': '11:35 – 12:25'},
    {'id': 6,  'label': '12:30 – 01:20'},
    {'id': 7,  'label': '01:25 – 02:15'},
    {'id': 8,  'label': '02:20 – 03:10'},
    {'id': 9,  'label': '03:10 – 04:00'},
    {'id': 10, 'label': '04:00 – 04:50'},
    {'id': 11, 'label': '04:50 – 05:30'},
    {'id': 12, 'label': '05:30 – 06:10'},
]

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


def get_day_order():
    weekday = datetime.now().weekday()
    return weekday + 1 if weekday < 5 else 1


def get_timetable_status(faculty_id):
    day_order = get_day_order()
    now = datetime.now()
    current_min = now.hour * 60 + now.minute
    slot_times = [
        (8*60, 8*60+50), (8*60+50, 9*60+40), (9*60+45, 10*60+35),
        (10*60+40, 11*60+30), (11*60+35, 12*60+25), (12*60+30, 13*60+20),
        (13*60+25, 14*60+15), (14*60+20, 15*60+10), (15*60+10, 16*60),
        (16*60, 16*60+50), (16*60+50, 17*60+30), (17*60+30, 18*60+10),
    ]
    conn = get_db()
    try:
        with conn.cursor() as cur:
            for i, (start, end) in enumerate(slot_times):
                if start <= current_min < end:
                    slot_num = i + 1
                    cur.execute("SELECT subject FROM timetable WHERE faculty_id=%s AND day_order=%s AND slot_number=%s",
                                (faculty_id, day_order, slot_num))
                    row = cur.fetchone()
                    return 'In Class' if (row and row['subject'] and row['subject'].strip()) else 'Free'
    finally:
        conn.close()
    return 'Free'


def get_faculty_status(faculty_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, manual_status FROM faculty WHERE id=%s", (faculty_id,))
            f = cur.fetchone()
    finally:
        conn.close()
    if not f:
        return 'Free'
    if f['status'] == 'On Leave':
        return 'On Leave'
    if f['manual_status'] and f['manual_status'] != 'auto':
        return f['manual_status']
    return get_timetable_status(faculty_id)

# ── AUTH ────────────────────────────────────────────────────────────────────────


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student')
        table = {'student': 'students', 'faculty': 'faculty',
                 'admin': 'admins'}.get(role)
        if table:
            conn = get_db()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT * FROM {table} WHERE email=%s", (email,))
                    user = cur.fetchone()
            finally:
                conn.close()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['role'] = role
                session['name'] = user['name']
                return redirect(url_for(f'{role}_dashboard'))
        error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── STUDENT ─────────────────────────────────────────────────────────────────────


@app.route('/student')
def student_dashboard():
    if session.get('role') not in ('student', 'faculty'):
        return redirect(url_for('login'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty ORDER BY name ASC")
            faculties = cur.fetchall()
    finally:
        conn.close()
    for f in faculties:
        f['effective_status'] = get_faculty_status(f['id'])
    now = datetime.now()
    return render_template('student_dashboard.html',
                           faculties=faculties, now=now, day_order=get_day_order(),
                           role=session.get('role'), name=session.get('name'))


@app.route('/faculty_detail/<int:faculty_id>')
def faculty_detail(faculty_id):
    if session.get('role') not in ('student', 'faculty'):
        return redirect(url_for('login'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty WHERE id=%s", (faculty_id,))
            faculty = cur.fetchone()
            cur.execute(
                "SELECT day_order, slot_number, subject, room FROM timetable WHERE faculty_id=%s", (faculty_id,))
            rows = cur.fetchall()
    finally:
        conn.close()
    timetable = {}
    for r in rows:
        timetable[(r['day_order'], r['slot_number'])] = {
            'subject': r['subject'], 'room': r.get('room', '')}
    return render_template('faculty_detail.html',
                           faculty=faculty, timetable=timetable,
                           time_slots=TIME_SLOTS, days=DAYS,
                           effective_status=get_faculty_status(faculty_id),
                           role=session.get('role'), current_day=get_day_order(), now=datetime.now())

# ── FACULTY ─────────────────────────────────────────────────────────────────────


@app.route('/faculty')
def faculty_dashboard():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty WHERE id=%s",
                        (session['user_id'],))
            faculty = cur.fetchone()
    finally:
        conn.close()
    return render_template('faculty_dashboard.html',
                           faculty=faculty, effective_status=get_faculty_status(
                               session['user_id']),
                           name=session.get('name'), now=datetime.now())


@app.route('/faculty/update_status')
def update_status():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    fid = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty WHERE id=%s", (fid,))
            faculty = cur.fetchone()
            cur.execute(
                "SELECT day_order, slot_number, subject FROM timetable WHERE faculty_id=%s", (fid,))
            slots = cur.fetchall()
    finally:
        conn.close()
    slot_map = {(s['day_order'], s['slot_number']): s['subject']
                for s in slots}
    return render_template('update_status.html',
                           faculty=faculty, effective_status=get_faculty_status(
                               fid),
                           time_slots=TIME_SLOTS, days=DAYS, slot_map=slot_map, now=datetime.now())


@app.route('/api/set_status', methods=['POST'])
def api_set_status():
    if session.get('role') != 'faculty':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    status = data.get('status')
    comment = data.get('comment', '')
    fid = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if status == 'On Leave':
                cur.execute(
                    "UPDATE faculty SET status='On Leave', manual_status='On Leave', leave_comment=%s WHERE id=%s", (comment, fid))
            elif status in ('Free', 'Busy'):
                cur.execute(
                    "UPDATE faculty SET status=%s, manual_status=%s, leave_comment='' WHERE id=%s", (status, status, fid))
            elif status == 'auto':
                cur.execute(
                    "UPDATE faculty SET manual_status='auto', leave_comment='' WHERE id=%s", (fid,))
                auto_status = get_timetable_status(fid)
                cur.execute(
                    "UPDATE faculty SET status=%s WHERE id=%s", (auto_status, fid))
        conn.commit()
    finally:
        conn.close()
    return jsonify({'success': True})


@app.route('/faculty/view_others')
def faculty_view_others():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM faculty WHERE id != %s ORDER BY name ASC", (session['user_id'],))
            faculties = cur.fetchall()
    finally:
        conn.close()
    for f in faculties:
        f['effective_status'] = get_faculty_status(f['id'])
    now = datetime.now()
    return render_template('student_dashboard.html',
                           faculties=faculties, now=now, day_order=get_day_order(),
                           role='faculty', name=session.get('name'), view_others=True)

# ── ADMIN ────────────────────────────────────────────────────────────────────────


@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty ORDER BY name ASC")
            faculties = cur.fetchall()
            cur.execute("SELECT COUNT(*) as cnt FROM students")
            student_count = cur.fetchone()['cnt']
    finally:
        conn.close()
    for f in faculties:
        f['effective_status'] = get_faculty_status(f['id'])
    return render_template('admin_dashboard.html',
                           faculties=faculties, student_count=student_count, name=session.get('name'), now=datetime.now())


@app.route('/admin/faculty/add', methods=['GET', 'POST'])
def add_faculty():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        pw = generate_password_hash(request.form['password'])
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO faculty (name, email, password, department, cabin, status, manual_status) VALUES (%s,%s,%s,%s,%s,'Free','auto')",
                            (request.form['name'], request.form['email'], pw, request.form['department'], request.form['cabin']))
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_faculty.html')


@app.route('/admin/faculty/edit/<int:fid>', methods=['GET', 'POST'])
def edit_faculty(fid):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        try:
            with conn.cursor() as cur:
                cur.execute("""UPDATE faculty SET name=%s, email=%s, department=%s,
                               dept_short=%s, designation=%s, cabin=%s WHERE id=%s""",
                            (request.form['name'], request.form['email'], request.form['department'],
                             request.form.get('dept_short', 'CSE'),
                             request.form.get(
                                 'designation', 'Assistant Professor'),
                             request.form['cabin'], fid))
                if request.form.get('password'):
                    cur.execute("UPDATE faculty SET password=%s WHERE id=%s",
                                (generate_password_hash(request.form['password']), fid))
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for('admin_dashboard'))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty WHERE id=%s", (fid,))
            faculty = cur.fetchone()
    finally:
        conn.close()
    return render_template('edit_faculty.html', faculty=faculty)


@app.route('/admin/faculty/delete/<int:fid>', methods=['POST'])
def delete_faculty(fid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM timetable WHERE faculty_id=%s", (fid,))
            cur.execute("DELETE FROM faculty WHERE id=%s", (fid,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({'success': True})


@app.route('/admin/timetable/<int:fid>', methods=['GET', 'POST'])
def manage_timetable(fid):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM faculty WHERE id=%s", (fid,))
            faculty = cur.fetchone()
            if request.method == 'POST':
                cur.execute(
                    "DELETE FROM timetable WHERE faculty_id=%s", (fid,))
                for day in range(1, 6):
                    for slot in range(1, 13):
                        subject = request.form.get(
                            f'slot_{day}_{slot}', '').strip()
                        room = request.form.get(
                            f'room_{day}_{slot}', '').strip()
                        if subject:
                            cur.execute("INSERT INTO timetable (faculty_id, day_order, slot_number, subject, room) VALUES (%s,%s,%s,%s,%s)",
                                        (fid, day, slot, subject, room))
                conn.commit()
                return redirect(url_for('admin_dashboard'))
            cur.execute("SELECT * FROM timetable WHERE faculty_id=%s", (fid,))
            rows = cur.fetchall()
    finally:
        conn.close()
    timetable = {(r['day_order'], r['slot_number']): {
        'subject': r['subject'], 'room': r.get('room', '')} for r in rows}
    return render_template('manage_timetable.html',
                           faculty=faculty, timetable=timetable, time_slots=TIME_SLOTS, days=DAYS)


if __name__ == '__main__':
    app.run(debug=True)
