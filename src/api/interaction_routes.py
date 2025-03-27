from flask import Blueprint, request, jsonify, session
from src.models.interaction import Interaction
from src.api.auth_routes import token_required, teacher_required
from bson.json_util import dumps, loads
import json
import logging

interaction_bp = Blueprint('interaction', __name__)

# 设置日志
logger = logging.getLogger(__name__)

# 从应用上下文获取模型
def get_interaction_model():
    from src.app import mongo
    return Interaction(mongo)

# 将MongoDB对象转换为JSON
def mongo_to_json(data):
    return json.loads(dumps(data))

#------------------------------------------------
# 问题相关接口
#------------------------------------------------

@interaction_bp.route('/student/questions', methods=['GET'])
@token_required
def get_student_questions(current_user):
    """获取学生提出的问题"""
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以查看自己的问题'}), 403
    
    student_id = str(current_user['_id'])
    questions = get_interaction_model().get_student_questions(student_id)
    
    return jsonify({
        'success': True, 
        'questions': mongo_to_json(questions)
    }), 200

@interaction_bp.route('/student/questions', methods=['POST'])
@token_required
def create_student_question(current_user):
    """学生创建新问题"""
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以提问'}), 403
    
    data = request.get_json()
    
    if not all(key in data for key in ['content']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    student_id = str(current_user['_id'])
    subject = data.get('subject')
    content = data['content']
    is_urgent = data.get('isUrgent', False)
    
    question_id = get_interaction_model().create_question(
        student_id,
        subject,
        content,
        is_urgent
    )
    
    if not question_id:
        return jsonify({'message': '创建问题失败'}), 500
    
    # 通知相关用户有新问题 (WebSocket暂未实现)
    # from src.app import socketio
    # socketio.emit('new_question', {'question_id': question_id})
    
    return jsonify({
        'success': True,
        'message': '问题提交成功',
        'questionId': question_id
    }), 201

@interaction_bp.route('/teacher/questions', methods=['GET'])
@token_required
@teacher_required
def get_teacher_pending_questions(current_user):
    """获取待回答的问题列表"""
    questions = get_interaction_model().get_pending_questions()
    
    return jsonify({
        'success': True, 
        'questions': mongo_to_json(questions)
    }), 200

@interaction_bp.route('/teacher/questions/answered', methods=['GET'])
@token_required
@teacher_required
def get_teacher_answered_questions(current_user):
    """获取已回答的问题列表"""
    questions = get_interaction_model().get_answered_questions()
    
    return jsonify({
        'success': True, 
        'questions': mongo_to_json(questions)
    }), 200

@interaction_bp.route('/teacher/questions/<question_id>/answer', methods=['POST'])
@token_required
@teacher_required
def answer_question(current_user, question_id):
    """教师回答问题"""
    data = request.get_json()
    
    if 'content' not in data:
        return jsonify({'message': '缺少回答内容'}), 400
    
    teacher_id = str(current_user['_id'])
    success = get_interaction_model().answer_question(
        question_id,
        teacher_id,
        data['content']
    )
    
    if not success:
        return jsonify({'message': '回答问题失败，可能问题不存在或已被回答'}), 400
    
    # 通知相关用户问题已回答 (WebSocket暂未实现)
    # from src.app import socketio
    # socketio.emit('question_answered', {'question_id': question_id})
    
    return jsonify({'success': True, 'message': '问题回答成功'}), 200

#------------------------------------------------
# 投票相关接口
#------------------------------------------------

@interaction_bp.route('/teacher/polls', methods=['POST'])
@token_required
@teacher_required
def create_poll(current_user):
    """教师创建投票"""
    data = request.get_json()
    
    if not all(key in data for key in ['title', 'options']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    if len(data['options']) < 2:
        return jsonify({'message': '投票选项不能少于2个'}), 400
    
    teacher_id = str(current_user['_id'])
    duration = int(data.get('duration', 0))
    
    poll_id = get_interaction_model().create_poll(
        teacher_id,
        data['title'],
        data['options'],
        duration
    )
    
    if not poll_id:
        return jsonify({'message': '创建投票失败'}), 500
    
    # 通知相关用户有新投票 (WebSocket暂未实现)
    # from src.app import socketio
    # socketio.emit('new_poll', {'poll_id': poll_id})
    
    return jsonify({
        'success': True,
        'message': '投票创建成功',
        'pollId': poll_id
    }), 201

@interaction_bp.route('/teacher/polls/active', methods=['GET'])
@token_required
@teacher_required
def get_active_polls(current_user):
    """获取活跃的投票"""
    polls = get_interaction_model().get_active_polls()
    
    return jsonify({
        'success': True, 
        'polls': mongo_to_json(polls)
    }), 200

@interaction_bp.route('/teacher/polls/ended', methods=['GET'])
@token_required
@teacher_required
def get_ended_polls(current_user):
    """获取已结束的投票"""
    polls = get_interaction_model().get_ended_polls()
    
    return jsonify({
        'success': True, 
        'polls': mongo_to_json(polls)
    }), 200

@interaction_bp.route('/teacher/polls/<poll_id>/end', methods=['POST'])
@token_required
@teacher_required
def end_poll(current_user, poll_id):
    """结束投票"""
    success = get_interaction_model().close_poll(poll_id)
    
    if not success:
        return jsonify({'message': '结束投票失败，可能投票不存在或已结束'}), 400
    
    return jsonify({'success': True, 'message': '投票已结束'}), 200

@interaction_bp.route('/student/polls/active', methods=['GET'])
@token_required
def get_student_active_polls(current_user):
    """获取学生可见的活跃投票"""
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以查看活跃投票'}), 403
    
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

@interaction_bp.route('/student/polls/<poll_id>/vote', methods=['POST'])
@token_required
def submit_vote(current_user, poll_id):
    """学生提交投票"""
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以参与投票'}), 403
    
    data = request.get_json()
    
    if 'optionId' not in data:
        return jsonify({'message': '缺少投票选项'}), 400
    
    student_id = str(current_user['_id'])
    option = data['optionId']
    
    success = get_interaction_model().vote_poll(poll_id, student_id, option)
    
    if not success:
        return jsonify({'message': '投票失败，可能投票已关闭或选项无效'}), 400
    
    # 获取更新后的投票信息
    updated_poll = get_interaction_model().get_interaction_by_id(poll_id)
    
    # 通知相关用户投票已更新 (WebSocket暂未实现)
    # from src.app import socketio
    # socketio.emit('poll_updated', {'poll_id': poll_id, 'votes': updated_poll['votes']})
    
    return jsonify({'success': True, 'message': '投票成功'}), 200

@interaction_bp.route('/interaction/<interaction_id>', methods=['GET'])
@token_required
def get_interaction(current_user, interaction_id):
    """获取互动详情"""
    interaction = get_interaction_model().get_interaction_by_id(interaction_id)
    
    if not interaction:
        return jsonify({'message': '互动不存在'}), 404
    
    return jsonify({
        'success': True, 
        'interaction': mongo_to_json(interaction)
    }), 200

@interaction_bp.route('/teacher/interaction/stats', methods=['GET'])
@token_required
@teacher_required
def get_interaction_stats(current_user):
    """获取互动统计数据"""
    interaction_model = get_interaction_model()
    
    # 获取待回答问题数量
    pending_questions = len(interaction_model.get_pending_questions())
    
    # 获取活跃投票数量
    active_polls = len(interaction_model.get_active_polls())
    
    # 获取紧急问题数量
    urgent_questions = len([q for q in interaction_model.get_pending_questions() if q.get('is_urgent', False)])
    
    return jsonify({
        'success': True,
        'stats': {
            'pending_questions': pending_questions,
            'active_polls': active_polls,
            'urgent_questions': urgent_questions
        }
    }), 200 