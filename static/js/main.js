/**
 * 师生互动系统 - 前端JS脚本
 */

// 全局变量
const API_BASE_URL = '/api';
let currentUser = null;
let socket = null;

// DOM 元素加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    
    // 初始化基本UI元素
    initUI();
    
    // 初始化工具提示和弹出框
    initTooltips();
    
    // 检查登录状态
    checkLoginStatus();
    
    // 根据当前页面初始化特定功能
    initPageSpecificFunctions();
    
    // 初始化表单处理
    initForms();
    
    // 初始化Ajax调用
    initAjaxCalls();
    
    // 获取当前页面路径
    const currentPath = window.location.pathname;
    
    // 根据当前页面路径初始化相应功能
    if (currentPath.includes('/student/dashboard')) {
        // 学生仪表盘页面
        initInteractions();
        loadDashboardData();
    } else if (currentPath.includes('/teacher/dashboard')) {
        // 教师仪表盘页面
        initInteractions();
        loadDashboardData();
    } else if (currentPath.includes('/news')) {
        // 新闻页面
        loadNewsData();
    } else if (currentPath.includes('/resources')) {
        // 资源页面
        initResourcesPage();
    } else if (currentPath === '/' || currentPath.includes('/login')) {
        // 主页或登录页
        initLoginPage();
    }
    
    // 处理注销
    var logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            console.log('用户注销');
            logout();
        });
    }
    
    // 在仪表板页面显示用户信息
    var currentUserData = localStorage.getItem('userData');
    if (currentUserData) {
        var currentUser = JSON.parse(currentUserData);
        console.log('当前登录用户: ', currentUser);
        
        // 显示用户名
        var userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = currentUser.name || '用户';
        }
        
        // 切换登录/未登录状态的UI元素
        document.querySelectorAll('.guest-controls').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.user-controls').forEach(el => el.style.display = 'block');
        
        // 设置用户信息
        var userInfoElement = document.getElementById('userInfo');
        if (userInfoElement) {
            userInfoElement.textContent = currentUser.name;
        }
    } else {
        // 未登录状态UI
        document.querySelectorAll('.guest-controls').forEach(el => el.style.display = 'block');
        document.querySelectorAll('.user-controls').forEach(el => el.style.display = 'none');
    }
    
    // 登录表单提交处理
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('找到登录表单，绑定提交事件');
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            login();
        });
    }
    
    console.log('JS初始化完成');
});

/**
 * 根据当前路径初始化特定的页面功能
 */
function initPageSpecificFunctions() {
    const path = window.location.pathname;
    console.log('当前路径:', path);
    
    // 学生仪表盘
    if (path.includes('/student/dashboard')) {
        console.log('初始化学生仪表盘');
        initStudentDashboard();
    }
    
    // 教师仪表盘
    if (path.includes('/teacher/dashboard')) {
        console.log('初始化教师仪表盘');
        initTeacherDashboard();
    }
    
    // 分析页面
    if (path.includes('/analytics')) {
        console.log('初始化分析页面');
        initAnalyticsPage();
    }
    
    // 资源页面
    if (path.includes('/resources')) {
        console.log('初始化资源页面');
        initResourcesPage();
    }
    
    // 新闻页面
    if (path.includes('/news')) {
        console.log('初始化新闻页面');
        initNewsPage();
    }
}

/**
 * 初始化学生仪表盘页面
 */
function initStudentDashboard() {
    console.log('初始化学生仪表盘功能');
    
    // 提问按钮
    const askQuestionBtn = document.getElementById('ask-question-btn');
    if (askQuestionBtn) {
        askQuestionBtn.addEventListener('click', function() {
            showQuestionForm();
        });
    }
    
    // 提交问题按钮
    const submitQuestionBtn = document.getElementById('submit-question');
    if (submitQuestionBtn) {
        submitQuestionBtn.addEventListener('click', submitQuestion);
    }
    
    // 投票表单提交
    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        console.log('找到投票表单，添加提交事件监听器');
        voteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('投票表单提交触发');
            submitVote();
        });
    } else {
        console.warn('未找到投票表单');
    }
    
    // 反馈按钮
    const feedbackBtn = document.getElementById('submit-feedback-btn');
    if (feedbackBtn) {
        feedbackBtn.addEventListener('click', function() {
            showFeedbackForm();
        });
    }
    
    // 反馈提交按钮
    const submitFeedbackBtn = document.getElementById('submit-feedback');
    if (submitFeedbackBtn) {
        submitFeedbackBtn.addEventListener('click', submitFeedback);
    }
    
    // 问题补充按钮
    const answerBtns = document.querySelectorAll('.answer-btn');
    answerBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question-id');
            showQuestionForm(questionId);
        });
    });
    
    // 加载最近问题
    loadRecentQuestions();
    
    // 加载活跃投票
    loadActivePolls();
    
    // 加载通知
    loadNotifications();
}

