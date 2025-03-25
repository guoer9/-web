from datetime import datetime
from bson.objectid import ObjectId

class Interaction:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.interactions
    
    def create_question(self, student_id, class_id, content):
        """学生提问"""
        interaction_data = {
            "type": "question",
            "student_id": student_id,
            "class_id": class_id,
            "content": content,
            "status": "pending",  # pending, answered, rejected
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = self.collection.insert_one(interaction_data)
        return str(result.inserted_id)
    
    def answer_question(self, question_id, teacher_id, answer):
        """教师回答问题"""
        result = self.collection.update_one(
            {"_id": ObjectId(question_id)},
            {
                "$set": {
                    "teacher_id": teacher_id,
                    "answer": answer,
                    "status": "answered",
                    "answered_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    def create_poll(self, teacher_id, class_id, title, options):
        """教师创建投票"""
        poll_data = {
            "type": "poll",
            "teacher_id": teacher_id,
            "class_id": class_id,
            "title": title,
            "options": options,
            "votes": {option: 0 for option in options},
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = self.collection.insert_one(poll_data)
        return str(result.inserted_id)
    
    def vote_poll(self, poll_id, student_id, option):
        """学生投票"""
        # 首先检查学生是否已经投票
        poll = self.collection.find_one({
            "_id": ObjectId(poll_id),
            "voters": {"$elemMatch": {"student_id": student_id}}
        })
        
        if poll:
            # 学生已投票，更新选项
            old_option = next(voter["option"] for voter in poll["voters"] if voter["student_id"] == student_id)
            
            # 减少原选项的票数
            self.collection.update_one(
                {"_id": ObjectId(poll_id)},
                {"$inc": {f"votes.{old_option}": -1}}
            )
            
            # 更新学生的选择
            self.collection.update_one(
                {"_id": ObjectId(poll_id), "voters.student_id": student_id},
                {"$set": {"voters.$.option": option, "updated_at": datetime.now()}}
            )
        else:
            # 学生首次投票
            self.collection.update_one(
                {"_id": ObjectId(poll_id)},
                {
                    "$push": {"voters": {"student_id": student_id, "option": option}},
                    "$inc": {f"votes.{option}": 1},
                    "$set": {"updated_at": datetime.now()}
                }
            )
        
        return True
    
    def create_discussion(self, teacher_id, class_id, title, description):
        """创建小组讨论"""
        discussion_data = {
            "type": "discussion",
            "teacher_id": teacher_id,
            "class_id": class_id,
            "title": title,
            "description": description,
            "messages": [],
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = self.collection.insert_one(discussion_data)
        return str(result.inserted_id)
    
    def add_discussion_message(self, discussion_id, user_id, content):
        """添加讨论消息"""
        message = {
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now()
        }
        
        result = self.collection.update_one(
            {"_id": ObjectId(discussion_id)},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    def get_class_interactions(self, class_id, interaction_type=None, limit=50):
        """获取班级互动记录"""
        query = {"class_id": class_id}
        if interaction_type:
            query["type"] = interaction_type
        
        interactions = list(
            self.collection.find(query).sort("created_at", -1).limit(limit)
        )
        return interactions
    
    def get_interaction_by_id(self, interaction_id):
        """通过ID获取互动记录"""
        return self.collection.find_one({"_id": ObjectId(interaction_id)})
    
    def close_interaction(self, interaction_id):
        """关闭互动（投票或讨论）"""
        result = self.collection.update_one(
            {"_id": ObjectId(interaction_id)},
            {
                "$set": {
                    "status": "closed",
                    "updated_at": datetime.now()
                }
            }
        )
        return result.modified_count > 0 