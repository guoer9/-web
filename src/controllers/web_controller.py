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
        logger.info(f"访问需要教师权限的路由，会话内容: {session}")
        if 'role' not in session:
            logger.warning("会话中不存在'role'键")
            return redirect(url_for('web.index'))
        if session['role'] != 'teacher':
            logger.warning(f"用户角色不是教师，而是: {session['role']}")
            return redirect(url_for('web.index'))
        logger.info("教师权限验证通过")
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
@teacher_required
def teacher_dashboard():
    """显示教师仪表板"""
    logger.info("访问教师仪表板")
    return render_template('teacher/dashboard.html')

@web_bp.route('/teacher/news')
@teacher_required
def teacher_news():
    """显示教师新闻页面"""
    logger.info("访问教师新闻页面")
    return render_template('teacher/news_dashboard.html')

@web_bp.route('/student/news')
@login_required
def student_news():
    """显示学生新闻页面"""
    logger.info("访问学生新闻页面")
    return render_template('student/news_dashboard.html')

@web_bp.route('/teacher/resources')
@teacher_required
def teacher_resources():
    """显示教师资源管理页面"""
    logger.info("访问教师资源管理页面")
    return render_template('teacher/resources.html')

@web_bp.route('/student/resources')
def student_resources():
    """显示学生资源页面"""
    logger.info("访问学生资源页面")
    return render_template('student/resources.html')

@web_bp.route('/teacher/analytics')
@teacher_required
def teacher_analytics():
    """显示教师分析页面"""
    logger.info("访问教师分析页面")
    return render_template('teacher/analytics_dashboard.html')

# 新增路由 - 互动管理
@web_bp.route('/teacher/interactions')
@teacher_required
def teacher_interactions():
    """显示教师互动管理页面"""
    logger.info("访问教师互动管理页面")
    return render_template('teacher/interactions.html')

@web_bp.route('/student/interactions')
def student_interactions():
    """显示学生互动页面"""
    logger.info("访问学生互动页面")
    return render_template('student/interactions.html')

# 新增路由 - 反馈处理
@web_bp.route('/teacher/feedback')
@teacher_required
def teacher_feedback():
    """显示教师反馈管理页面"""
    logger.info("访问教师反馈管理页面")
    return render_template('teacher/feedback.html')

@web_bp.route('/student/feedback')
def student_feedback():
    """显示学生反馈页面"""
    logger.info("访问学生反馈页面")
    return render_template('student/feedback.html')

# 新增路由 - 数据分析
@web_bp.route('/student/analytics')
def student_analytics():
    """显示学生数据分析页面"""
    logger.info("访问学生数据分析页面")
    return render_template('student/analytics.html')

# 新增路由 - 个人资料
@web_bp.route('/teacher/profile')
@teacher_required
def teacher_profile():
    """显示教师个人资料页面"""
    logger.info("访问教师个人资料页面")
    return render_template('teacher/profile.html')

@web_bp.route('/student/profile')
def student_profile():
    """显示学生个人资料页面"""
    logger.info("访问学生个人资料页面")
    return render_template('student/profile.html')

# 新增路由 - 通知设置
@web_bp.route('/teacher/notifications')
@teacher_required
def teacher_notifications():
    """显示教师通知设置页面"""
    logger.info("访问教师通知设置页面")
    return render_template('teacher/notifications.html')

@web_bp.route('/student/notifications')
def student_notifications():
    """显示学生通知设置页面"""
    logger.info("访问学生通知设置页面")
    return render_template('student/notifications.html')

# 新增路由 - 学生名单
@web_bp.route('/teacher/students')
@teacher_required
def teacher_students():
    """显示教师查看学生名单页面"""
    logger.info("访问教师查看学生名单页面")
    return render_template('teacher/students.html')

# 新增路由 - 课堂讨论
@web_bp.route('/teacher/discussions')
@teacher_required
def teacher_discussions():
    """显示教师讨论管理页面"""
    logger.info("访问教师讨论管理页面")
    return render_template('teacher/discussions.html')

@web_bp.route('/student/discussions')
def student_discussions():
    """显示学生课堂讨论页面"""
    logger.info("访问学生课堂讨论页面")
    return render_template('student/discussions.html')

# 测验管理路由
@web_bp.route('/teacher/quizzes')
@teacher_required
def teacher_quizzes():
    """显示教师测验管理页面"""
    logger.info("访问教师测验管理页面")
    return render_template('teacher/quizzes.html')

@web_bp.route('/student/quizzes')
def student_quizzes():
    """显示学生测验页面"""
    logger.info("访问学生测验页面")
    return render_template('student/quizzes.html')

# 错误处理页面
@web_bp.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@web_bp.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500 