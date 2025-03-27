from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
import os

from .config import config

# 初始化扩展
mongo = PyMongo()
cache = Cache()

def create_app(config_name='default'):
    """创建Flask应用实例"""
    # 指定正确的模板和静态文件目录
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    mongo.init_app(app)
    CORS(app)
    cache.init_app(app)
    
    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('应用启动')
    
    # 注册蓝图
    from .api.auth_routes import auth_bp
    from .api.teacher_routes import teacher_bp
    from .api.student_routes import student_bp
    from .routes import routes_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(routes_bp)
    
    # 注册错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return {'success': False, 'message': '未找到请求的资源'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'message': '服务器内部错误'}, 500
    
    # 确保MongoDB连接可用
    with app.app_context():
        try:
            mongo.db.command('ping')
            app.logger.info('MongoDB连接成功')
        except Exception as e:
            app.logger.error(f'MongoDB连接失败: {str(e)}')
            raise
    
    return app 