/**
 * 初始化登录页面
 */
function initLoginPage() {
    console.log('初始化登录页面');
    
    // 获取登录表单
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('找到登录表单，添加提交事件');
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('登录表单提交');
            login();
        });
    } else {
        console.warn('未找到登录表单');
    }
    
    // 获取注册表单
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        console.log('找到注册表单，添加提交事件');
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('注册表单提交');
            register();
        });
    } else {
        console.warn('未找到注册表单');
    }
    
    // 角色切换事件（如果有的话）
    const roleRadios = document.querySelectorAll('input[name="registerRole"]');
    roleRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const studentFields = document.querySelectorAll('.student-field');
            if (this.value === 'student') {
                studentFields.forEach(field => field.style.display = 'block');
            } else {
                studentFields.forEach(field => field.style.display = 'none');
            }
        });
    });
}

/**
 * 重定向到仪表盘
 */
function redirectToDashboard(role) {
    if (role === 'teacher') {
        window.location.href = '/teacher/dashboard';
    } else {
        window.location.href = '/student/dashboard';
    }
}

// 登录函数
function login() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var role = document.querySelector('input[name="role"]:checked') ? document.querySelector('input[name="role"]:checked').value : 'student';
    
    if (!username || !password) {
        showMessage('请输入用户名和密码', 'error');
        return;
    }

    console.log('尝试登录:', username, '角色:', role);

    // 发送登录请求
    fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        console.log('登录响应状态:', response.status);
        if (!response.ok) {
            throw new Error('登录失败，状态码: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('登录响应完整数据:', data);
        
        // 存储用户信息和认证令牌
        localStorage.setItem('token', data.token);
        console.log('令牌已保存到localStorage');
        
        // 格式化并保存用户数据，使用后端返回的角色
        const userData = {
            id: data.user.id,
            username: data.user.username,
            role: data.user.role,
            name: data.user.name || data.user.username
        };
        
        console.log('准备保存到localStorage的用户数据:', userData);
        const userDataString = JSON.stringify(userData);
        console.log('JSON字符串化的用户数据:', userDataString);
        
        localStorage.setItem('userData', userDataString);
        console.log('用户数据已保存到localStorage');
        
        // 获取保存后的数据，进行验证
        const savedData = localStorage.getItem('userData');
        console.log('验证：从localStorage中读取的userData:', savedData);
        try {
            const parsedData = JSON.parse(savedData);
            console.log('验证：解析后的用户数据:', parsedData);
        } catch(e) {
            console.error('验证：解析用户数据出错:', e);
        }
        
        // 根据用户角色重定向到相应页面
        if (userData.role === 'teacher') {
            console.log('用户是教师，重定向到教师仪表盘');
            window.location.href = '/teacher/dashboard';
        } else if (userData.role === 'student') {
            console.log('用户是学生，重定向到学生仪表盘');
            window.location.href = '/student/dashboard';
        } else {
            console.log('未知角色，重定向到首页');
            window.location.href = '/';
        }
    })
    .catch(error => {
        console.error('登录错误:', error);
        showMessage('登录失败，请检查用户名和密码', 'error');
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
        if(response.data.message) {
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
        showMessage("注册请求失败: " + (error.response?.data?.message || "未知错误"), "error");
    });
}

// 注销函数
function logout() {
    localStorage.removeItem('userData');
    localStorage.removeItem('authToken');
    window.location.href = '/';
}

