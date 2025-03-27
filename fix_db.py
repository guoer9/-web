#!/usr/bin/env python3
"""
数据库连接修复脚本
自动检测并修复MongoDB连接问题
"""
import os
import sys
import subprocess
import time

def check_mongodb():
    """检查MongoDB是否安装并运行"""
    print("检查MongoDB服务状态...")
    
    # 检查MongoDB是否安装
    try:
        # 尝试使用mongosh连接
        result = subprocess.run(['mongosh', '--eval', 'db.version()', '--quiet'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("MongoDB已安装并可连接")
            return True
    except FileNotFoundError:
        print("未找到MongoDB客户端工具")
    
    # 检查服务状态
    result = subprocess.run(['systemctl', 'status', 'mongodb'], 
                           capture_output=True, text=True)
    
    if result.returncode == 0 and "active (running)" in result.stdout:
        print("MongoDB服务正在运行")
        return True
    else:
        print("MongoDB服务未运行或未安装")
        return False

def install_mongodb():
    """安装并启动MongoDB"""
    print("准备安装MongoDB...")
    choice = input("是否安装MongoDB? (y/n): ")
    if choice.lower() != 'y':
        print("用户取消安装")
        return False
    
    try:
        # 更新软件包列表
        print("更新软件包列表...")
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        
        # 安装MongoDB
        print("安装MongoDB...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'mongodb'], check=True)
        
        # 启动服务
        print("启动MongoDB服务...")
        subprocess.run(['sudo', 'systemctl', 'start', 'mongodb'], check=True)
        
        # 设置开机自启
        print("设置MongoDB开机自启...")
        subprocess.run(['sudo', 'systemctl', 'enable', 'mongodb'], check=True)
        
        # 等待服务启动
        print("等待MongoDB服务启动...")
        time.sleep(3)
        
        return check_mongodb()
    except subprocess.CalledProcessError as e:
        print(f"安装MongoDB失败: {e}")
        return False

def test_db_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    
    try:
        from flask import Flask
        from flask_pymongo import PyMongo
        
        app = Flask(__name__)
        app.config['MONGO_URI'] = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/jhxt'
        mongo = PyMongo(app)
        
        with app.app_context():
            # 测试连接
            mongo.db.command('ping')
            print("数据库连接成功")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("==== 数据库连接修复工具 ====")
    
    # 检查Python依赖
    try:
        import flask_pymongo
        print("Flask-PyMongo已安装")
    except ImportError:
        print("安装Flask-PyMongo...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask-pymongo'], check=True)
    
    # 检查MongoDB状态
    if not check_mongodb():
        if not install_mongodb():
            print("MongoDB安装失败，请手动安装")
            return False
    
    # 测试数据库连接
    if test_db_connection():
        print("数据库连接正常")
        # 运行初始化脚本
        choice = input("是否初始化测试数据? (y/n): ")
        if choice.lower() == 'y':
            try:
                subprocess.run([sys.executable, 'init_db.py'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"初始化数据失败: {e}")
        
        print("数据库修复完成")
        return True
    else:
        print("数据库连接仍然失败，请检查配置")
        return False

if __name__ == '__main__':
    sys.exit(0 if main() else 1) 