from flask import Blueprint, jsonify, request, current_app
from bson import ObjectId
from datetime import datetime
from functools import wraps
import jwt
import json

from ..models.interaction import Interaction
from ..models.user import User

teacher_bp = Blueprint('teacher', __name__)

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
            if not current_user or current_user.get('role') != 'teacher':
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

# 投票相关API
@teacher_bp.route('/polls', methods=['POST'])
@token_required
def create_poll(current_user):
    """创建新投票"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'title' not in data or 'options' not in data:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    title = data.get('title')
    options = data.get('options')
    duration = data.get('duration', 0)
    
    # 校验选项
    if not isinstance(options, list) or len(options) < 2:
        return jsonify({'success': False, 'message': '投票选项至少需要两个'}), 400
    
    # 创建投票
    try:
        teacher_id = str(current_user['_id'])
        teacher_name = current_user.get('name', current_user.get('username', '教师'))
        
        poll_id = get_interaction_model().create_poll(
            teacher_id=teacher_id,
            teacher_name=teacher_name,
            title=title,
            options=options,
            duration=duration
        )
        
        if poll_id:
            return jsonify({
                'success': True,
                'message': '投票创建成功',
                'poll_id': poll_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '投票创建失败'
            }), 500
    except Exception as e:
        current_app.logger.error(f"创建投票失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@teacher_bp.route('/polls/active', methods=['GET'])
@token_required
def get_active_polls(current_user):
    """获取活跃投票列表"""
    try:
        polls = get_interaction_model().get_active_polls()
        
        return jsonify({
            'success': True,
            'polls': mongo_to_json(polls)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取活跃投票失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@teacher_bp.route('/polls/ended', methods=['GET'])
@token_required
def get_ended_polls(current_user):
    """获取已结束投票列表"""
    try:
        polls = get_interaction_model().get_ended_polls()
        
        return jsonify({
            'success': True,
            'polls': mongo_to_json(polls)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取已结束投票失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@teacher_bp.route('/polls/<poll_id>/end', methods=['POST'])
@token_required
def end_poll(current_user, poll_id):
    """结束投票"""
    try:
        result = get_interaction_model().end_poll(poll_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': '投票已成功结束'
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': '结束投票失败，投票可能不存在或已结束'
            }), 400
    except Exception as e:
        current_app.logger.error(f"结束投票失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

# 问题相关API
@teacher_bp.route('/questions', methods=['GET'])
@token_required
def get_pending_questions(current_user):
    """获取待回答的问题列表"""
    try:
        questions = get_interaction_model().get_pending_questions()
        
        return jsonify({
            'success': True,
            'questions': mongo_to_json(questions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取待回答问题失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@teacher_bp.route('/questions/answered', methods=['GET'])
@token_required
def get_answered_questions(current_user):
    """获取已回答的问题列表"""
    try:
        questions = get_interaction_model().get_answered_questions()
        
        return jsonify({
            'success': True,
            'questions': mongo_to_json(questions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取已回答问题失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@teacher_bp.route('/questions/<question_id>/answer', methods=['POST'])
@token_required
def answer_question(current_user, question_id):
    """回答问题"""
    data = request.get_json()
    
    # 验证请求数据
    if not data or 'content' not in data:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    content = data.get('content')
    
    # 回答问题
    try:
        teacher_id = str(current_user['_id'])
        teacher_name = current_user.get('name', current_user.get('username', '教师'))
        
        result = get_interaction_model().answer_question(
            question_id=question_id,
            teacher_id=teacher_id,
            teacher_name=teacher_name,
            content=content
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': '问题已成功回答'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '回答问题失败，问题可能不存在或已被回答'
            }), 400
    except Exception as e:
        current_app.logger.error(f"回答问题失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@teacher_bp.route('/interaction/stats', methods=['GET'])
@token_required
def get_interaction_stats(current_user):
    """获取互动统计数据"""
    try:
        interaction_model = get_interaction_model()
        
        # 获取待回答问题数量
        pending_questions = interaction_model.count_pending_questions()
        
        # 获取活跃投票数量
        active_polls = interaction_model.count_active_polls()
        
        # 获取紧急问题数量
        urgent_questions = interaction_model.count_urgent_questions()
        
        return jsonify({
            'success': True,
            'stats': {
                'pending_questions': pending_questions,
                'active_polls': active_polls,
                'urgent_questions': urgent_questions
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取互动统计数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500 