// 检查登录状态
function checkLoginStatus() {
    console.log('检查登录状态');
    const token = localStorage.getItem('authToken');
    
    if (token) {
        axios.get('/api/auth/me')
            .then(response => {
                console.log('获取用户信息成功:', response.data);
                
                // 保存用户信息
                const userData = response.data;
                localStorage.setItem('userData', JSON.stringify(userData));
                
                // 更新UI
                updateUIByLoginStatus(true, userData);
                
                // 如果在登录页并已登录，重定向到相应的仪表盘
                if (window.location.pathname === '/login' || window.location.pathname === '/') {
                    redirectToDashboard(userData.role);
                }
            })
            .catch(error => {
                console.error('获取用户信息失败:', error);
                localStorage.removeItem('authToken');
                localStorage.removeItem('userData');
                updateUIByLoginStatus(false);
                
                // 如果不在登录页并未登录，重定向到登录页
                if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
                    window.location.href = '/login';
                }
            });
    } else {
        console.log('未找到认证令牌');
        updateUIByLoginStatus(false);
        
        // 如果不在登录页并未登录，重定向到登录页
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
            window.location.href = '/login';
        }
    }
}

// 根据登录状态更新UI
function updateUIByLoginStatus(isLoggedIn, userData = null) {
    console.log('根据登录状态更新UI:', isLoggedIn, userData);
    
    const loginNavItem = document.getElementById('loginNavItem');
    const userDropdown = document.getElementById('userDropdown');
    const userAvatar = document.getElementById('userAvatar');
    const userDisplayName = document.getElementById('userDisplayName');
    
    if (isLoggedIn && userData) {
        // 隐藏登录按钮，显示用户下拉菜单
        if (loginNavItem) loginNavItem.style.display = 'none';
        if (userDropdown) userDropdown.style.display = 'block';
        
        // 更新用户信息
        if (userDisplayName) userDisplayName.textContent = userData.name || userData.username;
        if (userAvatar) {
            if (userData.avatar) {
                userAvatar.src = userData.avatar;
            } else {
                userAvatar.src = '/static/img/placeholder.png';
            }
        }
    } else {
        // 显示登录按钮，隐藏用户下拉菜单
        if (loginNavItem) loginNavItem.style.display = 'block';
        if (userDropdown) userDropdown.style.display = 'none';
    }
}

// 显示消息提示
function showMessage(message, type = 'info') {
    console.log(`显示消息: ${message}, 类型: ${type}`);
    
    const messageContainer = document.getElementById('messageContainer');
    if (!messageContainer) {
        console.error('未找到消息容器');
        return;
    }
    
    const alertClass = type === 'error' ? 'danger' : type;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alertElement.role = 'alert';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    messageContainer.appendChild(alertElement);
    
    // 5秒后自动关闭
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => {
            alertElement.remove();
        }, 150);
    }, 5000);
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

/**
 * 初始化页面交互元素
 */
function initInteractions() {
    console.log('初始化页面交互');
    
    // 导航栏交互
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 如果链接没有href属性或是#，则阻止默认行为
            if (!this.getAttribute('href') || this.getAttribute('href') === '#') {
                e.preventDefault();
                showMessage("该功能暂未实现", "info");
            }
        });
    });
    
    // 投票按钮交互
    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        console.log('找到投票表单，绑定提交事件');
        voteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('投票表单提交');
            submitVote();
        });
    } else {
        console.warn('未找到投票表单');
    }
    
    // 提问按钮
    const askQuestionBtn = document.getElementById('ask-question-btn');
    if (askQuestionBtn) {
        askQuestionBtn.addEventListener('click', function() {
            console.log('点击提问按钮');
            showQuestionForm();
        });
    }
    
    // 提交问题按钮
    const submitQuestionBtn = document.getElementById('submit-question');
    if (submitQuestionBtn) {
        submitQuestionBtn.addEventListener('click', function() {
            console.log('点击提交问题按钮');
            submitQuestion();
        });
    }
    
    // 反馈按钮
    const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
    if (submitFeedbackBtn) {
        submitFeedbackBtn.addEventListener('click', function() {
            console.log('点击反馈按钮');
            showFeedbackForm();
        });
    }
    
    // 提交反馈按钮
    const submitFeedbackActionBtn = document.getElementById('submit-feedback');
    if (submitFeedbackActionBtn) {
        submitFeedbackActionBtn.addEventListener('click', function() {
            console.log('点击提交反馈按钮');
            submitFeedback();
        });
    }
}

/**
 * 初始化表单处理
 */
