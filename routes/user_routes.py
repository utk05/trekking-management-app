from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
from services.auth_service import login_required
from datetime import date

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required(role='user')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM treks WHERE status = 'Open'")
    open_treks = cur.fetchall()
    conn.close()
    return render_template('user/dashboard.html', treks=open_treks)

@user_bp.route('/treks/<int:trek_id>/book', methods=['GET', 'POST'])
@login_required(role='user')
def book_trek(trek_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM treks WHERE id = ?", (trek_id,))
    trek = cur.fetchone()

    if trek is None:
        conn.close()
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        if trek['status']!= 'Open':
            conn.close()
            return redirect(url_for('user.dashboard'))

        if trek['available_slots']<= 0:
            conn.close()
            return redirect(url_for('user.dashboard'))  
        cur.execute("INSERT INTO bookings (user_id, trek_id, booking_date, status) VALUES (?, ?, ?, 'Booked')",
                    (session['user_id'], trek_id, date.today()))    
        cur.execute("UPDATE treks SET available_slots = available_slots - 1 WHERE id = ?", (trek_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('user.dashboard'))

    conn.close()
    return render_template('user/book_trek.html', trek=trek)

@user_bp.route('/bookings')
@login_required(role='user')
def my_bookings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT bookings.*, treks.name AS trek_name, treks.location, treks.start_date, treks.end_date
        FROM bookings
        JOIN treks ON bookings.trek_id = treks.id
        WHERE bookings.user_id = ?
    """, (session['user_id'],))
    bookings = cur.fetchall()
    conn.close()
    return render_template('user/bookings.html', bookings=bookings)

@user_bp.route('/dashboard')
@login_required(role='user')
def dashboard():
    difficulty = request.args.get('difficulty')
    location = request.args.get('location')

    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM treks WHERE status = 'Open'"
    params = []

    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    cur.execute(query, params)
    open_treks = cur.fetchall()
    conn.close()
    return render_template('user/dashboard.html', treks=open_treks, difficulty=difficulty, location=location)