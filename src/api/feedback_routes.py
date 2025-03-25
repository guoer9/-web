from flask import Blueprint, request, jsonify
from src.models.feedback import Feedback
from src.api.auth_routes import token_required, teacher_required
from bson.json_util import dumps, loads
import json

feedback_bp = Blueprint('feedback', __name__)

# 从应用上下文获取模型
def get_feedback_model():
    from src.app import mongo
    return Feedback(mongo)

# 将MongoDB对象转换为JSON
def mongo_to_json(data):
    return json.loads(dumps(data))

@feedback_bp.route('', methods=['POST'])
@token_required
def create_feedback(current_user):
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以提交反馈'}), 403
    
    data = request.get_json()
    
    if not all(key in data for key in ['class_id', 'rating', 'content']):
        return jsonify({'message': '缺少必要字段'}), 400
    
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'message': '评分必须是1-5之间的整数'}), 400
    
    feedback_id = get_feedback_model().create_feedback(
        str(current_user['_id']),
        data['class_id'],
        data['rating'],
        data['content'],
        data.get('is_anonymous', False)
    )
    
    return jsonify({
        'message': '反馈提交成功',
        'feedback_id': feedback_id
    }), 201

@feedback_bp.route('/class/<class_id>', methods=['GET'])
@token_required
@teacher_required
def get_class_feedback(current_user, class_id):
    feedbacks = get_feedback_model().get_class_feedback(class_id)
    return jsonify(mongo_to_json(feedbacks)), 200

@feedback_bp.route('/class/<class_id>/stats', methods=['GET'])
@token_required
def get_feedback_stats(current_user, class_id):
    stats = get_feedback_model().get_feedback_stats(class_id)
    return jsonify(stats), 200

@feedback_bp.route('/student', methods=['GET'])
@token_required
def get_student_feedback(current_user):
    if current_user['role'] != 'student':
        return jsonify({'message': '只有学生可以查看自己的反馈记录'}), 403
    
    feedbacks = get_feedback_model().get_student_feedback(str(current_user['_id']))
    return jsonify(mongo_to_json(feedbacks)), 200 