function initForms() {
    console.log('初始化表单');
    
    // 通用表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.id !== 'loginForm' && form.id !== 'registerForm' && form.id !== 'vote-form') {
            form.addEventListener('submit', function(e) {
                // 阻止表单提交
                e.preventDefault();
                console.log('普通表单提交:', form.id);
                showMessage('表单提交成功', 'success');
            });
        }
    });
}

/**
 * 初始化Ajax调用
 */
function initAjaxCalls() {
    // 设置全局AJAX错误处理
    axios.interceptors.response.use(
        response => response,
        error => {
            console.error('AJAX请求失败:', error);
            
            // 显示错误消息
            const errorMessage = error.response?.data?.message || '请求失败，请稍后再试';
            showMessage(errorMessage, 'error');
            
            return Promise.reject(error);
        }
    );
    
    // 设置请求拦截器，自动添加token
    axios.interceptors.request.use(config => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    }, error => {
        return Promise.reject(error);
    });
}

/**
 * 加载仪表板数据
 */
function loadDashboardData() {
    console.log('加载仪表盘数据');
    
    // 获取当前用户信息
    const userDataJson = localStorage.getItem('userData');
    if (!userDataJson) {
        console.error('未找到用户信息，重定向到登录页');
        window.location.href = '/';
        return;
    }
    
    const userData = JSON.parse(userDataJson);
    console.log('当前用户:', userData);
    
    // 更新用户名显示
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = userData.name || userData.username || '用户';
    }
    
    // 获取课程信息
    axios.get('/api/courses/current')
        .then(response => {
            updateCourseInfo(response.data.courses);
        })
        .catch(error => {
            console.error('获取课程信息失败:', error);
            // 使用静态数据替代
            const staticCourses = [
                { id: 1, name: '物理学', status: 'active', time: '周一 10:00-12:00' },
                { id: 2, name: '数学', status: 'upcoming', time: '周二 14:00-16:00' },
                { id: 3, name: '化学', status: 'upcoming', time: '周三 08:00-10:00' }
            ];
            updateCourseInfo(staticCourses);
        });
    
    // 获取最近问题
    axios.get('/api/interaction/recent')
        .then(response => {
            updateRecentQuestions(response.data.questions);
        })
        .catch(error => {
            console.error('获取最近问题失败:', error);
            // 使用静态数据
            const staticQuestions = [
                { 
                    id: 1, 
                    text: '如何理解牛顿三定律？', 
                    status: 'answered', 
                    createdAt: new Date(Date.now() - 3 * 60 * 1000),
                    answer: '牛顿三定律是经典力学的基础，包括惯性定律、动量定律和作用力与反作用力定律。'
                },
                { 
                    id: 2, 
                    text: '请问下周考试范围是什么？', 
                    status: 'pending', 
                    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000)
                }
            ];
            updateRecentQuestions(staticQuestions);
        });
    
    // 获取通知
    axios.get('/api/notifications')
        .then(response => {
            updateNotifications(response.data.notifications);
        })
        .catch(error => {
            console.error('获取通知失败:', error);
            // 使用静态数据
            const staticNotifications = [
                { id: 1, text: '下周三物理课将进行小测验，请做好准备。', createdAt: new Date() },
                { id: 2, text: '化学实验报告截止日期延长至下周五。', createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000) }
            ];
            updateNotifications(staticNotifications);
        });
}

/**
 * 加载新闻数据
 */
function loadNewsData() {
    console.log('加载新闻数据');
    
    // 获取最新新闻
    axios.get('/api/news/recent')
        .then(response => {
            updateNewsListing(response.data.news);
        })
        .catch(error => {
            console.error('获取新闻列表失败:', error);
            showMessage('加载新闻失败，请稍后再试', 'error');
        });
    
    // 获取新闻类别
    axios.get('/api/news/categories')
        .catch(error => {
            console.error('获取新闻类别失败:', error);
        });
}

/**
 * 提交投票
 */
