from functools import wraps
from flask import session, redirect, url_for

login_routes = {
    'admin': 'auth.login_admin',
    'staff': 'auth.login_staff',
    'user': 'auth.login_user'
}

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            session_key = f'{role}_id' if role else None
            if role and (session_key not in session or session.get('role') != role):
                return redirect(url_for(login_routes[role]))
            return f(*args, **kwargs)
        return wrapped
    return decorator