from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
from services.auth_service import login_required

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/dashboard')
@login_required(role='staff')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    staff_id = session['staff_id']
    cur.execute("SELECT * FROM treks WHERE assigned_staff_id = ?", (staff_id,))
    assigned_treks = cur.fetchall()
    conn.close()
    return render_template('staff/dashboard.html', treks=assigned_treks)

@staff_bp.route('/treks/<int:trek_id>/update', methods=['GET', 'POST'])
@login_required(role='staff')
def update_trek(trek_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM treks WHERE id = ? AND assigned_staff_id = ?", (trek_id, session['staff_id']))
    trek = cur.fetchone()
    if trek is None:
        conn.close()
        return redirect(url_for('staff.dashboard'))  # not their trek — kick them back
    if request.method == 'POST':
        available_slots = request.form['available_slots']
        status = request.form['status']
        cur.execute("UPDATE treks SET available_slots = ?, status = ? WHERE id = ?",
                    (available_slots, status, trek_id))
        conn.commit()
        conn.close()
        return redirect(url_for('staff.dashboard'))
    conn.close()
    return render_template('staff/update_trek.html', trek=trek)

@staff_bp.route('/treks/<int:trek_id>/participants')
@login_required(role='staff')
def view_participants(trek_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM treks WHERE id = ? AND assigned_staff_id = ?", (trek_id, session['staff_id']))
    trek = cur.fetchone()
    if trek is None:
        conn.close()
        return redirect(url_for('staff.dashboard'))
    cur.execute("""
        SELECT bookings.*, users.name AS user_name, users.email AS user_email
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        WHERE bookings.trek_id = ?
    """, (trek_id,))
    participants = cur.fetchall()
    conn.close()
    return render_template('staff/participants.html', trek=trek, participants=participants)