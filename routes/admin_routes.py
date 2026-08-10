from flask import Blueprint, render_template, request, redirect, url_for
from db import get_connection
from services.auth_service import login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required(role='admin')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM treks")
    total_treks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM staff")
    total_staff = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cur.fetchone()[0]
    conn.close()
    return render_template('admin/dashboard.html',
                            total_treks=total_treks,
                            total_users=total_users,
                            total_staff=total_staff,
                            total_bookings=total_bookings)

@admin_bp.route('/treks/new', methods=['GET', 'POST'])
@login_required(role='admin')
def create_trek():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        difficulty = request.form['difficulty']
        duration = request.form['duration']
        available_slots = request.form['available_slots']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO treks (name, location, difficulty, duration, available_slots, status, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, location, difficulty, duration, available_slots, 'Pending', start_date, end_date))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_trek.html')

@admin_bp.route('/treks')
@login_required(role='admin')
def list_treks():
    search = request.args.get('search', '')
    conn = get_connection()
    cur = conn.cursor()
    if search:
        cur.execute("SELECT * FROM treks WHERE name LIKE ? OR id = ?",
                    (f"%{search}%", search if search.isdigit() else -1))
    else:
        cur.execute("SELECT * FROM treks")
    treks = cur.fetchall()
    conn.close()
    return render_template('admin/treks.html', treks=treks, search=search)

@admin_bp.route('/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_trek(trek_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        difficulty = request.form['difficulty']
        duration = request.form['duration']
        available_slots = request.form['available_slots']
        status = request.form['status']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        assigned_staff_id = request.form.get('assigned_staff_id') or None

        cur.execute("""
            UPDATE treks SET name=?, location=?, difficulty=?, duration=?,
            available_slots=?, status=?, start_date=?, end_date=?, assigned_staff_id=?
            WHERE id=?
        """, (name, location, difficulty, duration, available_slots, status, start_date, end_date, assigned_staff_id, trek_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.list_treks'))

    cur.execute("SELECT * FROM treks WHERE id = ?", (trek_id,))
    trek = cur.fetchone()
    cur.execute("SELECT * FROM staff WHERE is_approved = 1 AND is_blacklisted = 0")
    eligible_staff = cur.fetchall()
    conn.close()
    return render_template('admin/edit_trek.html', trek=trek, eligible_staff=eligible_staff)

@admin_bp.route('/treks/<int:trek_id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_trek(trek_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM treks WHERE id = ?", (trek_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.list_treks'))

@admin_bp.route('/staff')
@login_required(role='admin')
def list_staff():
    search = request.args.get('search', '')
    conn = get_connection()
    cur = conn.cursor()
    if search:
        cur.execute("SELECT * FROM staff WHERE name LIKE ? OR id = ?",
                    (f"%{search}%", search if search.isdigit() else -1))
    else:
        cur.execute("SELECT * FROM staff")
    staff_list = cur.fetchall()
    conn.close()
    return render_template('admin/staff.html', staff_list=staff_list, search=search)

@admin_bp.route('/staff/<int:staff_id>/approve', methods=['POST'])
@login_required(role='admin')
def approve_staff(staff_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE staff SET is_approved = 1 WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.list_staff'))

@admin_bp.route('/staff/<int:staff_id>/blacklist', methods=['POST'])
@login_required(role='admin')
def blacklist_staff(staff_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE staff SET is_blacklisted = 1 WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.list_staff'))

@admin_bp.route('/users')
@login_required(role='admin')
def list_users():
    search = request.args.get('search', '')
    conn = get_connection()
    cur = conn.cursor()
    if search:
        cur.execute("SELECT * FROM users WHERE name LIKE ? OR id = ?",
                    (f"%{search}%", search if search.isdigit() else -1))
    else:
        cur.execute("SELECT * FROM users")
    users_list = cur.fetchall()
    conn.close()
    return render_template('admin/users.html', users_list=users_list, search=search)

@admin_bp.route('/users/<int:user_id>/blacklist', methods=['POST'])
@login_required(role='admin')
def blacklist_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_blacklisted = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/bookings')
@login_required(role='admin')
def list_bookings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT bookings.*, users.name AS user_name, treks.name AS trek_name
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        JOIN treks ON bookings.trek_id = treks.id
    """)
    bookings = cur.fetchall()
    conn.close()
    return render_template('admin/bookings.html', bookings=bookings)