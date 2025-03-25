"""
教学资源模型模块
定义资源的数据结构和处理逻辑
"""
from datetime import datetime
from bson.objectid import ObjectId
import os
import hashlib
import mimetypes

class ResourceModel:
    """教学资源模型类"""
    
    RESOURCE_TYPES = [
        "document", "image", "video", "audio", "link", "other"
    ]
    
    RESOURCE_TAGS = [
        "教案", "课件", "练习", "考试", "阅读材料", "参考资料", "视频教程", "音频材料"
    ]
    
    def __init__(self, mongo):
        """
        初始化资源模型
        
        Args:
            mongo: MongoDB连接实例
        """
        self.mongo = mongo
        self._ensure_indexes()
        
    def _ensure_indexes(self):
        """确保创建必要的索引"""
        # 尝试创建索引，如果数据库不可用则跳过
        try:
            self.mongo.db.resources.create_index([("title", "text"), ("description", "text")])
            self.mongo.db.resources.create_index("teacher_id")
            self.mongo.db.resources.create_index("class_id")
            self.mongo.db.resources.create_index("type")
            self.mongo.db.resources.create_index("tags")
            self.mongo.db.resources.create_index("created_at")
        except Exception as e:
            print(f"创建资源索引失败: {str(e)}")
    
    def create_resource(self, data):
        """
        创建新资源
        
        Args:
            data: 资源数据，包含title, description, teacher_id, class_id等
            
        Returns:
            resource_id: 新创建的资源ID
        """
        resource = {
            "title": data.get("title", "未命名资源"),
            "description": data.get("description", ""),
            "type": data.get("type", "document"),
            "tags": data.get("tags", []),
            "teacher_id": ObjectId(data["teacher_id"]) if "teacher_id" in data else None,
            "class_id": ObjectId(data["class_id"]) if "class_id" in data else None,
            "file_path": data.get("file_path", ""),
            "file_size": data.get("file_size", 0),
            "mime_type": data.get("mime_type", ""),
            "external_url": data.get("external_url", ""),
            "download_count": 0,
            "view_count": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 验证资源类型
        if resource["type"] not in self.RESOURCE_TYPES:
            resource["type"] = "other"
        
        # 过滤无效标签
        resource["tags"] = [tag for tag in resource["tags"] if tag in self.RESOURCE_TAGS]
        
        result = self.mongo.db.resources.insert_one(resource)
        return str(result.inserted_id)
    
    def get_resource(self, resource_id):
        """
        获取资源详情
        
        Args:
            resource_id: 资源ID
            
        Returns:
            resource: 资源详情
        """
        resource = self.mongo.db.resources.find_one({"_id": ObjectId(resource_id)})
        if resource:
            resource["_id"] = str(resource["_id"])
            if "teacher_id" in resource and resource["teacher_id"]:
                resource["teacher_id"] = str(resource["teacher_id"])
            if "class_id" in resource and resource["class_id"]:
                resource["class_id"] = str(resource["class_id"])
            
            # 更新查看次数
            self.mongo.db.resources.update_one(
                {"_id": ObjectId(resource_id)},
                {"$inc": {"view_count": 1}}
            )
        
        return resource
    
    def update_resource(self, resource_id, data):
        """
        更新资源信息
        
        Args:
            resource_id: 资源ID
            data: 要更新的资源数据
            
        Returns:
            success: 更新是否成功
        """
        update_data = {}
        
        # 只更新提供的字段
        allowed_fields = ["title", "description", "tags", "class_id", "external_url"]
        for field in allowed_fields:
            if field in data:
                if field == "class_id" and data[field]:
                    update_data[field] = ObjectId(data[field])
                else:
                    update_data[field] = data[field]
        
        if update_data:
            update_data["updated_at"] = datetime.now()
            
            result = self.mongo.db.resources.update_one(
                {"_id": ObjectId(resource_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        
        return False
    
    def delete_resource(self, resource_id):
        """
        删除资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            success: 删除是否成功
        """
        # 获取资源信息(用于删除文件)
        resource = self.mongo.db.resources.find_one({"_id": ObjectId(resource_id)})
        
        if not resource:
            return False
        
        # 删除数据库记录
        result = self.mongo.db.resources.delete_one({"_id": ObjectId(resource_id)})
        
        # 如果有物理文件，尝试删除
        if result.deleted_count > 0 and resource.get("file_path"):
            try:
                if os.path.exists(resource["file_path"]):
                    os.remove(resource["file_path"])
            except Exception as e:
                print(f"删除文件失败: {str(e)}")
        
        return result.deleted_count > 0
    
    def search_resources(self, query, filters=None, page=1, page_size=20):
        """
        搜索资源
        
        Args:
            query: 搜索关键词
            filters: 过滤条件，例如类型、标签等
            page: 页码
            page_size: 每页记录数
            
        Returns:
            resources: 资源列表
            total: 总记录数
            page_count: 总页数
        """
        filter_condition = {}
        
        # 添加文本搜索条件
        if query:
            filter_condition["$text"] = {"$search": query}
        
        # 添加过滤条件
        if filters:
            if "type" in filters and filters["type"]:
                filter_condition["type"] = filters["type"]
            
            if "tags" in filters and filters["tags"]:
                filter_condition["tags"] = {"$in": filters["tags"]}
            
            if "teacher_id" in filters and filters["teacher_id"]:
                filter_condition["teacher_id"] = ObjectId(filters["teacher_id"])
            
            if "class_id" in filters and filters["class_id"]:
                filter_condition["class_id"] = ObjectId(filters["class_id"])
        
        # 计算总记录数
        total = self.mongo.db.resources.count_documents(filter_condition)
        
        # 计算总页数
        page_count = (total + page_size - 1) // page_size
        
        # 查询数据
        cursor = self.mongo.db.resources.find(filter_condition)
        
        # 排序 (默认按创建时间降序)
        cursor = cursor.sort("created_at", -1)
        
        # 分页
        cursor = cursor.skip((page - 1) * page_size).limit(page_size)
        
        # 处理结果
        resources = []
        for resource in cursor:
            resource["_id"] = str(resource["_id"])
            if "teacher_id" in resource and resource["teacher_id"]:
                resource["teacher_id"] = str(resource["teacher_id"])
            if "class_id" in resource and resource["class_id"]:
                resource["class_id"] = str(resource["class_id"])
            resources.append(resource)
        
        return {
            "resources": resources,
            "total": total,
            "page_count": page_count,
            "current_page": page,
            "page_size": page_size
        }
    
    def get_teacher_resources(self, teacher_id, page=1, page_size=20):
        """
        获取教师的所有资源
        
        Args:
            teacher_id: 教师ID
            page: 页码
            page_size: 每页记录数
            
        Returns:
            resources: 资源列表
            total: 总记录数
            page_count: 总页数
        """
        return self.search_resources(
            query=None, 
            filters={"teacher_id": teacher_id}, 
            page=page, 
            page_size=page_size
        )
    
    def get_class_resources(self, class_id, page=1, page_size=20):
        """
        获取班级的所有资源
        
        Args:
            class_id: 班级ID
            page: 页码
            page_size: 每页记录数
            
        Returns:
            resources: 资源列表
            total: 总记录数
            page_count: 总页数
        """
        return self.search_resources(
            query=None, 
            filters={"class_id": class_id}, 
            page=page, 
            page_size=page_size
        )
    
    def increment_download_count(self, resource_id):
        """
        增加资源下载计数
        
        Args:
            resource_id: 资源ID
        """
        self.mongo.db.resources.update_one(
            {"_id": ObjectId(resource_id)},
            {"$inc": {"download_count": 1}}
        )
    
    @staticmethod
    def get_file_type(filename):
        """
        根据文件名获取资源类型
        
        Args:
            filename: 文件名
            
        Returns:
            type: 资源类型
        """
        mime = mimetypes.guess_type(filename)[0]
        
        if mime:
            if mime.startswith('image/'):
                return "image"
            elif mime.startswith('video/'):
                return "video"
            elif mime.startswith('audio/'):
                return "audio"
            elif mime in ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'application/vnd.ms-excel',
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         'application/vnd.ms-powerpoint',
                         'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                         'text/plain']:
                return "document"
        
        # 根据扩展名判断
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt']:
            return "document"
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
            return "image"
        elif ext in ['.mp4', '.avi', '.mov', '.flv', '.wmv']:
            return "video"
        elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
            return "audio"
            
        return "other"
    
    @staticmethod
    def generate_file_path(upload_dir, filename):
        """
        生成文件保存路径
        
        Args:
            upload_dir: 上传目录
            filename: 原始文件名
            
        Returns:
            file_path: 文件保存路径
        """
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(filename)
        hash_obj = hashlib.md5(f"{name}{timestamp}".encode())
        hashed_name = hash_obj.hexdigest()
        
        # 生成文件路径
        return os.path.join(upload_dir, f"{hashed_name}{ext}") 