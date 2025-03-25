from datetime import datetime
from bson.objectid import ObjectId

class Feedback:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.feedback
    
    def create_feedback(self, student_id, class_id, rating, content, is_anonymous=False):
        """学生创建课程反馈"""
        feedback_data = {
            "class_id": class_id,
            "rating": rating,  # 1-5 评分
            "content": content,
            "created_at": datetime.now()
        }
        
        # 如果不是匿名反馈，添加学生ID
        if not is_anonymous:
            feedback_data["student_id"] = student_id
        
        result = self.collection.insert_one(feedback_data)
        return str(result.inserted_id)
    
    def get_class_feedback(self, class_id, limit=50):
        """获取班级的所有反馈"""
        feedbacks = list(
            self.collection.find({"class_id": class_id}).sort("created_at", -1).limit(limit)
        )
        return feedbacks
    
    def get_feedback_stats(self, class_id):
        """获取班级反馈统计数据"""
        pipeline = [
            {"$match": {"class_id": class_id}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "average_rating": {"$avg": "$rating"},
                "rating_counts": {
                    "$push": "$rating"
                }
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        if not result:
            return {
                "total": 0,
                "average_rating": 0,
                "rating_distribution": {
                    "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
                }
            }
        
        stats = result[0]
        
        # 计算评分分布
        rating_distribution = {
            "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
        }
        
        for rating in stats["rating_counts"]:
            rating_distribution[str(rating)] += 1
        
        return {
            "total": stats["total"],
            "average_rating": round(stats["average_rating"], 1),
            "rating_distribution": rating_distribution
        }
    
    def get_student_feedback(self, student_id, limit=20):
        """获取特定学生的反馈记录"""
        feedbacks = list(
            self.collection.find({"student_id": student_id}).sort("created_at", -1).limit(limit)
        )
        return feedbacks 