function submitVote() {
    console.log('提交投票');
    
    const voteForm = document.getElementById('vote-form');
    if (!voteForm) {
        console.error('未找到投票表单');
        return;
    }
    
    const pollId = voteForm.getAttribute('data-poll-id');
    const selectedOption = voteForm.querySelector('input[name="poll-option"]:checked');
    
    if (!selectedOption) {
        showMessage('请选择一个选项', 'error');
        return;
    }
    
    const optionId = selectedOption.value;
    console.log(`投票: 投票ID=${pollId}, 选项ID=${optionId}`);
    
    // 发送投票请求
    axios.post(`/api/interaction/poll/${pollId}/vote`, {
        option: optionId
    })
    .then(response => {
        console.log('投票响应:', response.data);
        showMessage('投票提交成功', 'success');
        
        // 禁用表单，防止重复提交
        voteForm.querySelectorAll('input').forEach(input => {
            input.disabled = true;
        });
        document.getElementById('submit-vote').disabled = true;
    })
    .catch(error => {
        console.error('投票提交错误:', error);
        showMessage('投票提交失败: ' + (error.response?.data?.message || '服务器错误'), 'error');
    });
}

/**
 * 显示提问表单
 */
function showQuestionForm(questionId) {
    console.log('显示提问表单', questionId ? `问题ID: ${questionId}` : '');
    
    // 重置表单
    const questionForm = document.getElementById('question-form');
    if (questionForm) {
        questionForm.reset();
        
        // 如果有问题ID，设置为表单属性
        if (questionId) {
            questionForm.setAttribute('data-question-id', questionId);
        } else {
            questionForm.removeAttribute('data-question-id');
        }
    }
    
    // 设置模态框标题
    const modalTitle = document.getElementById('askQuestionModalLabel');
    if (modalTitle) {
        modalTitle.textContent = questionId ? '补充问题' : '提出问题';
    }
    
    // 显示模态框
    const modal = document.getElementById('ask-question-modal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    } else {
        console.error('未找到提问模态框');
        showMessage('无法打开提问表单', 'error');
    }
}

/**
 * 显示反馈表单
 */
function showFeedbackForm() {
    console.log('显示反馈表单');
    
    // 重置表单
    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.reset();
    }
    
    // 显示模态框
    const modal = document.getElementById('feedback-modal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    } else {
        console.error('未找到反馈模态框');
        showMessage('无法打开反馈表单', 'error');
    }
}

/**
 * 提交问题
 */
function submitQuestion() {
    console.log('提交问题');
    
    const questionText = document.getElementById('question-text').value.trim();
    if (!questionText) {
        showMessage('请输入问题内容', 'error');
        return;
    }
    
    const questionForm = document.getElementById('question-form');
    const courseId = questionForm.getAttribute('data-course-id') || '1'; // 默认课程ID
    const questionId = questionForm.getAttribute('data-question-id'); // 可能为null
    
    // 准备请求数据
    const requestData = {
        course_id: courseId,
        question: questionText
    };
    
    // 如果是补充问题，添加原问题ID
    if (questionId) {
        requestData.parent_question_id = questionId;
    }
    
    // 发送请求
    axios.post('/api/interaction/ask', requestData)
    .then(response => {
        console.log('提问响应:', response.data);
        if (response.data.success) {
            showMessage(questionId ? '问题补充成功' : '问题提交成功', 'success');
            
            // 关闭模态框
            const modal = document.getElementById('ask-question-modal');
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
            
            // 刷新问题列表
            axios.get('/api/interaction/recent')
                .then(response => {
                    updateRecentQuestions(response.data.questions);
                })
                .catch(error => {
                    console.error('刷新问题列表失败:', error);
                });
        } else {
            showMessage(response.data.message || '问题提交失败', 'error');
        }
    })
    .catch(error => {
        console.error('提问错误:', error);
        showMessage('问题提交失败: ' + (error.response?.data?.message || '服务器错误'), 'error');
    });
}

/**
 * 提交反馈
 */
function submitFeedback() {
    console.log('提交反馈');
    
    const feedbackText = document.getElementById('feedback-text').value.trim();
    if (!feedbackText) {
        showMessage('请输入反馈内容', 'error');
        return;
    }
    
    const feedbackForm = document.getElementById('feedback-form');
    const courseId = feedbackForm.getAttribute('data-course-id') || '1'; // 默认课程ID
    
    // 发送请求
    axios.post('/api/interaction/feedback', {
        course_id: courseId,
        feedback: feedbackText
    })
    .then(response => {
        console.log('反馈响应:', response.data);
        if (response.data.success) {
            showMessage('反馈提交成功，谢谢您的宝贵意见！', 'success');
            
            // 关闭模态框
            const modal = document.getElementById('feedback-modal');
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        } else {
            showMessage(response.data.message || '反馈提交失败', 'error');
        }
    })
    .catch(error => {
        console.error('反馈错误:', error);
        showMessage('反馈提交失败: ' + (error.response?.data?.message || '服务器错误'), 'error');
    });
}

