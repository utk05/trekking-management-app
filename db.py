import sqlite3
import os
from werkzeug.security import generate_password_hash
DB_NAME = "trekking.db"
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL)
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_approved BOOLEAN NOT NULL DEFAULT 0,
        is_blacklisted BOOLEAN NOT NULL DEFAULT 0

    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_blacklisted BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS treks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'moderate', 'hard')),
        duration INTEGER NOT NULL,
        available_slots INTEGER NOT NULL,
        assigned_staff_id INTEGER,
        status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        FOREIGN KEY (assigned_staff_id) REFERENCES staff(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        trek_id INTEGER NOT NULL,
        booking_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (trek_id) REFERENCES treks(id)
    )
    """)
    conn.commit()
    cur.close()
    conn.close()
def seed_admin():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin")
    if cur.fetchone() is None:
        hashed = generate_password_hash("choose a password")
        cur.execute(
            "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
            ("admin@trekapp.com", hashed)
        )
        conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_admin()
    print("Database initialized and admin seeded")
