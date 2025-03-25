# 师生互动系统

这是一个基于Flask和MongoDB的师生互动系统，旨在提升课堂互动体验和教学反馈收集效率。系统支持实时问答、投票、讨论等功能，为师生之间的交流提供便捷的平台。

## 功能特点

- **用户管理**：支持教师和学生两种角色的注册、登录和权限管理
- **实时互动**：课堂实时问答、投票和小组讨论
- **教学反馈**：学生可提交课程反馈，教师可查看反馈统计
- **数据分析**：为教师提供互动和反馈数据的统计分析
- **演示模式**：支持无数据库的演示模式，便于快速体验系统功能

## 技术栈

- **后端**：Python 3.8+ + Flask 2.2.3
- **数据库**：MongoDB 4.4+
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5
- **实时通信**：Socket.IO
- **认证**：JWT (JSON Web Tokens)

## 系统架构

系统采用MVC架构，分为以下几个部分：

1. **模型层（Models）**：定义数据结构和业务逻辑
   - 用户模型（User）
   - 互动模型（Interaction）
   - 反馈模型（Feedback）

2. **视图层（Views）**：处理用户界面
   - 前端模板（Templates）
   - 静态资源（CSS/JS）

3. **控制器层（Controllers）**：处理请求和响应
   - Web控制器
   - API路由
   - WebSocket管理

## 项目结构

```
├── src/                  # 源代码目录
│   ├── app.py            # 应用入口
│   ├── api/              # API接口
│   │   ├── auth_routes.py       # 认证相关API
│   │   ├── interaction_routes.py # 互动功能API
│   │   └── feedback_routes.py   # 反馈功能API
│   ├── models/           # 数据模型
│   │   ├── user.py              # 用户模型
│   │   ├── interaction.py       # 互动模型
│   │   └── feedback.py          # 反馈模型
│   ├── controllers/      # 控制器
│   │   └── web_controller.py    # Web页面控制器
│   ├── services/         # 业务逻辑服务
│   └── utils/            # 工具类
│       └── socket_manager.py    # WebSocket管理器
├── static/               # 静态资源
│   ├── css/              # 样式表
│   │   └── style.css     # 主样式表
│   └── js/               # JavaScript文件
│       └── main.js       # 主JS逻辑
├── templates/            # 前端模板
│   ├── index.html        # 主页模板
│   ├── student/          # 学生相关页面
│   │   └── dashboard.html # 学生仪表盘
│   └── teacher/          # 教师相关页面
│       └── dashboard.html # 教师仪表盘
├── tests/                # 测试目录
├── .env                  # 环境变量配置
├── requirements.txt      # 项目依赖
└── README.md             # 项目文档
```

## 安装和运行

### 前提条件

- Python 3.8+
- MongoDB 4.4+ (若使用演示模式则不需要)
- pip (Python包管理器)

### 安装步骤

1. 克隆或下载项目代码
   ```
   git clone https://github.com/yourusername/teacher-student-interaction.git
   cd teacher-student-interaction
   ```

2. 创建并激活虚拟环境（可选但推荐）
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

4. 配置环境变量
   - 复制`.env.example`为`.env`（如果没有则创建`.env`文件）
   - 修改以下配置：
     ```
     FLASK_APP=src/app.py
     FLASK_ENV=development
     MONGO_URI=mongodb://localhost:27017/teacher_student_interaction
     SECRET_KEY=your_secret_key_here
     ```

5. 启动MongoDB（可选，若使用演示模式则不需要）
   ```
   # Windows
   "C:\Program Files\MongoDB\Server\4.4\bin\mongod.exe" --dbpath="C:\data\db"
   # macOS/Linux
   mongod --dbpath /var/lib/mongodb
   ```

6. 运行应用
   ```
   python src/app.py
   ```

7. 访问应用
   在浏览器中打开 http://localhost:5000

## 使用说明

### 演示模式

系统默认以演示模式启动（未连接数据库时自动启用），可以使用任意用户名和密码登录，但数据不会被保存。

### 用户注册/登录

1. 访问首页，点击"注册"按钮
2. 填写用户信息，选择角色（学生/教师）
3. 完成注册后使用用户名和密码登录
4. 系统将根据角色重定向到相应的仪表盘

### 学生功能

- 提交问题给教师
- 参与课堂投票
- 加入讨论组
- 提交课程反馈

### 教师功能

- 回答学生问题
- 创建课堂投票
- 管理讨论主题
- 查看反馈统计

## 特别说明

- **数据库连接**：系统会自动检测MongoDB连接状态，若连接失败则启用演示模式
- **安全性**：生产环境中请修改SECRET_KEY，并禁用调试模式
- **浏览器兼容性**：推荐使用Chrome、Firefox、Edge等现代浏览器

## 开发计划

- [ ] 添加课堂签到功能
- [ ] 实现教学资料共享
- [ ] 集成在线考试模块
- [ ] 支持移动端界面适配

## 贡献指南

欢迎贡献代码或提出建议，请遵循以下步骤：

1. Fork本仓库
2. 创建分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request