/**
 * 更新课程信息显示
 */
function updateCourseInfo(courses) {
    console.log('更新课程信息:', courses);
    
    const coursesContainer = document.querySelector('.current-courses');
    if (!coursesContainer) {
        console.warn('未找到课程容器');
        return;
    }
    
    // 清空容器
    coursesContainer.innerHTML = '';
    
    // 添加课程项
    courses.forEach(course => {
        const courseItem = document.createElement('div');
        courseItem.className = 'course-item';
        
        const statusClass = course.status === 'active' ? 'badge-success' : 'badge-secondary';
        const statusText = course.status === 'active' ? '进行中' : course.time || '即将开始';
        
        courseItem.innerHTML = `
            <div class="course-name">${course.name}</div>
            <div class="course-meta">
                <span class="badge ${statusClass}">${statusText}</span>
            </div>
        `;
        
        coursesContainer.appendChild(courseItem);
    });
    
    // 如果没有课程，显示提示
    if (courses.length === 0) {
        coursesContainer.innerHTML = '<div class="text-center py-3 text-muted">暂无课程</div>';
    }
}

/**
 * 更新最近问题显示
 */
function updateRecentQuestions(questions) {
    console.log('更新最近问题:', questions);
    
    const questionsContainer = document.querySelector('.recent-questions');
    if (!questionsContainer) {
        console.warn('未找到问题容器');
        return;
    }
    
    // 清空容器
    questionsContainer.innerHTML = '';
    
    // 添加问题项
    questions.forEach(question => {
        const questionItem = createQuestionElement(question);
        questionsContainer.appendChild(questionItem);
    });
    
    // 如果没有问题，显示提示
    if (questions.length === 0) {
        questionsContainer.innerHTML = '<div class="text-center py-3 text-muted">暂无问题</div>';
    }
}

/**
 * 创建问题元素
 */
function createQuestionElement(question) {
    const questionItem = document.createElement('div');
    questionItem.className = 'question-item';
    
    const statusClass = question.status === 'answered' ? 'badge-success' : 'badge-secondary';
    const statusText = question.status === 'answered' ? '已回答' : '待回答';
    
    const timeAgo = formatTimeAgo(question.createdAt);
    
    let html = `
        <div class="question-text">${question.text}</div>
        <div class="question-meta">
            <span class="badge ${statusClass}">${statusText}</span>
            <span class="time-ago">${timeAgo}</span>
        </div>
    `;
    
    // 如果问题已回答，显示回答内容
    if (question.status === 'answered' && question.answer) {
        html += `
            <div class="answer mt-2">
                <div class="answer-label">回答:</div>
                <div class="answer-text">${question.answer}</div>
            </div>
        `;
    } else {
        // 否则显示补充问题按钮
        html += `
            <button class="btn btn-sm btn-outline-primary answer-btn mt-2" data-question-id="${question.id}">
                补充问题
            </button>
        `;
    }
    
    questionItem.innerHTML = html;
    
    // 绑定补充问题按钮事件
    const answerBtn = questionItem.querySelector('.answer-btn');
    if (answerBtn) {
        answerBtn.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question-id');
            showQuestionForm(questionId);
        });
    }
    
    return questionItem;
}

/**
 * 更新通知显示
 */
function updateNotifications(notifications) {
    console.log('更新通知:', notifications);
    
    const notificationsContainer = document.querySelector('.recent-notifications');
    if (!notificationsContainer) {
        console.warn('未找到通知容器');
        return;
    }
    
    // 清空容器
    notificationsContainer.innerHTML = '';
    
    // 添加通知项
    notifications.forEach(notification => {
        const notificationItem = document.createElement('div');
        notificationItem.className = 'notification-item';
        
        const timeAgo = formatTimeAgo(notification.createdAt);
        
        notificationItem.innerHTML = `
            <div class="notification-text">${notification.text}</div>
            <div class="notification-meta">
                <span class="time-ago">${timeAgo}</span>
            </div>
        `;
        
        notificationsContainer.appendChild(notificationItem);
    });
    
    // 如果没有通知，显示提示
    if (notifications.length === 0) {
        notificationsContainer.innerHTML = '<div class="text-center py-3 text-muted">暂无通知</div>';
    }
}

