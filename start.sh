#!/bin/bash
# 一键启动应用脚本

# 输出带颜色的文本
log_info() {
    echo -e "\033[0;32m[INFO] $1\033[0m"
}

log_error() {
    echo -e "\033[0;31m[ERROR] $1\033[0m"
}

log_warning() {
    echo -e "\033[0;33m[WARNING] $1\033[0m"
}

# 确认MongoDB服务正在运行
check_mongodb() {
    log_info "检查MongoDB服务状态..."
    if systemctl is-active --quiet mongodb; then
        log_info "MongoDB服务正在运行"
        return 0
    else
        log_warning "MongoDB服务未运行"
        log_info "尝试启动MongoDB服务..."
        sudo systemctl start mongodb
        if [ $? -eq 0 ]; then
            log_info "MongoDB服务启动成功"
            return 0
        else
            log_error "MongoDB服务启动失败"
            return 1
        fi
    fi
}

# 检查虚拟环境是否存在
check_venv() {
    if [ -d "venv" ]; then
        log_info "使用现有虚拟环境"
        return 0
    else
        log_info "创建新的虚拟环境..."
        python3 -m venv venv
        if [ $? -eq 0 ]; then
            log_info "虚拟环境创建成功"
            return 0
        else
            log_error "虚拟环境创建失败"
            return 1
        fi
    fi
}

# 安装依赖
install_deps() {
    log_info "安装项目依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        log_info "依赖安装成功"
        return 0
    else
        log_error "依赖安装失败"
        return 1
    fi
}

# 初始化数据库
init_database() {
    log_info "检查是否需要初始化数据库..."
    source venv/bin/activate
    python fix_db.py
    if [ $? -eq 0 ]; then
        log_info "数据库检查/初始化成功"
        return 0
    else
        log_error "数据库检查/初始化失败"
        return 1
    fi
}

# 启动应用
start_app() {
    log_info "启动Flask应用..."
    source venv/bin/activate
    export FLASK_APP=run.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    
    # 在后台运行应用
    python run.py &
    APP_PID=$!
    
    log_info "应用已启动，PID: $APP_PID"
    log_info "在浏览器中访问: http://localhost:5000"
    log_info "按Ctrl+C停止应用"
    
    # 保存PID到文件
    echo $APP_PID > .app.pid
    
    # 等待用户中断
    wait $APP_PID
}

# 清理函数
cleanup() {
    log_info "正在停止应用..."
    if [ -f .app.pid ]; then
        PID=$(cat .app.pid)
        kill $PID 2>/dev/null
        rm .app.pid
    fi
    exit 0
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    log_info "=== 交互系统启动 ==="
    
    check_mongodb || return 1
    check_venv || return 1
    install_deps || return 1
    init_database || return 1
    start_app
    
    return 0
}

# 执行主函数
main
exit $? 