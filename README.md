# Faculty Schedule Monitoring System

A Flask + MySQL web application for SRM IST to monitor faculty availability.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
> On Ubuntu/Linux: `pip install -r requirements.txt --break-system-packages`

### 2. Set Up MySQL Database
Make sure MySQL is running, then edit `setup_db.py` with your MySQL password and run:
```bash
python setup_db.py
```

### 3. Configure the App
Edit `app.py` and update the MySQL credentials:
```python
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
```

### 4. Run the App
```bash
python app.py
```
Visit: http://localhost:5000

---

## Login Credentials (after setup_db.py)

| Role    | Email                            | Password    |
|---------|----------------------------------|-------------|
| Admin   | admin@srm.edu.in                 | admin123    |
| Faculty | raman@srm.edu.in                 | faculty123  |
| Faculty | meera@srm.edu.in                 | faculty123  |
| Student | ra2311030010174@srm.edu.in       | student123  |

---

## Features

### Student View
- Browse faculty directory (alphabetical order)
- Search by name, department, or cabin
- Filter by status (Free / Busy / In Class / On Leave)
- View full weekly timetable for any faculty member

### Faculty View
- Update own status: Free / Busy / On Leave (with optional comment)
- Reset to automatic (timetable-based) status
- View own timetable
- Browse other faculty schedules

### Admin View
- Add / Edit / Delete faculty members
- Manage timetables (12 slots × 5 days per faculty)
- Live status overview with stats

## Status Priority Logic
1. **On Leave** (highest priority)
2. **Manual override** (Free/Busy set by faculty)
3. **Timetable-based automatic** (checks current time slot)

## Time Slots (as per SRM timetable)
| Slot | Time           |
|------|----------------|
| 1    | 08:00 – 08:50  |
| 2    | 08:50 – 09:40  |
| 3    | 09:45 – 10:35  |
| 4    | 10:40 – 11:30  |
| 5    | 11:35 – 12:25  |
| 6    | 12:30 – 01:20  |
| 7    | 01:25 – 02:15  |
| 8    | 02:20 – 03:10  |
| 9    | 03:10 – 04:00  |
| 10   | 04:00 – 04:50  |
| 11   | 04:50 – 05:30  |
| 12   | 05:30 – 06:10  |

## Tech Stack
- **Backend:** Flask (Python)
- **Database:** MySQL (via Flask-MySQLdb)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Icons:** Font Awesome 6
- **Fonts:** DM Sans (Google Fonts)
