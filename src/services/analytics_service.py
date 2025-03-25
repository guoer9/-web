"""
数据分析服务模块，提供教学互动和反馈数据的统计分析功能
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from bson.json_util import dumps
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter

class AnalyticsService:
    def __init__(self, mongo):
        """
        初始化数据分析服务
        
        Args:
            mongo: MongoDB连接实例
        """
        self.mongo = mongo
        
    def generate_interaction_report(self, teacher_id, start_date=None, end_date=None):
        """
        生成互动数据报告
        
        Args:
            teacher_id: 教师ID
            start_date: 开始日期，默认为过去30天
            end_date: 结束日期，默认为当前日期
            
        Returns:
            report_data: 报告数据，包含统计数据和图表
        """
        # 设置默认时间范围为过去30天
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        # 查询指定时间范围内的互动数据
        questions = list(self.mongo.db.interactions.find({
            "teacher_id": teacher_id,
            "type": "question",
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        polls = list(self.mongo.db.interactions.find({
            "teacher_id": teacher_id,
            "type": "poll",
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        discussions = list(self.mongo.db.interactions.find({
            "teacher_id": teacher_id,
            "type": "discussion",
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # 基本统计数据
        report_data = {
            "summary": {
                "total_questions": len(questions),
                "total_polls": len(polls),
                "total_discussions": len(discussions),
                "total_interactions": len(questions) + len(polls) + len(discussions)
            },
            "questions": self._analyze_questions(questions),
            "polls": self._analyze_polls(polls),
            "discussions": self._analyze_discussions(discussions),
            "charts": self._generate_interaction_charts(questions, polls, discussions)
        }
        
        return report_data
    
    def generate_feedback_report(self, teacher_id, start_date=None, end_date=None):
        """
        生成反馈数据报告
        
        Args:
            teacher_id: 教师ID
            start_date: 开始日期，默认为过去30天
            end_date: 结束日期，默认为当前日期
            
        Returns:
            report_data: 报告数据，包含统计数据和图表
        """
        # 设置默认时间范围为过去30天
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        # 查询指定时间范围内的反馈数据
        feedbacks = list(self.mongo.db.feedbacks.find({
            "teacher_id": teacher_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # 基本统计数据
        report_data = {
            "summary": {
                "total_feedbacks": len(feedbacks),
                "average_rating": self._calculate_average_rating(feedbacks),
                "positive_feedback_percentage": self._calculate_sentiment_percentage(feedbacks, "positive"),
                "negative_feedback_percentage": self._calculate_sentiment_percentage(feedbacks, "negative")
            },
            "detailed_analysis": self._analyze_feedback_text(feedbacks),
            "charts": self._generate_feedback_charts(feedbacks)
        }
        
        return report_data
    
    def _analyze_questions(self, questions):
        """分析问题数据"""
        if not questions:
            return {"count": 0}
            
        # 计算回答率
        answered_count = sum(1 for q in questions if q.get("answered", False))
        answer_rate = answered_count / len(questions) if questions else 0
        
        # 分析问题类型
        question_types = Counter([q.get("category", "未分类") for q in questions])
        
        return {
            "count": len(questions),
            "answer_rate": answer_rate,
            "question_types": dict(question_types),
            "avg_response_time": self._calculate_avg_response_time(questions)
        }
    
    def _analyze_polls(self, polls):
        """分析投票数据"""
        if not polls:
            return {"count": 0}
            
        # 计算平均参与人数
        avg_participants = sum(len(p.get("responses", [])) for p in polls) / len(polls) if polls else 0
        
        return {
            "count": len(polls),
            "avg_participants": avg_participants,
            "completion_rate": self._calculate_poll_completion_rate(polls)
        }
    
    def _analyze_discussions(self, discussions):
        """分析讨论数据"""
        if not discussions:
            return {"count": 0}
            
        # 计算平均参与人数和消息数
        avg_participants = sum(len(set(msg.get("user_id") for msg in d.get("messages", []))) for d in discussions) / len(discussions) if discussions else 0
        avg_messages = sum(len(d.get("messages", [])) for d in discussions) / len(discussions) if discussions else 0
        
        return {
            "count": len(discussions),
            "avg_participants": avg_participants,
            "avg_messages": avg_messages
        }
    
    def _calculate_average_rating(self, feedbacks):
        """计算平均评分"""
        if not feedbacks:
            return 0
        return sum(f.get("rating", 0) for f in feedbacks) / len(feedbacks)
    
    def _calculate_sentiment_percentage(self, feedbacks, sentiment_type):
        """计算情感百分比"""
        if not feedbacks:
            return 0
        count = sum(1 for f in feedbacks if f.get("sentiment") == sentiment_type)
        return (count / len(feedbacks)) * 100
    
    def _calculate_avg_response_time(self, questions):
        """计算平均响应时间（分钟）"""
        response_times = []
        for q in questions:
            if q.get("answered_at") and q.get("created_at"):
                delta = q["answered_at"] - q["created_at"]
                response_times.append(delta.total_seconds() / 60)  # 转换为分钟
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_poll_completion_rate(self, polls):
        """计算投票完成率"""
        if not polls:
            return 0
        
        completion_rates = []
        for poll in polls:
            if poll.get("student_count", 0) > 0:
                response_count = len(poll.get("responses", []))
                completion_rates.append(response_count / poll["student_count"])
        
        return sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    def _analyze_feedback_text(self, feedbacks):
        """分析反馈文本"""
        if not feedbacks:
            return {}
            
        # 提取常见关键词
        all_text = " ".join([f.get("content", "") for f in feedbacks if f.get("content")])
        words = all_text.lower().split()
        word_counts = Counter(words)
        
        # 过滤掉常见停用词
        stop_words = {"的", "了", "和", "在", "是", "我", "有", "不", "这", "也", "都", "他", "你"}
        for word in stop_words:
            if word in word_counts:
                del word_counts[word]
        
        return {
            "common_keywords": dict(word_counts.most_common(10)),
            "avg_feedback_length": sum(len(f.get("content", "")) for f in feedbacks) / len(feedbacks)
        }
    
    def _generate_interaction_charts(self, questions, polls, discussions):
        """生成互动数据图表"""
        charts = {}
        
        # 互动类型分布饼图
        if questions or polls or discussions:
            labels = ['问题', '投票', '讨论']
            sizes = [len(questions), len(polls), len(discussions)]
            
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('互动类型分布')
            
            # 转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            charts["interaction_type_distribution"] = chart_data
        
        # 如果有足够的数据，生成互动趋势图
        if len(questions) >= 5 or len(polls) >= 5 or len(discussions) >= 5:
            # 准备时间序列数据
            all_interactions = []
            for q in questions:
                all_interactions.append((q["created_at"], "问题"))
            for p in polls:
                all_interactions.append((p["created_at"], "投票"))
            for d in discussions:
                all_interactions.append((d["created_at"], "讨论"))
            
            # 按时间排序
            all_interactions.sort(key=lambda x: x[0])
            
            # 仅使用最近30个数据点
            recent_interactions = all_interactions[-30:] if len(all_interactions) > 30 else all_interactions
            
            dates = [i[0].strftime('%m-%d') for i in recent_interactions]
            types = [i[1] for i in recent_interactions]
            
            plt.figure(figsize=(12, 6))
            for t, c in zip(['问题', '投票', '讨论'], ['blue', 'green', 'red']):
                indices = [i for i, x in enumerate(types) if x == t]
                if indices:
                    plt.scatter([dates[i] for i in indices], [1 for _ in indices], label=t, color=c)
            
            plt.yticks([])  # 隐藏y轴刻度
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.legend()
            plt.title('互动时间线')
            
            # 转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            charts["interaction_timeline"] = chart_data
            
        return charts
    
    def _generate_feedback_charts(self, feedbacks):
        """生成反馈数据图表"""
        charts = {}
        
        # 评分分布图
        if feedbacks:
            ratings = [f.get("rating", 0) for f in feedbacks]
            rating_counts = Counter(ratings)
            
            plt.figure(figsize=(10, 6))
            plt.bar(rating_counts.keys(), rating_counts.values())
            plt.xlabel('评分')
            plt.ylabel('数量')
            plt.title('反馈评分分布')
            plt.xticks(range(1, 6))
            
            # 转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            charts["rating_distribution"] = chart_data
            
            # 情感分析饼图
            sentiment_counts = Counter([f.get("sentiment", "neutral") for f in feedbacks])
            labels = ['正面', '中性', '负面']
            sizes = [sentiment_counts.get("positive", 0), 
                     sentiment_counts.get("neutral", 0), 
                     sentiment_counts.get("negative", 0)]
            
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                   colors=['green', 'gray', 'red'])
            plt.axis('equal')
            plt.title('反馈情感分布')
            
            # 转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            charts["sentiment_distribution"] = chart_data
            
        return charts
    
    def get_student_engagement_data(self, class_id, start_date=None, end_date=None):
        """
        获取学生参与度数据
        
        Args:
            class_id: 班级ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            engagement_data: 学生参与度数据
        """
        # 设置默认时间范围为过去30天
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        # 获取班级学生
        students = list(self.mongo.db.users.find({"class_id": class_id, "role": "student"}))
        
        engagement_data = []
        for student in students:
            student_id = student["_id"]
            
            # 统计学生的互动次数
            question_count = self.mongo.db.interactions.count_documents({
                "student_id": student_id,
                "type": "question",
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            poll_count = self.mongo.db.interactions.count_documents({
                "student_id": student_id,
                "type": "poll_response",
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            discussion_count = self.mongo.db.interactions.count_documents({
                "user_id": student_id,
                "type": "discussion_message",
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            feedback_count = self.mongo.db.feedbacks.count_documents({
                "student_id": student_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            total_interactions = question_count + poll_count + discussion_count + feedback_count
            
            # 计算参与度分数 (简单算法，可以根据需要调整)
            engagement_score = min(100, total_interactions * 10)  # 上限为100分
            
            engagement_data.append({
                "student_id": str(student_id),
                "student_name": student.get("name", "未知学生"),
                "question_count": question_count,
                "poll_participation": poll_count,
                "discussion_participation": discussion_count,
                "feedback_submission": feedback_count,
                "total_interactions": total_interactions,
                "engagement_score": engagement_score
            })
            
        # 按参与度分数排序
        engagement_data.sort(key=lambda x: x["engagement_score"], reverse=True)
        
        return engagement_data 