from flask import Blueprint, request, jsonify
from src.models.interaction import Interaction
from src.api.auth_routes import token_required, teacher_required
from bson.json_util import dumps, loads
import json

interaction_bp = Blueprint('interaction', __name__)

# 从应用上下文获取模型
def get_interaction_model():
    from src.app import mongo
    return Interaction(mongo)

# 将MongoDB对象转换为JSON
def mongo_to_json(data):
    return json.loads(dumps(data))

@interaction_bp.route('/question', methods=['POST'])
@token_required
def create_question(current_user):
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以提问'}), 403
    
    data = request.get_json()
    
    if not all(key in data for key in ['class_id', 'content']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    question_id = get_interaction_model().create_question(
        str(current_user['_id']),
        data['class_id'],
        data['content']
    )
    
    # 通知相关用户有新问题
    from src.app import socketio
    socketio.emit('new_question', {
        'question_id': question_id,
        'class_id': data['class_id']
    }, room=data['class_id'])
    
    return jsonify({
        'message': '问题提交成功',
        'question_id': question_id
    }), 201

@interaction_bp.route('/question/<question_id>/answer', methods=['POST'])
@token_required
@teacher_required
def answer_question(current_user, question_id):
    data = request.get_json()
    
    if 'answer' not in data:
        return jsonify({'message': '缺少回答内容'}), 400
    
    success = get_interaction_model().answer_question(
        question_id,
        str(current_user['_id']),
        data['answer']
    )
    
    if not success:
        return jsonify({'message': '回答问题失败'}), 400
    
    # 获取问题详情以便在通知中使用
    question = get_interaction_model().get_interaction_by_id(question_id)
    
    # 通知相关用户问题已回答
    from src.app import socketio
    socketio.emit('question_answered', {
        'question_id': question_id,
        'class_id': question['class_id']
    }, room=question['class_id'])
    
    return jsonify({'message': '问题回答成功'}), 200

@interaction_bp.route('/poll', methods=['POST'])
@token_required
@teacher_required
def create_poll(current_user):
    data = request.get_json()
    
    if not all(key in data for key in ['class_id', 'title', 'options']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    if len(data['options']) < 2:
        return jsonify({'message': '投票选项不能少于2个'}), 400
    
    poll_id = get_interaction_model().create_poll(
        str(current_user['_id']),
        data['class_id'],
        data['title'],
        data['options']
    )
    
    # 通知相关用户有新投票
    from src.app import socketio
    socketio.emit('new_poll', {
        'poll_id': poll_id,
        'class_id': data['class_id']
    }, room=data['class_id'])
    
    return jsonify({
        'message': '投票创建成功',
        'poll_id': poll_id
    }), 201

@interaction_bp.route('/poll/<poll_id>/vote', methods=['POST'])
@token_required
def vote_poll(current_user, poll_id):
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以参与投票'}), 403
    
    data = request.get_json()
    
    if 'option' not in data:
        return jsonify({'message': '缺少投票选项'}), 400
    
    # 获取投票信息
    poll = get_interaction_model().get_interaction_by_id(poll_id)
    if not poll:
        return jsonify({'message': '投票不存在'}), 404
    
    if poll['status'] != 'active':
        return jsonify({'message': '投票已关闭'}), 400
    
    if data['option'] not in poll['options']:
        return jsonify({'message': '无效的投票选项'}), 400
    
    success = get_interaction_model().vote_poll(
        poll_id,
        str(current_user['_id']),
        data['option']
    )
    
    if not success:
        return jsonify({'message': '投票失败'}), 400
    
    # 获取更新后的投票信息
    updated_poll = get_interaction_model().get_interaction_by_id(poll_id)
    
    # 通知相关用户投票已更新
    from src.app import socketio
    socketio.emit('poll_updated', {
        'poll_id': poll_id,
        'votes': updated_poll['votes'],
        'class_id': poll['class_id']
    }, room=poll['class_id'])
    
    return jsonify({'message': '投票成功'}), 200

@interaction_bp.route('/discussion', methods=['POST'])
@token_required
@teacher_required
def create_discussion(current_user):
    data = request.get_json()
    
    if not all(key in data for key in ['class_id', 'title', 'description']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    discussion_id = get_interaction_model().create_discussion(
        str(current_user['_id']),
        data['class_id'],
        data['title'],
        data['description']
    )
    
    # 通知相关用户有新讨论
    from src.app import socketio
    socketio.emit('new_discussion', {
        'discussion_id': discussion_id,
        'class_id': data['class_id']
    }, room=data['class_id'])
    
    return jsonify({
        'message': '讨论创建成功',
        'discussion_id': discussion_id
    }), 201

@interaction_bp.route('/discussion/<discussion_id>/message', methods=['POST'])
@token_required
def add_discussion_message(current_user, discussion_id):
    data = request.get_json()
    
    if 'content' not in data:
        return jsonify({'message': '缺少消息内容'}), 400
    
    # 获取讨论信息
    discussion = get_interaction_model().get_interaction_by_id(discussion_id)
    if not discussion:
        return jsonify({'message': '讨论不存在'}), 404
    
    if discussion['status'] != 'active':
        return jsonify({'message': '讨论已关闭'}), 400
    
    success = get_interaction_model().add_discussion_message(
        discussion_id,
        str(current_user['_id']),
        data['content']
    )
    
    if not success:
        return jsonify({'message': '添加消息失败'}), 400
    
    # 通知相关用户讨论有新消息
    from src.app import socketio
    socketio.emit('discussion_message', {
        'discussion_id': discussion_id,
        'user_id': str(current_user['_id']),
        'user_name': current_user['name'],
        'content': data['content'],
        'class_id': discussion['class_id']
    }, room=discussion_id)
    
    return jsonify({'message': '消息发送成功'}), 200

@interaction_bp.route('/class/<class_id>/interactions', methods=['GET'])
@token_required
def get_class_interactions(current_user, class_id):
    interaction_type = request.args.get('type')
    
    interactions = get_interaction_model().get_class_interactions(
        class_id,
        interaction_type
    )
    
    return jsonify(mongo_to_json(interactions)), 200

@interaction_bp.route('/interaction/<interaction_id>', methods=['GET'])
@token_required
def get_interaction(current_user, interaction_id):
    interaction = get_interaction_model().get_interaction_by_id(interaction_id)
    
    if not interaction:
        return jsonify({'message': '互动不存在'}), 404
    
    return jsonify(mongo_to_json(interaction)), 200

@interaction_bp.route('/interaction/<interaction_id>/close', methods=['POST'])
@token_required
@teacher_required
def close_interaction(current_user, interaction_id):
    # 获取互动信息
    interaction = get_interaction_model().get_interaction_by_id(interaction_id)
    if not interaction:
        return jsonify({'message': '互动不存在'}), 404
    
    if interaction['type'] not in ['poll', 'discussion']:
        return jsonify({'message': '只能关闭投票或讨论'}), 400
    
    success = get_interaction_model().close_interaction(interaction_id)
    
    if not success:
        return jsonify({'message': '关闭互动失败'}), 400
    
    # 通知相关用户互动已关闭
    from src.app import socketio
    socketio.emit('interaction_closed', {
        'interaction_id': interaction_id,
        'type': interaction['type'],
        'class_id': interaction['class_id']
    }, room=interaction['class_id'])
    
    return jsonify({'message': '互动已关闭'}), 200 