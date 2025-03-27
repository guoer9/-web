#!/usr/bin/env python3
"""
数据库初始化脚本，用于创建初始用户和测试数据
"""
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_pymongo import PyMongo
from flask import Flask

def init_db():
    """初始化数据库"""
    app = Flask(__name__)
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/jhxt'
    mongo = PyMongo(app)
    
    # 连接测试
    try:
        mongo.db.command('ping')
        print("MongoDB连接成功")
    except Exception as e:
        print(f"MongoDB连接失败: {str(e)}")
        sys.exit(1)
    
    # 创建索引
    mongo.db.users.create_index('username', unique=True)
    
    # 检查是否已存在用户
    if mongo.db.users.count_documents({}) > 0:
        answer = input("数据库中已存在用户。是否清空并重新创建? (y/n): ")
        if answer.lower() == 'y':
            mongo.db.users.delete_many({})
            print("已清空用户集合")
        else:
            print("保留现有用户")
    
    # 创建默认用户
    test_users = [
        {
            'username': 'teacher1',
            'password': generate_password_hash('123456'),
            'name': '教师用户',
            'role': 'teacher',
            'created_at': datetime.utcnow()
        },
        {
            'username': 'student1',
            'password': generate_password_hash('123456'),
            'name': '学生用户',
            'role': 'student',
            'class_id': '1',
            'created_at': datetime.utcnow()
        }
    ]
    
    for user in test_users:
        username = user['username']
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            print(f"用户 {username} 已存在，跳过创建")
        else:
            result = mongo.db.users.insert_one(user)
            if result.inserted_id:
                print(f"创建用户 {username} 成功，ID: {result.inserted_id}")
            else:
                print(f"创建用户 {username} 失败")
    
    print("数据库初始化完成")

if __name__ == '__main__':
    init_db() 