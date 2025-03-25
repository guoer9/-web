from flask import render_template, redirect, url_for, request, session, Blueprint, jsonify
from functools import wraps
import jwt
import logging
import os
import json

web_bp = Blueprint('web', __name__)

# 设置日志
logger = logging.getLogger(__name__)

# 验证用户是否已登录
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function

# 验证用户是否是教师
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'teacher':
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function

# 验证用户是否是学生
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'student':
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function

@web_bp.route('/')
def index():
    """显示主页"""
    return render_template('index.html')

@web_bp.route('/status')
def status():
    """返回API状态"""
    mode = "演示模式" if os.environ.get('FLASK_ENV') == 'development' else "生产模式"
    return jsonify({
        "status": "运行中",
        "mode": mode,
        "version": "0.1.0"
    })

@web_bp.route('/student/dashboard')
def student_dashboard():
    """显示学生仪表板"""
    logger.info("访问学生仪表板")
    return render_template('student/dashboard.html')

@web_bp.route('/teacher/dashboard')
def teacher_dashboard():
    """显示教师仪表板"""
    logger.info("访问教师仪表板")
    return render_template('teacher/dashboard.html') 