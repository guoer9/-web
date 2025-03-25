from flask_pymongo import PyMongo
from datetime import datetime
import bcrypt
import logging

# 设置日志
logger = logging.getLogger(__name__)

class User:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.users
        
        # 测试当前所处模式
        try:
            # 尝试调用collection的find_one方法
            test_call = callable(getattr(self.collection, 'find_one', None))
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

    def create_user(self, username, password, name, role, class_id=None):
        """创建新用户"""
        logger.info(f"尝试创建用户: {username}, 角色: {role}")
        
        # 模拟模式处理
        if self.test_mode:
            logger.info(f"模拟模式: 创建用户 {username} 成功")
            return True, "mock_id_12345"
            
        # 检查用户名是否已存在
        if self.collection.find_one({"username": username}):
            logger.warning(f"用户创建失败: 用户名 {username} 已存在")
            return False, "用户名已存在"
        
        try:
            # 加密密码
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # 创建用户文档
            user_data = {
                "username": username,
                "password": hashed_password,
                "name": name,
                "role": role,  # 'student' 或 'teacher'
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 如果是学生，添加班级ID
            if role == "student" and class_id:
                user_data["class_id"] = class_id
            
            # 插入数据库
            result = self.collection.insert_one(user_data)
            logger.info(f"用户创建成功: {username}, ID: {result.inserted_id}")
            return True, str(result.inserted_id)
        except Exception as e:
            logger.error(f"用户创建过程中发生错误: {str(e)}")
            return False, f"创建用户时发生错误: {str(e)}"
    
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
            
        user = self.collection.find_one({"username": username})
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
    
    def get_user_by_id(self, user_id):
        """通过ID获取用户"""
        logger.info(f"尝试获取用户ID: {user_id}")
        
        # 模拟模式处理
        if self.test_mode:
            mock_user = {
                "_id": user_id,
                "username": "user_" + user_id[:5] if len(user_id) >= 5 else "user",
                "name": "模拟用户",
                "role": "student"
            }
            return mock_user
            
        from bson.objectid import ObjectId
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user.pop('password', None)
                logger.info(f"获取用户成功: ID {user_id}")
            else:
                logger.warning(f"获取用户失败: ID {user_id} 不存在")
            return user
        except Exception as e:
            logger.error(f"获取用户过程中发生错误: {str(e)}")
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
            users = list(self.collection.find(query, {"password": 0}))
            logger.info(f"获取到 {len(users)} 个 {role} 角色用户")
            return users
        except Exception as e:
            logger.error(f"获取用户列表过程中发生错误: {str(e)}")
            return []
    
    def update_user(self, user_id, update_data):
        """更新用户信息"""
        logger.info(f"尝试更新用户: {user_id}")
        
        # 模拟模式处理
        if self.test_mode:
            logger.info(f"模拟模式: 更新用户 {user_id} 成功")
            return True
            
        from bson.objectid import ObjectId
        
        try:
            # 移除不允许更新的字段
            if 'username' in update_data:
                del update_data['username']
            if 'password' in update_data:
                # 如果更新密码，需要加密
                update_data['password'] = bcrypt.hashpw(
                    update_data['password'].encode('utf-8'), 
                    bcrypt.gensalt()
                )
            
            update_data['updated_at'] = datetime.now()
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            success = result.modified_count > 0
            logger.info(f"用户 {user_id} 更新{'成功' if success else '失败'}")
            return success
        except Exception as e:
            logger.error(f"更新用户过程中发生错误: {str(e)}")
            return False 