/**
 * 更新新闻列表显示
 */
function updateNewsListing(newsList) {
    console.log('更新新闻列表:', newsList);
    
    const newsListContainer = document.getElementById('news-list');
    if (!newsListContainer) {
        console.warn('未找到新闻列表容器');
        return;
    }
    
    if (!newsList || !newsList.length) {
        newsListContainer.innerHTML = '<div class="alert alert-info">没有找到相关新闻</div>';
        return;
    }
    
    let html = '';
    newsList.forEach(news => {
        html += `
        <div class="news-item">
          <div class="title">
            <a href="${news.url || '#'}" target="_blank">${news.title}</a>
          </div>
          <div class="summary">${news.summary}</div>
          <div class="meta">
            <div>
              <span class="category-badge category-${news.category}">${news.category}</span>
              <span class="source">${news.source}</span>
            </div>
            <div class="time">${formatTimeAgo(news.published_at || news.publishedAt)}</div>
          </div>
        </div>
        `;
    });
    
    newsListContainer.innerHTML = html;
}

/**
 * 更新新闻分类显示
 */
function updateNewsCategories(categories) {
    console.log('更新新闻分类:', categories);
    
    const statsContainer = document.getElementById('category-stats');
    if (!statsContainer) {
        console.warn('未找到分类统计容器');
        return;
    }
    
    if (!categories || !categories.length) {
        statsContainer.innerHTML = '<p>暂无分类数据</p>';
        return;
    }
    
    let html = '';
    categories.forEach(category => {
        html += `
        <div class="mb-2">
          <span class="category-badge category-${category}">${category}</span>
        </div>
        `;
    });
    
    statsContainer.innerHTML = html;
}

/**
 * 格式化时间显示
 */
