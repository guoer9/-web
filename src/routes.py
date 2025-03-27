from flask import Blueprint, render_template, redirect, url_for, request, session
from functools import wraps

routes_bp = Blueprint('routes', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function

@routes_bp.route('/')
def index():
    return redirect(url_for('routes.login'))

@routes_bp.route('/login')
def login():
    return render_template('login.html')

@routes_bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if session.get('user', {}).get('role') != 'teacher':
        return redirect(url_for('routes.login'))
    return render_template('teacher/dashboard.html')

@routes_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    if session.get('user', {}).get('role') != 'student':
        return redirect(url_for('routes.login'))
    return render_template('student/dashboard.html') 