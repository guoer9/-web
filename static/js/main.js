/**
 * 师生互动系统 - 前端JS脚本
 * 简化版本，用于演示模式
 */

// 全局变量
let currentUser = null;
let socket = null;
const DEMO_MODE = true; // 设置为演示模式

// DOM 元素加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    
    // 获取登录表单
    var loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('提交登录表单');
            
            // 获取用户名和密码
            var username = document.getElementById('username').value;
            var password = document.getElementById('password').value;
            var role = document.getElementById('loginRoleInput').value || 'student';
            
            // 在演示模式下，直接"登录成功"
            console.log('演示模式登录: ' + username + ', 角色: ' + role);
            
            // 创建一个用户对象并保存到本地存储
            var user = {
                name: username,
                username: username,
                role: role
            };
            
            localStorage.setItem('currentUser', JSON.stringify(user));
            console.log('用户信息已保存到本地存储');
            
            // 重定向到对应的仪表板
            var dashboardUrl = role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard';
            console.log('准备重定向到: ' + dashboardUrl);
            
            // 直接进行页面跳转
            window.location.href = dashboardUrl;
        });
    }
    
    // 获取注册表单
    var registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('提交注册表单');
            
            // 简单的验证
            var name = document.getElementById('registerName').value;
            var username = document.getElementById('registerUsername').value;
            var password = document.getElementById('registerPassword').value;
            var confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                alert('两次输入的密码不一致');
                return;
            }
            
            // 注册成功，显示提示并返回登录页
            alert('注册成功，请登录');
            
            // 关闭注册模态框，打开登录模态框
            var registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            if (registerModal) {
                registerModal.hide();
                
                // 预填充用户名
                document.getElementById('username').value = username;
                
                // 显示登录模态框
                setTimeout(function() {
                    var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                    loginModal.show();
                }, 500);
            }
        });
    }
    
    // 处理注销
    var logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            console.log('用户注销');
            localStorage.removeItem('currentUser');
            window.location.href = '/';
        });
    }
    
    // 在仪表板页面显示用户信息
    var currentUserData = localStorage.getItem('currentUser');
    if (currentUserData) {
        var currentUser = JSON.parse(currentUserData);
        console.log('当前登录用户: ', currentUser);
        
        // 显示用户名
        var userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = currentUser.name || '用户';
        }
    }
    
    console.log('JS初始化完成');
});

// 登录函数
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('loginRoleInput').value || 'student';
    
    if(!username || !password) {
        showMessage("请输入用户名和密码", "error");
        return;
    }
    
    // 演示模式下，直接通过登录
    if(DEMO_MODE) {
        console.log("演示模式：直接登录成功");
        
        // 创建模拟用户数据
        const mockUser = {
            _id: "demo_" + Math.random().toString(36).substr(2, 9),
            username: username,
            name: username,  // 在演示模式下，显示名称与用户名相同
            role: role
        };
        
        // 保存用户信息到本地存储
        localStorage.setItem("currentUser", JSON.stringify(mockUser));
        
        // 根据角色重定向到相应的仪表板
        if(role === "teacher") {
            window.location.href = "/teacher/dashboard";
        } else {
            window.location.href = "/student/dashboard";
        }
        
        return;
    }
    
    // 正常模式下的登录逻辑
    axios.post('/api/auth/login', {
        username: username,
        password: password,
        role: role
    })
    .then(response => {
        if(response.data.success) {
            localStorage.setItem("currentUser", JSON.stringify(response.data.user));
            
            if(response.data.user.role === "teacher") {
                window.location.href = "/teacher/dashboard";
            } else {
                window.location.href = "/student/dashboard";
            }
        } else {
            showMessage(response.data.message || "登录失败", "error");
        }
    })
    .catch(error => {
        showMessage("登录请求失败: " + error.response?.data?.message || "未知错误", "error");
    });
}