function formatTimeAgo(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) {
        return '刚刚';
    } else if (diffMin < 60) {
        return `${diffMin}分钟前`;
    } else if (diffHour < 24) {
        return `${diffHour}小时前`;
    } else if (diffDay === 1) {
        return '昨天';
    } else if (diffDay < 7) {
        return `${diffDay}天前`;
    } else {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${year}-${month < 10 ? '0' + month : month}-${day < 10 ? '0' + day : day}`;
    }
}

/**
 * 加载最近问题
 */
function loadRecentQuestions() {
    console.log('加载最近问题');
    
    axios.get('/api/interaction/recent-questions')
    .then(response => {
        console.log('获取最近问题成功:', response.data);
        updateRecentQuestions(response.data);
    })
    .catch(error => {
        console.error('获取最近问题失败:', error);
        // 使用静态数据作为后备
        const staticQuestions = [
            {
                id: '1',
                content: '如何理解牛顿三定律？',
                status: 'answered',
                time: '3分钟前',
                answer: '请解释一下作用力与反作用力的概念，谢谢老师。'
            },
            {
                id: '2',
                content: '请问下周考试范围是什么？',
                status: 'pending',
                time: '昨天'
            }
        ];
        updateRecentQuestions(staticQuestions);
    });
}

/**
 * 加载活跃投票
 */
function loadActivePolls() {
    console.log('加载活跃投票');
    
    axios.get('/api/interaction/active-polls')
    .then(response => {
        console.log('获取活跃投票成功:', response.data);
        updateActivePolls(response.data);
    })
    .catch(error => {
        console.error('获取活跃投票失败:', error);
        // 静态数据作为后备
        const staticPoll = {
            id: '1',
            title: '你最喜欢的学习方式是？',
            options: [
                { id: '1', text: '课堂讲解' },
                { id: '2', text: '小组讨论' },
                { id: '3', text: '实验操作' },
                { id: '4', text: '自主学习' }
            ]
        };
        updateActivePolls([staticPoll]);
    });
}

/**
 * 加载通知
 */
function loadNotifications() {
    console.log('加载通知');
    
    axios.get('/api/user/notifications')
    .then(response => {
        console.log('获取通知成功:', response.data);
        updateNotifications(response.data);
    })
    .catch(error => {
        console.error('获取通知失败:', error);
        // 静态数据作为后备
        const staticNotifications = [
            {
                id: '1',
                content: '下周三物理课将进行小测验，请做好准备。',
                time: '刚刚'
            },
            {
                id: '2',
                content: '化学实验报告截止日期延长至下周五。',
                time: '2小时前'
            }
        ];
        updateNotifications(staticNotifications);
    });
}

/**
 * 更新最近问题显示
 */
function updateRecentQuestions(questions) {
    const container = document.querySelector('.recent-questions');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (questions && questions.length > 0) {
        questions.forEach(question => {
            const statusClass = question.status === 'answered' ? 'success' : 'secondary';
            const statusText = question.status === 'answered' ? '已回答' : '待回答';
            
            let html = `
                <div class="question-item">
                    <div class="question-text">${question.content}</div>
                    <div class="question-meta">
                        <span class="badge badge-${statusClass}">${statusText}</span>
                        <span class="time-ago">${question.time}</span>
                    </div>
            `;
            
            if (question.status === 'answered' && question.answer) {
                html += `
                    <div class="answer mt-2">
                        <div class="answer-label">回答:</div>
                        <div class="answer-text">${question.answer}</div>
                    </div>
                `;
            } else {
                html += `
                    <button class="btn btn-sm btn-outline-primary answer-btn mt-2" data-question-id="${question.id}">
                        补充问题
                    </button>
                `;
            }
            
            html += `</div>`;
            
            container.innerHTML += html;
        });
        
        // 重新绑定补充问题按钮
        const answerBtns = container.querySelectorAll('.answer-btn');
        answerBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const questionId = this.getAttribute('data-question-id');
                showQuestionForm(questionId);
            });
        });
    } else {
        container.innerHTML = '<div class="text-center py-3">暂无问题</div>';
    }
}

/**
 * 更新活跃投票显示
 */
function updateActivePolls(polls) {
    const container = document.querySelector('.active-poll');
    if (!container) return;
    
    if (polls && polls.length > 0) {
        const poll = polls[0]; // 暂时只显示第一个投票
        
        const voteForm = document.getElementById('vote-form') || container.querySelector('form');
        if (voteForm) {
            voteForm.setAttribute('data-poll-id', poll.id);
            
            const pollQuestion = container.querySelector('.poll-question strong');
            if (pollQuestion) {
                pollQuestion.textContent = poll.title;
            }
            
            const optionsContainer = voteForm.querySelector('.voting-options');
            if (optionsContainer) {
                optionsContainer.innerHTML = '';
                
                poll.options.forEach((option, index) => {
                    const optionHtml = `
                        <div class="voting-option">
                            <input type="radio" name="poll-option" id="option${index+1}" value="${option.id}" class="d-none">
                            <label for="option${index+1}" class="option-label">${option.text}</label>
                        </div>
                    `;
                    optionsContainer.innerHTML += optionHtml;
                });
            }
        }
    } else {
        container.innerHTML = '<div class="text-center py-3">暂无活跃投票</div>';
    }
}

/**
 * 更新通知显示
 */
function updateNotifications(notifications) {
    const container = document.querySelector('.recent-notifications');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (notifications && notifications.length > 0) {
        notifications.forEach(notification => {
            const notificationHtml = `
                <div class="notification-item">
                    <div class="notification-text">${notification.content}</div>
                    <div class="notification-meta">
                        <span class="time-ago">${notification.time}</span>
                    </div>
                </div>
            `;
            container.innerHTML += notificationHtml;
        });
    } else {
        container.innerHTML = '<div class="text-center py-3">暂无通知</div>';
    }
}

/**
 * 初始化基本UI元素
 */
function initUI() {
    console.log('初始化UI元素');
    
    // 初始化登录和注册按钮
    const loginButtons = document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target="#loginModal"]');
    loginButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('点击登录按钮');
        });
    });
    
    const registerButtons = document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target="#registerModal"]');
    registerButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('点击注册按钮');
        });
    });
    
    // 初始化登出按钮
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            console.log('点击登出按钮');
            logout();
        });
    }
}

/**
 * 初始化工具提示和弹出框
 */
function initTooltips() {
    // 初始化Bootstrap工具提示
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
} 