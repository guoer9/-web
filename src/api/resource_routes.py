"""
教学资源API路由
提供教学资源的上传、下载、管理等接口
"""
from flask import Blueprint, jsonify, request, current_app, send_file
from datetime import datetime
from bson.objectid import ObjectId
import os
import json
from werkzeug.utils import secure_filename
from src.models.resource import ResourceModel

resource_bp = Blueprint('resource', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'document': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    'video': ['.mp4', '.avi', '.mov', '.flv', '.wmv'],
    'audio': ['.mp3', '.wav', '.ogg', '.flac']
}

# 资源上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')

def get_resource_model():
    """获取资源模型实例"""
    return ResourceModel(current_app.mongo)

def allowed_file(filename):
    """检查文件是否为允许上传的类型"""
    ext = os.path.splitext(filename)[1].lower()
    for extensions in ALLOWED_EXTENSIONS.values():
        if ext in extensions:
            return True
    return False

@resource_bp.route('/upload', methods=['POST'])
def upload_resource():
    """上传资源文件"""
    try:
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            return jsonify({"error": "请求中未包含文件"}), 400
            
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400
            
        # 检查文件类型是否允许
        if not allowed_file(file.filename):
            return jsonify({"error": "不支持的文件类型"}), 400
            
        # 获取资源元数据
        title = request.form.get('title', '未命名资源')
        description = request.form.get('description', '')
        tags = json.loads(request.form.get('tags', '[]'))
        teacher_id = request.form.get('teacher_id')
        class_id = request.form.get('class_id')
        
        # 检查必要参数
        if not teacher_id:
            return jsonify({"error": "缺少必要参数：teacher_id"}), 400
            
        # 安全处理文件名并保存文件
        filename = secure_filename(file.filename)
        resource_model = get_resource_model()
        
        # 生成文件路径
        file_path = resource_model.generate_file_path(UPLOAD_FOLDER, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 确定资源类型
        resource_type = resource_model.get_file_type(filename)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 创建资源记录
        resource_data = {
            "title": title,
            "description": description,
            "type": resource_type,
            "tags": tags,
            "teacher_id": teacher_id,
            "class_id": class_id,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": file.content_type
        }
        
        resource_id = resource_model.create_resource(resource_data)
        
        return jsonify({
            "success": True,
            "resource_id": resource_id,
            "message": "资源上传成功"
        })
        
    except Exception as e:
        current_app.logger.error(f"资源上传错误: {str(e)}")
        return jsonify({"error": f"资源上传失败: {str(e)}"}), 500

@resource_bp.route('/external', methods=['POST'])
def add_external_resource():
    """添加外部链接资源"""
    try:
        # 解析请求数据
        data = request.json
        
        # 检查必要参数
        required_fields = ['title', 'external_url', 'teacher_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必要参数：{field}"}), 400
                
        # 创建资源记录
        resource_model = get_resource_model()
        resource_data = {
            "title": data['title'],
            "description": data.get('description', ''),
            "type": "link",
            "tags": data.get('tags', []),
            "teacher_id": data['teacher_id'],
            "class_id": data.get('class_id'),
            "external_url": data['external_url']
        }
        
        resource_id = resource_model.create_resource(resource_data)
        
        return jsonify({
            "success": True,
            "resource_id": resource_id,
            "message": "外部资源添加成功"
        })
        
    except Exception as e:
        current_app.logger.error(f"添加外部资源错误: {str(e)}")
        return jsonify({"error": f"添加外部资源失败: {str(e)}"}), 500

@resource_bp.route('/download/<resource_id>', methods=['GET'])
def download_resource(resource_id):
    """下载资源文件"""
    try:
        # 获取资源信息
        resource_model = get_resource_model()
        resource = resource_model.get_resource(resource_id)
        
        if not resource:
            return jsonify({"error": "资源不存在"}), 404
            
        # 检查是否是外部链接
        if resource['type'] == 'link':
            return jsonify({
                "success": True,
                "external_url": resource['external_url']
            })
            
        # 检查文件是否存在
        if not resource.get('file_path') or not os.path.exists(resource['file_path']):
            return jsonify({"error": "资源文件不存在"}), 404
            
        # 增加下载计数
        resource_model.increment_download_count(resource_id)
        
        # 获取文件名
        filename = os.path.basename(resource['file_path'])
        
        # 发送文件
        return send_file(
            resource['file_path'],
            as_attachment=True,
            download_name=filename,
            mimetype=resource.get('mime_type')
        )
        
    except Exception as e:
        current_app.logger.error(f"资源下载错误: {str(e)}")
        return jsonify({"error": f"资源下载失败: {str(e)}"}), 500

@resource_bp.route('/<resource_id>', methods=['GET'])
def get_resource_details(resource_id):
    """获取资源详情"""
    try:
        # 获取资源信息
        resource_model = get_resource_model()
        resource = resource_model.get_resource(resource_id)
        
        if not resource:
            return jsonify({"error": "资源不存在"}), 404
            
        return jsonify({
            "success": True,
            "resource": resource
        })
        
    except Exception as e:
        current_app.logger.error(f"获取资源详情错误: {str(e)}")
        return jsonify({"error": f"获取资源详情失败: {str(e)}"}), 500

@resource_bp.route('/<resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """更新资源信息"""
    try:
        # 解析请求数据
        data = request.json
        
        # 更新资源
        resource_model = get_resource_model()
        success = resource_model.update_resource(resource_id, data)
        
        if not success:
            return jsonify({"error": "资源更新失败，可能资源不存在"}), 400
            
        return jsonify({
            "success": True,
            "message": "资源更新成功"
        })
        
    except Exception as e:
        current_app.logger.error(f"更新资源错误: {str(e)}")
        return jsonify({"error": f"更新资源失败: {str(e)}"}), 500

@resource_bp.route('/<resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """删除资源"""
    try:
        # 删除资源
        resource_model = get_resource_model()
        success = resource_model.delete_resource(resource_id)
        
        if not success:
            return jsonify({"error": "资源删除失败，可能资源不存在"}), 400
            
        return jsonify({
            "success": True,
            "message": "资源删除成功"
        })
        
    except Exception as e:
        current_app.logger.error(f"删除资源错误: {str(e)}")
        return jsonify({"error": f"删除资源失败: {str(e)}"}), 500

@resource_bp.route('/search', methods=['GET'])
def search_resources():
    """搜索资源"""
    try:
        # 获取请求参数
        query = request.args.get('query', '')
        resource_type = request.args.get('type')
        tags = request.args.getlist('tags')
        teacher_id = request.args.get('teacher_id')
        class_id = request.args.get('class_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 构建过滤条件
        filters = {}
        if resource_type:
            filters['type'] = resource_type
        if tags:
            filters['tags'] = tags
        if teacher_id:
            filters['teacher_id'] = teacher_id
        if class_id:
            filters['class_id'] = class_id
            
        # 搜索资源
        resource_model = get_resource_model()
        result = resource_model.search_resources(query, filters, page, page_size)
        
        return jsonify({
            "success": True,
            **result
        })
        
    except Exception as e:
        current_app.logger.error(f"搜索资源错误: {str(e)}")
        return jsonify({"error": f"搜索资源失败: {str(e)}"}), 500

@resource_bp.route('/teacher/<teacher_id>', methods=['GET'])
def get_teacher_resources(teacher_id):
    """获取教师的资源"""
    try:
        # 获取请求参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 获取教师资源
        resource_model = get_resource_model()
        result = resource_model.get_teacher_resources(teacher_id, page, page_size)
        
        return jsonify({
            "success": True,
            **result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取教师资源错误: {str(e)}")
        return jsonify({"error": f"获取教师资源失败: {str(e)}"}), 500

@resource_bp.route('/class/<class_id>', methods=['GET'])
def get_class_resources(class_id):
    """获取班级的资源"""
    try:
        # 获取请求参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 获取班级资源
        resource_model = get_resource_model()
        result = resource_model.get_class_resources(class_id, page, page_size)
        
        return jsonify({
            "success": True,
            **result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取班级资源错误: {str(e)}")
        return jsonify({"error": f"获取班级资源失败: {str(e)}"}), 500 