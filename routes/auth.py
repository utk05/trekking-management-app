from flask import Blueprint, render_template, request, session, redirect, url_for
from db import get_connection
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        if user is None or not check_password_hash(user['password_hash'], password):
            return render_template('auth/login_user.html', error="Invalid email or password")
        elif user['is_blacklisted'] == 1:
            return render_template('auth/login_user.html', error="Your account has been blacklisted")
        else:
            session['user_id'] = user['id']
            session['role'] = 'user'
            return redirect(url_for('user.dashboard'))
    return render_template('auth/login_user.html')


@auth_bp.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cur = conn.cursor()
        existing_user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            conn.close()
            return render_template('auth/register.html', error="Email already registered")
        password_hash = generate_password_hash(password)
        conn.execute("INSERT INTO users (name, email, password_hash, is_blacklisted) VALUES (?, ?, ?, 0)", (name, email, password_hash))
        conn.commit()
        conn.close()
        return redirect(url_for('auth.login_user'))
    return render_template('auth/register.html')


@auth_bp.route('/register/staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        existing_staff = conn.execute("SELECT * FROM staff WHERE email = ?", (email,)).fetchone()
        if existing_staff:
            conn.close()
            return render_template('auth/register_staff.html', error="Email already registered")
        password_hash = generate_password_hash(password)
        conn.execute("INSERT INTO staff (name, email, password_hash, is_approved, is_blacklisted) VALUES (?, ?, ?, 0, 0)", (name, email, password_hash))
        conn.commit()
        conn.close()
        return redirect(url_for('auth.login_user'))
    return render_template('auth/register_staff.html')


@auth_bp.route('/login/staff', methods=['GET', 'POST'])
def login_staff():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM staff WHERE email = ?", (email,))
        staff = cur.fetchone()
        conn.close()
        if staff is None or not check_password_hash(staff['password_hash'], password):
            return render_template('auth/login_staff.html', error="Invalid email or password")
        elif staff['is_blacklisted'] == 1:
            return render_template('auth/login_staff.html', error="Your account has been blacklisted")
        elif staff['is_approved'] == 0:
            return render_template('auth/login_staff.html', error="Your registration is pending admin approval")
        else:
            session['staff_id'] = staff['id']
            session['role'] = 'staff'
            return redirect(url_for('staff.dashboard'))
    return render_template('auth/login_staff.html')


@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_connection()
        admin = conn.execute("SELECT * FROM admin WHERE email = ?", (email,)).fetchone()
        conn.close()
        if admin is None or not check_password_hash(admin['password_hash'], password):
            return render_template('auth/login_admin.html', error='Invalid email or password')
        session['admin_id'] = admin['id']
        session['role'] = 'admin'
        return redirect(url_for('admin.dashboard'))
    return render_template('auth/login_admin.html')