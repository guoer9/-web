from flask import Blueprint, jsonify, request, current_app
from bson import ObjectId
from datetime import datetime
from functools import wraps
import jwt
import json

from ..models.interaction import Interaction
from ..models.user import User

student_bp = Blueprint('student', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User(current_app.mongo).get_user_by_id(data['user_id'])
            if not current_user or current_user.get('role') != 'student':
                return jsonify({'message': '无效的认证令牌'}), 401
        except:
            return jsonify({'message': '无效的认证令牌'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# 辅助函数，将MongoDB对象转换为JSON
def mongo_to_json(data):
    return json.loads(json.dumps(data, default=str))

# 获取互动模型实例
def get_interaction_model():
    return Interaction(current_app.mongo)

# 问题相关API
@student_bp.route('/questions', methods=['GET'])
@token_required
def get_my_questions(current_user):
    """获取学生的问题列表"""
    try:
        student_id = str(current_user['_id'])
        questions = get_interaction_model().get_student_questions(student_id)
        
        return jsonify({
            'success': True,
            'questions': mongo_to_json(questions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取问题列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@student_bp.route('/questions', methods=['POST'])
@token_required
def create_question(current_user):
    """创建新问题"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'content' not in data:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    content = data.get('content')
    subject = data.get('subject', '')
    is_urgent = data.get('is_urgent', False)
    
    # 创建问题
    try:
        student_id = str(current_user['_id'])
        
        question_id = get_interaction_model().create_question(
            student_id=student_id,
            subject=subject,
            content=content,
            is_urgent=is_urgent
        )
        
        if question_id:
            return jsonify({
                'success': True,
                'message': '问题提交成功',
                'question_id': question_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '问题提交失败'
            }), 500
    except Exception as e:
        current_app.logger.error(f"创建问题失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

# 投票相关API
@student_bp.route('/polls/active', methods=['GET'])
@token_required
def get_active_polls(current_user):
    """获取活跃投票列表"""
    try:
        # 获取活跃投票
        polls = get_interaction_model().get_active_polls()
        
        # 获取学生已投票的信息
        student_id = str(current_user['_id'])
        student_votes = get_interaction_model().get_student_poll_votes(student_id)
        
        # 映射投票ID到学生选择
        vote_map = {vote['poll_id']: vote['option'] for vote in student_votes}
        
        # 为每个投票添加学生选择信息
        polls_json = mongo_to_json(polls)
        for poll in polls_json:
            poll_id = str(poll['_id'])
            if poll_id in vote_map:
                poll['student_vote'] = vote_map[poll_id]
            else:
                poll['student_vote'] = None
        
        return jsonify({
            'success': True,
            'polls': polls_json
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取活跃投票失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@student_bp.route('/polls/<poll_id>/vote', methods=['POST'])
@token_required
def vote_poll(current_user, poll_id):
    """提交投票"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'option' not in data:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    option = data.get('option')
    
    # 提交投票
    try:
        student_id = str(current_user['_id'])
        
        result = get_interaction_model().vote_poll(
            poll_id=poll_id,
            student_id=student_id,
            option=option
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': '投票提交成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '投票提交失败，可能已经投过票或投票已结束'
            }), 400
    except Exception as e:
        current_app.logger.error(f"提交投票失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500 