from flask import Flask, jsonify, request, abort
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import sys
import logging
import requests
import traceback
import threading

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__, 
            static_folder="../static",
            template_folder="../templates")

# 应用配置
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
app.config["ADMIN_TOKEN"] = os.getenv("ADMIN_TOKEN", "admin_secret_token")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

# 大模型API配置
app.config["AI_API_KEY"] = os.getenv("AI_API_KEY")
app.config["AI_API_URL"] = os.getenv("AI_API_URL", "https://api.openai.com/v1/chat/completions")
app.config["AI_MODEL"] = os.getenv("AI_MODEL", "gpt-3.5-turbo")

# 确保上传目录存在
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# 初始化CORS和SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 连接MongoDB
try:
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/teacher_student_interaction")
    mongo = PyMongo(app)
    # 测试MongoDB连接
    mongo.db.command('ping')
    app.mongo_client = mongo.db.client  # 添加客户端引用
    logger.info("MongoDB连接成功")
except Exception as e:
    error_msg = f"MongoDB连接失败: {str(e)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    # 系统依赖MongoDB，连接失败直接中止启动
    raise RuntimeError("MongoDB连接失败，系统无法启动。请检查配置并确保MongoDB服务运行正常。") from e

# 测试大模型API连接
def test_ai_api():
    if not app.config["AI_API_KEY"]:
        logger.warning("未配置AI_API_KEY，大模型分析功能将不可用")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {app.config['AI_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": app.config["AI_MODEL"],
            "messages": [{"role": "system", "content": "测试连接"}],
            "max_tokens": 10
        }
        
        response = requests.post(app.config["AI_API_URL"], headers=headers, json=data, timeout=5)
        
        if response.status_code == 200:
            logger.info("大模型API连接成功")
            return True
        else:
            logger.warning(f"大模型API连接测试失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.warning(f"大模型API连接测试失败: {str(e)}")
        return False

# 测试大模型API连接
app.config["AI_API_AVAILABLE"] = test_ai_api()

# 导入路由
from src.api.auth_routes import auth_bp
from src.api.interaction_routes import interaction_bp
from src.api.feedback_routes import feedback_bp
from src.api.analytics_routes import analytics_bp
from src.api.resource_routes import resource_bp
from src.api.news_routes import news_bp
from src.controllers.web_controller import web_bp
from src.utils.socket_manager import SocketManager
from src.services.news_service import news_service  # 导入新闻服务实例

# 初始化Socket管理器
socket_manager = SocketManager(socketio)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(interaction_bp, url_prefix='/api/interaction')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(resource_bp, url_prefix='/api/resources')
app.register_blueprint(news_bp, url_prefix='/api/news')
app.register_blueprint(web_bp, url_prefix='')

# 启动新闻自动更新服务
def start_news_service():
    try:
        with app.app_context():
            from src.services.news_service import news_service
            logger.info("启动新闻自动更新服务")
            # 先尝试更新一次
            news_service.update_news()
            # 然后设置定时更新
            news_service.schedule_update(interval=3600)  # 每小时更新一次
    except Exception as e:
        logger.error(f"启动新闻自动更新服务失败: {str(e)}\n{traceback.format_exc()}")

# 应用启动后启动新闻服务和测试AI API
@app.before_first_request
def before_first_request():
    logger.info("应用已启动，等待第一个请求")
    # 使用线程避免阻塞第一个请求
    threading.Timer(5.0, start_news_service).start()
    # 测试AI API连接
    threading.Timer(3.0, test_ai_api).start()

@app.route('/api')
def api_index():
    return jsonify({
        "message": "师生交互系统API服务运行中",
        "db_status": "已连接",
        "ai_status": "已连接" if app.config["AI_API_AVAILABLE"] else "未连接或未配置"
    })

# 通用错误处理
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "请求参数错误", "details": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "请求的资源不存在", "details": str(error)}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"服务器内部错误: {str(error)}\n{traceback.format_exc()}")
    return jsonify({"error": "服务器内部错误", "details": str(error)}), 500

if __name__ == "__main__":
    logger.info(f"应用启动中，使用DEBUG模式: {os.getenv('FLASK_DEBUG', 'False')}")
    socketio.run(app, debug=True)