// 注册函数
function register() {
    const name = document.getElementById('registerName').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const role = document.querySelector('input[name="registerRole"]:checked').value;
    const classId = role === 'student' ? document.getElementById('classId').value : null;
    
    if(!username || !password || !name || !role) {
        showMessage("请填写所有必填字段", "error");
        return;
    }
    
    // 验证密码
    if (password !== confirmPassword) {
        showMessage('两次输入的密码不一致', 'error');
        return;
    }
    
    // 演示模式下模拟注册成功
    if(DEMO_MODE) {
        console.log("演示模式：注册成功，请登录");
        showMessage("注册成功，请登录", "success");
        const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
        registerModal.hide();
        setTimeout(() => {
            document.getElementById('username').value = username;
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            loginModal.show();
        }, 500);
        return;
    }
    
    // 正常注册流程
    const registerData = {
        name: name,
        username: username,
        password: password,
        role: role
    };
    
    if (role === 'student' && classId) {
        registerData.class_id = classId;
    }
    
    axios.post('/api/auth/register', registerData)
    .then(response => {
        if(response.data.success) {
            showMessage("注册成功，请登录", "success");
            const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            registerModal.hide();
            setTimeout(() => {
                document.getElementById('username').value = username;
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            }, 500);
        } else {
            showMessage(response.data.message || "注册失败", "error");
        }
    })
    .catch(error => {
        showMessage("注册请求失败: " + error.response?.data?.message || "未知错误", "error");
    });
}

// 注销函数
function logout() {
    localStorage.removeItem("currentUser");
    window.location.href = "/";
}

// 检查登录状态
function checkLoginStatus() {
    const userJson = localStorage.getItem("currentUser");
    
    if(userJson) {
        try {
            currentUser = JSON.parse(userJson);
            
            // 更新用户显示
            updateUserDisplay();
            
            // 如果在首页，可以自动跳转到仪表板
            if(window.location.pathname === "/") {
                if(currentUser.role === "teacher") {
                    window.location.href = "/teacher/dashboard";
                } else {
                    window.location.href = "/student/dashboard";
                }
            }
            
            console.log("已登录用户: ", currentUser.username);
        } catch(e) {
            console.error("解析用户数据失败", e);
            localStorage.removeItem("currentUser");
        }
    } else {
        // 未登录状态
        console.log("用户未登录");
        
        // 如果访问需要登录的页面，重定向到首页
        const path = window.location.pathname;
        if(path.startsWith("/teacher/") || path.startsWith("/student/")) {
            window.location.href = "/";
        }
    }
}

// 更新用户显示
function updateUserDisplay() {
    if(currentUser) {
        // 显示登录后的用户信息
        document.getElementById('userInfo').textContent = currentUser.name;
        document.querySelector('.user-controls').style.display = 'block';
        document.querySelector('.guest-controls').style.display = 'none';
    } else {
        // 显示游客状态
        document.querySelector('.user-controls').style.display = 'none';
        document.querySelector('.guest-controls').style.display = 'block';
    }
}

// 显示消息提示
function showMessage(message, type = "info") {
    const alertClass = type === "error" ? "alert-danger" : 
                       type === "success" ? "alert-success" : 
                       "alert-info";
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    document.getElementById('messageContainer').innerHTML = alertHtml;
    
    // 3秒后自动消失
    setTimeout(function() {
        document.querySelector('.alert').alert('close');
    }, 3000);
}

// 初始化Socket.IO连接
function initializeSocket(token, userId) {
    socket = io({
        auth: {
            token: token
        }
    });
    
    socket.on('connect', () => {
        console.log('Socket.IO连接成功');
    });
    
    socket.on('disconnect', () => {
        console.log('Socket.IO连接断开');
    });
    
    socket.on('error', (error) => {
        console.error('Socket.IO错误:', error);
    });
}

// 加入房间
function joinRoom(roomId) {
    if (socket) {
        socket.emit('join', { room: roomId });
    }
}

// 离开房间
function leaveRoom(roomId) {
    if (socket) {
        socket.emit('leave', { room: roomId });
    }
}

// 发送消息
function sendMessage(roomId, message) {
    if (socket) {
        socket.emit('message', { room: roomId, message: message });
    }
} 