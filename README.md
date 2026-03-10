# Faculty Schedule Viewing System

A web-based application that allows students and staff to view real-time faculty availability based on timetable data.

Developed for SRM IST, the system provides an easy way to check whether a faculty member is **Free, Busy, In Class, or On Leave**, helping students find available faculty without unnecessary waiting.

---

# Features

## Student Portal
- Browse faculty directory
- Search by name, department, or cabin
- View faculty availability status
- Check complete weekly timetable

## Faculty Portal
- Update status (Free / Busy / On Leave)
- Optional status comments
- Reset status to automatic timetable mode
- View personal timetable
- Browse other faculty schedules

## Admin Portal
- Add / Edit / Delete faculty members
- Manage faculty timetables
- Monitor live availability statistics
- Administrative control panel

---

# Status Priority Logic

Faculty availability is determined using the following priority:

1. **On Leave** (highest priority)
2. **Manual override** set by faculty
3. **Automatic timetable status**

This ensures manual updates always override the timetable.

---

# Technology Stack

Backend:
- Python (Flask)

Database:
- MySQL (Flask-MySQLdb)

Frontend:
- HTML5
- CSS3
- JavaScript

UI Resources:
- Font Awesome
- Google Fonts (DM Sans)

---