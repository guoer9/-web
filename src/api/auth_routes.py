from flask import Blueprint, request, jsonify, session, current_app
from src.models.user import User
from functools import wraps
import jwt
from datetime import datetime, timedelta
import logging
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# 设置日志
logger = logging.getLogger(__name__)

# 验证JWT令牌装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'message': '缺少认证令牌'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            from src import mongo
            user_model = User(mongo)
            current_user = user_model.get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'message': '无效的认证令牌'}), 401
        except Exception as e:
            logger.error(f"Token验证失败: {str(e)}")
            return jsonify({'success': False, 'message': '无效的认证令牌'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# 验证用户是否是教师
def teacher_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'teacher':
            return jsonify({'success': False, 'message': '需要教师权限'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data or 'role' not in data:
            return jsonify({'success': False, 'message': '缺少必要的参数'}), 400
        
        if data['role'] not in ['student', 'teacher']:
            return jsonify({'success': False, 'message': '无效的用户角色'}), 400
        
        from src import mongo
        user_model = User(mongo)
        
        # 检查用户名是否已存在
        if user_model.get_user_by_username(data['username']):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 创建新用户
        user_data = {
            'username': data['username'],
            'password': generate_password_hash(data['password']),
            'role': data['role'],
            'name': data.get('name', data['username']),
            'created_at': datetime.utcnow()
        }
        
        # 如果是学生，添加班级信息
        if data['role'] == 'student' and 'class_id' in data:
            user_data['class_id'] = data['class_id']
        
        user_id = user_model.create_user(user_data)
        
        if user_id:
            logger.info(f"用户注册成功: {data['username']}")
            return jsonify({
                'success': True,
                'message': '注册成功',
                'user_id': str(user_id)
            })
        else:
            logger.error(f"用户注册失败: {data['username']}")
            return jsonify({'success': False, 'message': '注册失败'}), 500
            
    except Exception as e:
        logger.error(f"注册异常: {str(e)}")
        return jsonify({'success': False, 'message': '注册失败'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': '缺少必要的参数'}), 400
        
        from src import mongo
        user_model = User(mongo)
        user = user_model.get_user_by_username(data['username'])
        
        if not user or not check_password_hash(user['password'], data['password']):
            logger.warning(f"登录失败，用户名或密码错误: {data['username']}")
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 生成JWT令牌
        token = jwt.encode({
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(days=1)
        }, current_app.config['JWT_SECRET_KEY'])
        
        # 同时在会话中保存用户信息，用于模板渲染
        session['user'] = {
            'id': str(user['_id']),
            'username': user['username'],
            'name': user.get('name', user['username']),
            'role': user['role']
        }
        
        logger.info(f"用户登录成功: {user['username']}")
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'name': user.get('name', user['username']),
                'role': user['role']
            }
        })
        
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        return jsonify({'success': False, 'message': '登录失败'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """获取用户信息"""
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': str(current_user['_id']),
                'username': current_user['username'],
                'name': current_user.get('name', current_user['username']),
                'role': current_user['role'],
                'created_at': current_user['created_at'].isoformat()
            }
        })
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取用户信息失败'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """更新用户信息"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '缺少必要的参数'}), 400
        
        from src import mongo
        user_model = User(mongo)
        update_data = {}
        
        # 允许更新的字段
        allowed_fields = ['name', 'password']
        for field in allowed_fields:
            if field in data:
                if field == 'password':
                    update_data[field] = generate_password_hash(data[field])
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'success': False, 'message': '没有要更新的数据'}), 400
        
        if user_model.update_user(str(current_user['_id']), update_data):
            logger.info(f"用户信息更新成功: {current_user['username']}")
            return jsonify({'success': True, 'message': '更新成功'})
        else:
            logger.error(f"用户信息更新失败: {current_user['username']}")
            return jsonify({'success': False, 'message': '更新失败'}), 500
    except Exception as e:
        logger.error(f"更新用户信息异常: {str(e)}")
        return jsonify({'success': False, 'message': '更新失败'}), 500

@auth_bp.route('/users', methods=['GET'])
@token_required
@teacher_required
def get_users(current_user):
    """获取用户列表（仅教师可用）"""
    try:
        role = request.args.get('role')
        class_id = request.args.get('class_id')
        
        if not role:
            return jsonify({'success': False, 'message': '请指定用户角色'}), 400
        
        from src import mongo
        user_model = User(mongo)
        users = user_model.get_users_by_role(role, class_id)
        
        # 转换ObjectId为字符串
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        logger.error(f"获取用户列表异常: {str(e)}")
        return jsonify({'success': False, 'message': '获取用户列表失败'}), 500

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