from flask_pymongo import PyMongo
from datetime import datetime
import bcrypt
import logging
from bson import ObjectId

# 设置日志
logger = logging.getLogger(__name__)

class User:
    def __init__(self, mongo):
        self.db = mongo.db
        self.users = self.db.users
        
        # 测试当前所处模式
        try:
            # 尝试调用collection的find_one方法
            test_call = callable(getattr(self.users, 'find_one', None))
            # 检查是否有users属性 - 这是MockDB的特性
            has_users = hasattr(mongo.db, 'users') and isinstance(getattr(mongo.db, 'users', None), dict)
            self.test_mode = has_users or not test_call
            
            if self.test_mode:
                logger.warning("用户模型初始化: 使用模拟数据库模式")
            else:
                logger.info("用户模型初始化: 使用真实数据库模式")
        except Exception as e:
            logger.error(f"模式检测发生错误: {str(e)}")
            self.test_mode = True
            logger.warning("默认使用模拟数据库模式")

    def create_user(self, user_data):
        """创建新用户"""
        try:
            result = self.users.insert_one(user_data)
            return str(result.inserted_id) if result.inserted_id else None
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id):
        """通过ID获取用户"""
        try:
            return self.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            return None
    
    def get_user_by_username(self, username):
        """通过用户名获取用户"""
        try:
            return self.users.find_one({'username': username})
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            return None
    
    def update_user(self, user_id, update_data):
        """更新用户信息"""
        try:
            result = self.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            return False
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            result = self.users.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            return False
    
    def get_users_by_role(self, role, class_id=None):
        """获取指定角色的用户列表"""
        try:
            query = {'role': role}
            if class_id:
                query['class_id'] = class_id
            return list(self.users.find(query))
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            return []
    
    def get_all_users(self):
        """获取所有用户"""
        try:
            return list(self.users.find())
        except Exception as e:
            logger.error(f"获取所有用户失败: {str(e)}")
            return []
    
    def count_users_by_role(self, role):
        """统计指定角色的用户数量"""
        try:
            return self.users.count_documents({'role': role})
        except Exception as e:
            logger.error(f"统计用户数量失败: {str(e)}")
            return 0
    
    def authenticate(self, username, password):
        """验证用户"""
        logger.info(f"尝试验证用户: {username}")
        
        # 模拟模式处理
        if self.test_mode:
            mock_user = {
                "_id": "mock_id_12345",
                "username": username,
                "name": "模拟用户",
                "role": "student"
            }
            logger.info(f"模拟模式: 用户 {username} 验证成功")
            return mock_user
            
        user = self.users.find_one({"username": username})
        if not user:
            logger.warning(f"验证失败: 用户 {username} 不存在")
            return None
        
        try:
            # 验证密码
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                # 移除密码后返回用户信息
                user.pop('password', None)
                logger.info(f"用户 {username} 验证成功")
                return user
            logger.warning(f"验证失败: 用户 {username} 密码错误")
            return None
        except Exception as e:
            logger.error(f"验证过程中发生错误: {str(e)}")
            return None
    
    def get_users_by_role(self, role, class_id=None):
        """获取特定角色的用户"""
        logger.info(f"尝试获取角色 {role} 的用户" + (f", 班级: {class_id}" if class_id else ""))
        
        # 模拟模式处理
        if self.test_mode:
            return [
                {"_id": "mock_id_1", "name": "模拟用户1", "username": "user1", "role": role},
                {"_id": "mock_id_2", "name": "模拟用户2", "username": "user2", "role": role}
            ]
            
        query = {"role": role}
        if class_id:
            query["class_id"] = class_id
        
        try:
            users = list(self.users.find(query, {"password": 0}))
            logger.info(f"获取到 {len(users)} 个 {role} 角色用户")
            return users
        except Exception as e:
            logger.error(f"获取用户列表过程中发生错误: {str(e)}")
            return [] 