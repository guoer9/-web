import os
from src import create_app

# 设置环境变量
os.environ['FLASK_APP'] = 'run.py'
os.environ['FLASK_ENV'] = 'development'

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 