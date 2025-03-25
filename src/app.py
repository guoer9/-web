from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
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

# 初始化CORS和SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 尝试连接MongoDB
try:
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/teacher_student_interaction")
    mongo = PyMongo(app)
    # 测试MongoDB连接
    mongo.db.command('ping')
    logger.info("MongoDB连接成功")
    db_available = True
except Exception as e:
    logger.error(f"MongoDB连接失败: {str(e)}")
    logger.warning("系统将以演示模式运行，数据库功能不可用")
    db_available = False
    
    # 创建模拟数据库对象
    class MockDB:
        def __init__(self):
            self.users = {}  # 用于存储用户数据的字典
        
        def find_one(self, query):
            if "username" in query and query["username"] in self.users:
                return self.users[query["username"]]
            return None
        
        def insert_one(self, data):
            if "username" in data:
                username = data["username"]
                self.users[username] = data
                from collections import namedtuple
                Result = namedtuple('Result', ['inserted_id'])
                return Result("mock_id_" + username)
    
    class MockMongo:
        def __init__(self):
            self.db = MockDB()
    
    mongo = MockMongo()

# 导入路由
from src.api.auth_routes import auth_bp
from src.api.interaction_routes import interaction_bp
from src.api.feedback_routes import feedback_bp
from src.controllers.web_controller import web_bp
from src.utils.socket_manager import SocketManager

# 初始化Socket管理器
socket_manager = SocketManager(socketio)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(interaction_bp, url_prefix='/api/interaction')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(web_bp, url_prefix='')

@app.route('/api')
def api_index():
    return jsonify({
        "message": "师生交互系统API服务运行中",
        "db_status": "已连接" if db_available else "未连接",
        "mode": "正常模式" if db_available else "演示模式"
    })

# 记录应用启动信息
@app.before_first_request
def before_first_request():
    logger.info("应用已启动，等待第一个请求")

if __name__ == "__main__":
    logger.info(f"应用启动中，使用DEBUG模式: {os.getenv('FLASK_DEBUG', 'False')}")
    socketio.run(app, debug=True)