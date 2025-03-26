from flask import Blueprint, request, jsonify, session, current_app
from src.models.user import User
from functools import wraps
import jwt
from datetime import datetime, timedelta
import logging

auth_bp = Blueprint('auth', __name__)

# 设置日志
logger = logging.getLogger(__name__)

# 从应用上下文获取mongo连接
def get_user_model():
    from src.app import mongo
    return User(mongo)

# 验证JWT令牌装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        
        try:
            # 解码令牌
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = get_user_model().get_user_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'message': '无效的令牌'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的令牌'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# 验证用户是否是教师
def teacher_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'teacher':
            return jsonify({'message': '需要教师权限'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(key in data for key in ['username', 'password', 'name', 'role']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 创建用户
    user_model = get_user_model()
    success, result = user_model.create_user(
        data['username'], 
        data['password'], 
        data['name'], 
        data['role'],
        data.get('class_id')
    )
    
    if not success:
        return jsonify({'message': result}), 400
    
    return jsonify({'message': '用户注册成功', 'user_id': result}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(key in data for key in ['username', 'password']):
        return jsonify({'message': '缺少用户名或密码'}), 400
    
    # 验证用户
    user_model = get_user_model()
    user = user_model.authenticate(data['username'], data['password'])
    
    if not user:
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 设置session
    session['user_id'] = str(user['_id'])
    session['role'] = user['role']
    session['username'] = user['username']
    
    logger.info(f"用户 {user['username']} 登录成功，角色: {user['role']}，会话: {session}")
    
    # 生成JWT令牌
    token = jwt.encode({
        'user_id': str(user['_id']),
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'username': user['username'],
            'role': user['role']
        }
    }), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    return jsonify({
        'id': str(current_user['_id']),
        'name': current_user['name'],
        'username': current_user['username'],
        'role': current_user['role']
    }), 200

@auth_bp.route('/users', methods=['GET'])
@token_required
@teacher_required
def get_users(current_user):
    role = request.args.get('role')
    class_id = request.args.get('class_id')
    
    if not role:
        return jsonify({'message': '请指定用户角色'}), 400
    
    users = get_user_model().get_users_by_role(role, class_id)
    
    # 转换ObjectId为字符串
    for user in users:
        user['_id'] = str(user['_id'])
    
    return jsonify(users), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # 清除会话
    user_id = session.get('user_id', '未知')
    username = session.get('username', '未知')
    role = session.get('role', '未知')
    logger.info(f"用户登出: ID={user_id}, 用户名={username}, 角色={role}")
    
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('username', None)
    
    return jsonify({'message': '登出成功'}), 200 