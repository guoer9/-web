from datetime import datetime
from bson import ObjectId
import uuid
import logging

# 设置日志
logger = logging.getLogger(__name__)

class Interaction:
    def __init__(self, mongo):
        self.db = mongo.db
        self.interactions = self.db.interactions
        self.questions = self.db.questions
        self.polls = self.db.polls
        self.votes = self.db.votes
        # 创建索引
        self.interactions.create_index([("type", 1)])
        self.interactions.create_index([("status", 1)])
        
    def create_question(self, student_id, subject, content, is_urgent=False):
        """创建新问题"""
        try:
            question = {
                'student_id': student_id,
                'subject': subject,
                'content': content,
                'is_urgent': is_urgent,
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            result = self.questions.insert_one(question)
            return str(result.inserted_id)
        except Exception as e:
            print(f"创建问题失败: {str(e)}")
            return None

    def get_student_questions(self, student_id):
        """获取学生的问题列表"""
        try:
            return list(self.questions.find({'student_id': student_id}).sort('created_at', -1))
        except Exception as e:
            print(f"获取学生问题失败: {str(e)}")
            return []

    def get_pending_questions(self):
        """获取所有待回答的问题"""
        try:
            return list(self.questions.find({'status': 'pending'}).sort('created_at', -1))
        except Exception as e:
            print(f"获取待回答问题失败: {str(e)}")
            return []

    def get_answered_questions(self):
        """获取所有已回答的问题"""
        try:
            return list(self.questions.find({'status': 'answered'}).sort('created_at', -1))
        except Exception as e:
            print(f"获取已回答问题失败: {str(e)}")
            return []

    def answer_question(self, question_id, teacher_id, teacher_name, content):
        """回答问题"""
        try:
            result = self.questions.update_one(
                {'_id': ObjectId(question_id)},
                {
                    '$set': {
                        'status': 'answered',
                        'answer': {
                            'teacher_id': teacher_id,
                            'teacher_name': teacher_name,
                            'content': content,
                            'created_at': datetime.utcnow()
                        }
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"回答问题失败: {str(e)}")
            return False

    def count_pending_questions(self):
        """统计待回答问题数量"""
        try:
            return self.questions.count_documents({'status': 'pending'})
        except Exception as e:
            print(f"统计待回答问题失败: {str(e)}")
            return 0

    def count_urgent_questions(self):
        """统计紧急问题数量"""
        try:
            return self.questions.count_documents({
                'status': 'pending',
                'is_urgent': True
            })
        except Exception as e:
            print(f"统计紧急问题失败: {str(e)}")
            return 0

    def create_poll(self, teacher_id, teacher_name, title, options, duration=0):
        """创建新投票"""
        try:
            poll = {
                'teacher_id': teacher_id,
                'teacher_name': teacher_name,
                'title': title,
                'options': options,
                'votes': {option: 0 for option in options},
                'status': 'active',
                'created_at': datetime.utcnow(),
                'duration': duration
            }
            result = self.polls.insert_one(poll)
            return str(result.inserted_id)
        except Exception as e:
            print(f"创建投票失败: {str(e)}")
            return None

    def get_active_polls(self):
        """获取活跃的投票列表"""
        try:
            return list(self.polls.find({'status': 'active'}).sort('created_at', -1))
        except Exception as e:
            print(f"获取活跃投票失败: {str(e)}")
            return []

    def get_ended_polls(self):
        """获取已结束的投票列表"""
        try:
            return list(self.polls.find({'status': 'ended'}).sort('created_at', -1))
        except Exception as e:
            print(f"获取已结束投票失败: {str(e)}")
            return []

    def vote_poll(self, poll_id, student_id, option):
        """提交投票"""
        try:
            # 检查是否已经投票
            if self.votes.find_one({'poll_id': poll_id, 'student_id': student_id}):
                return False
            
            # 检查投票是否仍然活跃
            poll = self.polls.find_one({'_id': ObjectId(poll_id), 'status': 'active'})
            if not poll or option not in poll['options']:
                return False
            
            # 记录投票
            vote = {
                'poll_id': poll_id,
                'student_id': student_id,
                'option': option,
                'created_at': datetime.utcnow()
            }
            self.votes.insert_one(vote)
            
            # 更新投票计数
            self.polls.update_one(
                {'_id': ObjectId(poll_id)},
                {'$inc': {f'votes.{option}': 1}}
            )
            
            return True
        except Exception as e:
            print(f"提交投票失败: {str(e)}")
            return False

    def end_poll(self, poll_id):
        """结束投票"""
        try:
            result = self.polls.update_one(
                {'_id': ObjectId(poll_id)},
                {
                    '$set': {
                        'status': 'ended',
                        'ended_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"结束投票失败: {str(e)}")
            return False

    def count_active_polls(self):
        """统计活跃投票数量"""
        try:
            return self.polls.count_documents({'status': 'active'})
        except Exception as e:
            print(f"统计活跃投票失败: {str(e)}")
            return 0

    def get_student_poll_votes(self, student_id):
        """获取学生的投票记录"""
        try:
            return list(self.votes.find({'student_id': student_id}))
        except Exception as e:
            print(f"获取学生投票记录失败: {str(e)}")
            return []

    def get_interaction_by_id(self, interaction_id):
        """根据ID获取互动详情"""
        # 先尝试查找问题
        question = self.questions.find_one({'_id': ObjectId(interaction_id)})
        if question:
            return question
        
        # 如果不是问题，尝试查找投票
        poll = self.polls.find_one({'_id': ObjectId(interaction_id)})
        if poll:
            return poll
        
        return None

    def _enhance_questions_with_user_details(self, questions):
        """为问题列表添加用户详情"""
        if not questions:
            return
        
        # 收集所有需要查询的用户ID
        student_ids = set()
        teacher_ids = set()
        
        for question in questions:
            if 'student_id' in question:
                student_ids.add(question['student_id'])
            if 'answer' and 'teacher_id' in question.get('answer', {}):
                teacher_ids.add(question['answer']['teacher_id'])
        
        # 查询所有学生信息
        students = {}
        if student_ids:
            student_docs = self.db.users.find({'_id': {'$in': [ObjectId(id) for id in student_ids]}})
            for student in student_docs:
                students[str(student['_id'])] = {
                    'username': student.get('username', ''),
                    'name': student.get('name', '')
                }
        
        # 查询所有教师信息
        teachers = {}
        if teacher_ids:
            teacher_docs = self.db.users.find({'_id': {'$in': [ObjectId(id) for id in teacher_ids]}})
            for teacher in teacher_docs:
                teachers[str(teacher['_id'])] = {
                    'username': teacher.get('username', ''),
                    'name': teacher.get('name', '')
                }
        
        # 添加用户信息到问题
        for question in questions:
            if 'student_id' in question and question['student_id'] in students:
                question['student_name'] = students[question['student_id']].get('name', '未知学生')
                question['student_username'] = students[question['student_id']].get('username', '')
            
            if 'answer' in question and 'teacher_id' in question['answer']:
                teacher_id = question['answer']['teacher_id']
                if teacher_id in teachers:
                    question['answer']['teacher_name'] = teachers[teacher_id].get('name', '未知教师')
                    question['answer']['teacher_username'] = teachers[teacher_id].get('username', '')
    
    def _enhance_polls_with_user_details(self, polls):
        """为投票列表添加用户详情"""
        if not polls:
            return
        
        # 收集所有需要查询的教师ID
        teacher_ids = set()
        
        for poll in polls:
            if 'teacher_id' in poll:
                teacher_ids.add(poll['teacher_id'])
        
        # 查询所有教师信息
        teachers = {}
        if teacher_ids:
            teacher_docs = self.db.users.find({'_id': {'$in': [ObjectId(id) for id in teacher_ids]}})
            for teacher in teacher_docs:
                teachers[str(teacher['_id'])] = {
                    'username': teacher.get('username', ''),
                    'name': teacher.get('name', '')
                }
        
        # 添加教师信息到投票
        for poll in polls:
            if 'teacher_id' in poll and poll['teacher_id'] in teachers:
                poll['teacher_name'] = teachers[poll['teacher_id']].get('name', '未知教师')
                poll['teacher_username'] = teachers[poll['teacher_id']].get('username', '') 