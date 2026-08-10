# Trekking Management App

A role-based web application for managing trek creation, staff assignment,
and bookings — built for the IITM BS App Dev I course project (May 2026 term).

## Roles
- **Admin** — pre-seeded, manages treks, staff approval, and users
- **Trek Staff** — self-registers (requires admin approval), manages assigned treks
- **User (Trekker)** — self-registers, browses and books treks

## Tech Stack
Flask, Jinja2, Bootstrap, SQLite (raw sqlite3, no ORM)

## Setup

1. Clone/extract this folder and navigate into it:
   cd code

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Initialize the database:
   python db.py
   <<describe what this does — creates tables, seeds the admin row, etc.
     Adjust this step if your DB setup works differently>>

5. Run the app:
   python app.py

6. Open in browser:
   http://127.0.0.1:5000

## Default Admin Login
- Email: <<your seeded admin email>>
- Password: <<your seeded admin password>>

## Notes
- No REST API is exposed — all routes are server-rendered Jinja2 views.
- Passwords are hashed using Werkzeug's generate_password_hash.