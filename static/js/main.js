/**
 * 师生互动系统 - 前端JS脚本
 */

// 全局变量
const API_BASE_URL = '/api';  // 使用相对路径
let currentUser = null;
let socket = null;

// 工具函数
function showError(message) {
    alert(message);
}

function showSuccess(message) {
    alert(message);
}

// 用户认证相关函数
async function login(username, password) {
    try {
        console.log('尝试登录，用户名:', username);
        
        const data = await API.auth.login(username, password);
        
        if (data.success) {
            // 保存token和用户信息
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            console.log('令牌和用户信息已保存到localStorage');
            
            // 根据用户角色跳转到不同页面
            if (data.user.role === 'teacher') {
                console.log('教师登录成功，跳转到教师仪表板');
                window.location.href = '/teacher/dashboard';
            } else {
                console.log('学生登录成功，跳转到学生仪表板');
                window.location.href = '/student/dashboard';
            }
            
            showSuccess(data.message);
        } else {
            console.error('登录失败:', data.message);
            showError(data.message);
        }
    } catch (error) {
        console.error('登录请求异常:', error);
        showError('登录失败，请稍后重试');
    }
}

async function register(userData) {
    try {
        console.log('尝试注册:', userData);
        
        const data = await API.auth.register(userData);
        
        if (data.success) {
            showSuccess(data.message);
            return true;
        } else {
            console.error('注册失败:', data.message);
            showError(data.message);
            return false;
        }
    } catch (error) {
        console.error('注册请求异常:', error);
        showError('注册失败，请稍后重试');
        return false;
    }
}

async function logout() {
    try {
        console.log('用户登出');
        // 清除本地存储
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        currentUser = null;
        
        // 调用登出API
        await API.auth.logout();
        
        // 跳转到登录页
        window.location.href = '/login';
    } catch (error) {
        console.error('登出异常:', error);
        // 即使API调用失败也清除本地状态并跳转
        window.location.href = '/login';
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 从localStorage获取用户信息
    const userJson = localStorage.getItem('user');
    if (userJson) {
        try {
            currentUser = JSON.parse(userJson);
            console.log('当前登录用户:', currentUser);
        } catch (e) {
            console.error('解析用户信息失败:', e);
            localStorage.removeItem('user');
        }
    }
    
    // 初始化页面
    initPage();
});

// 根据页面路径初始化不同功能
function initPage() {
    const path = window.location.pathname;
    
    // 绑定登出按钮
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // 初始化登录表单
    if (path === '/' || path === '/login') {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                login(username, password);
            });
        }
        
        // 初始化注册表单
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = {
                    username: document.getElementById('registerUsername').value,
                    password: document.getElementById('registerPassword').value,
                    name: document.getElementById('name').value,
                    role: document.getElementById('role').value
                };
                register(formData);
            });
        }
    }
}

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

/**
 * 显示消息提示
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型（success, error, info, warning）
 */
function showMessage(message, type = 'info') {
    console.log(`显示消息: ${message}, 类型: ${type}`);
    
    const messageContainer = document.getElementById('messageContainer');
    if (!messageContainer) {
        // 如果消息容器不存在，创建一个
        const container = document.createElement('div');
        container.id = 'messageContainer';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    const alertClass = type === 'error' ? 'danger' : type;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alertElement.role = 'alert';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.getElementById('messageContainer').appendChild(alertElement);
    
    // 5秒后自动关闭
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => {
            alertElement.remove();
        }, 150);
    }, 5000);
}

/**
 * 显示API错误提示
 * @param {Error} error - 错误对象
 * @param {string} fallbackMessage - 默认错误消息
 */
function showApiError(error, fallbackMessage = '操作失败，请稍后重试') {
    console.error('API错误:', error);
    
    let errorMessage = fallbackMessage;
    if (error.message) {
        errorMessage = error.message;
    }
    
    showMessage(errorMessage, 'error');
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
        showMessage('请选择一个选项', 'warning');
        return;
    }
    
    const optionId = selectedOption.value;
    console.log(`投票: 投票ID=${pollId}, 选项ID=${optionId}`);
    
    // 发送投票请求
    API.student.votePoll(pollId, optionId)
    .then(response => {
        console.log('投票响应:', response);
        showMessage('投票提交成功', 'success');
        
        // 禁用表单，防止重复提交
        voteForm.querySelectorAll('input').forEach(input => {
            input.disabled = true;
        });
        document.getElementById('submit-vote').disabled = true;
        
        // 重新加载投票列表
        loadActivePolls();
    })
    .catch(error => {
        console.error('投票提交错误:', error);
        showMessage('投票提交失败: ' + (error.message || '服务器错误'), 'error');
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
    
    API.student.getMyQuestions()
    .then(response => {
        console.log('获取最近问题成功:', response);
        if (response.success) {
            updateRecentQuestions(response.questions);
        }
    })
    .catch(error => {
        console.error('获取最近问题失败:', error);
        showApiError(error, '加载问题列表失败');
        
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
    
    API.student.getActivePolls()
    .then(response => {
        console.log('获取活跃投票成功:', response);
        if (response.success) {
            updateActivePolls(response.polls);
        }
    })
    .catch(error => {
        console.error('获取活跃投票失败:', error);
        showApiError(error, '加载投票列表失败');
        
        // 静态数据作为后备
        const staticPoll = {
            id: '1',
            title: '你最喜欢的学习方式是？',
            options: [
                '课堂讲解', 
                '小组讨论', 
                '实验操作', 
                '自主学习'
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
        
        container.innerHTML = `
            <div class="poll-question mb-3">
                <strong>${poll.title}</strong>
            </div>
            <form id="vote-form" data-poll-id="${poll._id}">
                <div class="voting-options">
                    ${poll.options.map((option, index) => `
                        <div class="voting-option">
                            <input type="radio" name="poll-option" id="option${index+1}" 
                                value="${option}" class="d-none" 
                                ${poll.student_vote === option ? 'checked' : ''} 
                                ${poll.student_vote ? 'disabled' : ''}>
                            <label for="option${index+1}" class="option-label">
                                ${option}
                            </label>
                        </div>
                    `).join('')}
                </div>
                <button type="submit" class="btn btn-primary w-100 mt-3" id="submit-vote"
                    ${poll.student_vote ? 'disabled' : ''}>
                    ${poll.student_vote ? '已投票' : '提交投票'}
                </button>
            </form>
        `;
        
        // 重新绑定表单提交事件
        const voteForm = document.getElementById('vote-form');
        if (voteForm) {
            voteForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitVote();
            });
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

// 互动管理相关函数
// 教师端 - 获取待回答问题列表
function fetchPendingQuestions() {
    const token = localStorage.getItem('token');
    if (!token) {
        showAlert('请先登录', 'danger');
        return;
    }

    fetch('/api/teacher/questions', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const questionsList = document.getElementById('pending-questions-list');
            if (questionsList) {
                questionsList.innerHTML = '';
                
                if (data.questions.length === 0) {
                    questionsList.innerHTML = '<li class="list-group-item text-center">暂无待回答问题</li>';
                    return;
                }
                
                data.questions.forEach(question => {
                    const urgent = question.is_urgent ? 
                        '<span class="badge bg-danger ms-2">紧急</span>' : '';
                    const subject = question.subject ? 
                        `<span class="badge bg-info ms-2">${question.subject}</span>` : '';
                    
                    const item = document.createElement('li');
                    item.className = 'list-group-item d-flex justify-content-between align-items-center';
                    item.innerHTML = `
                        <div>
                            <strong>${question.student_name || '学生'}</strong>: ${question.content}
                            ${urgent}
                            ${subject}
                            <small class="text-muted d-block">
                                ${new Date(question.created_at).toLocaleString()}
                            </small>
                        </div>
                        <button class="btn btn-sm btn-primary answer-btn" 
                                data-question-id="${question._id}">
                            回答
                        </button>
                    `;
                    questionsList.appendChild(item);
                });
                
                // 添加回答问题按钮事件
                document.querySelectorAll('.answer-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const questionId = this.getAttribute('data-question-id');
                        openAnswerModal(questionId);
                    });
                });
            }
        } else {
            showAlert(data.message || '获取问题失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('获取问题失败，请检查网络连接', 'danger');
    });
}

// 教师端 - 获取已回答问题列表
function fetchAnsweredQuestions() {
    const token = localStorage.getItem('token');
    if (!token) {
        showAlert('请先登录', 'danger');
        return;
    }

    fetch('/api/teacher/questions/answered', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const questionsList = document.getElementById('answered-questions-list');
            if (questionsList) {
                questionsList.innerHTML = '';
                
                if (data.questions.length === 0) {
                    questionsList.innerHTML = '<li class="list-group-item text-center">暂无已回答问题</li>';
                    return;
                }
                
                data.questions.forEach(question => {
                    const urgent = question.is_urgent ? 
                        '<span class="badge bg-danger ms-2">紧急</span>' : '';
                    const subject = question.subject ? 
                        `<span class="badge bg-info ms-2">${question.subject}</span>` : '';
                    
                    const item = document.createElement('li');
                    item.className = 'list-group-item';
                    item.innerHTML = `
                        <div>
                            <strong>${question.student_name || '学生'}</strong>: ${question.content}
                            ${urgent}
                            ${subject}
                            <small class="text-muted d-block">
                                提问时间: ${new Date(question.created_at).toLocaleString()}
                            </small>
                        </div>
                        <div class="mt-2 p-2 bg-light rounded">
                            <strong>回答</strong>: ${question.answer.content}
                            <small class="text-muted d-block">
                                回答时间: ${new Date(question.answer.created_at).toLocaleString()}
                            </small>
                        </div>
                    `;
                    questionsList.appendChild(item);
                });
            }
        } else {
            showAlert(data.message || '获取问题失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('获取问题失败，请检查网络连接', 'danger');
    });
}

// 教师端 - 打开回答问题模态框
function openAnswerModal(questionId) {
    const modal = document.getElementById('answer-modal');
    if (modal) {
        const questionIdInput = document.getElementById('question-id-input');
        if (questionIdInput) {
            questionIdInput.value = questionId;
        }
        
        // 获取问题详情并填充模态框
        fetch(`/api/interaction/${questionId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const question = data.interaction;
                const questionContent = document.getElementById('question-content');
                if (questionContent) {
                    questionContent.textContent = question.content;
                }
                
                // 显示模态框
                const answerModal = new bootstrap.Modal(modal);
                answerModal.show();
            } else {
                showAlert(data.message || '获取问题详情失败', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('获取问题详情失败，请检查网络连接', 'danger');
        });
    }
}

// 教师端 - 提交问题回答
function submitAnswer() {
    const token = localStorage.getItem('token');
    const questionId = document.getElementById('question-id-input').value;
    const answerContent = document.getElementById('answer-content').value;
    
    if (!answerContent.trim()) {
        showAlert('请输入回答内容', 'warning');
        return;
    }
    
    fetch(`/api/teacher/questions/${questionId}/answer`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: answerContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('回答提交成功', 'success');
            
            // 关闭模态框
            const modal = document.getElementById('answer-modal');
            const answerModal = bootstrap.Modal.getInstance(modal);
            answerModal.hide();
            
            // 刷新问题列表
            fetchPendingQuestions();
            fetchAnsweredQuestions();
            
            // 清空表单
            document.getElementById('answer-content').value = '';
        } else {
            showAlert(data.message || '回答提交失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('回答提交失败，请检查网络连接', 'danger');
    });
}

// 教师端 - 获取活跃投票列表
function fetchActivePollsTeacher() {
    fetch('/api/teacher/polls/active', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const pollsList = document.getElementById('active-polls-list');
            document.getElementById('active-polls-count-badge').textContent = data.polls.length;
            
            if (data.polls.length === 0) {
                pollsList.innerHTML = '<div class="text-center py-3">暂无活跃投票</div>';
                return;
            }
            
            pollsList.innerHTML = data.polls.map(poll => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${poll.title}</h5>
                        <div class="mb-3">
                            ${Object.entries(poll.votes).map(([option, count]) => `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span>${option}</span>
                                        <span>${count} 票</span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: ${calculatePercentage(count, getTotalVotes(poll.votes))}%" 
                                             aria-valuenow="${count}" aria-valuemin="0" 
                                             aria-valuemax="${getTotalVotes(poll.votes)}">
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                总投票数: ${getTotalVotes(poll.votes)} · 
                                创建时间: ${formatTimeAgo(new Date(poll.created_at))}
                            </small>
                            <button class="btn btn-danger btn-sm" onclick="endPoll('${poll._id}')">
                                结束投票
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    })
    .catch(error => console.error('获取活跃投票失败:', error));
}

// 获取已结束投票列表
function fetchEndedPollsTeacher() {
    fetch('/api/teacher/polls/ended', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const pollsList = document.getElementById('ended-polls-list');
            document.getElementById('ended-polls-count').textContent = data.polls.length;
            
            if (data.polls.length === 0) {
                pollsList.innerHTML = '<div class="text-center py-3">暂无已结束投票</div>';
                return;
            }
            
            pollsList.innerHTML = data.polls.map(poll => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${poll.title}</h5>
                        <div class="mb-3">
                            ${Object.entries(poll.votes).map(([option, count]) => `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span>${option}</span>
                                        <span>${count} 票</span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar bg-secondary" role="progressbar" 
                                             style="width: ${calculatePercentage(count, getTotalVotes(poll.votes))}%" 
                                             aria-valuenow="${count}" aria-valuemin="0" 
                                             aria-valuemax="${getTotalVotes(poll.votes)}">
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <small class="text-muted">
                            总投票数: ${getTotalVotes(poll.votes)} · 
                            结束时间: ${formatTimeAgo(new Date(poll.updated_at))}
                        </small>
                    </div>
                </div>
            `).join('');
        }
    })
    .catch(error => console.error('获取已结束投票失败:', error));
}

// 创建新投票
function createNewPoll() {
    const title = document.getElementById('poll-title').value;
    const duration = parseInt(document.getElementById('poll-duration').value) || 0;
    const optionInputs = document.querySelectorAll('.poll-option-input');
    const options = Array.from(optionInputs).map(input => input.value.trim()).filter(Boolean);
    
    if (!title.trim()) {
        showAlert('请输入投票标题', 'warning');
        return;
    }
    
    if (options.length < 2) {
        showAlert('至少需要两个选项', 'warning');
        return;
    }
    
    fetch('/api/teacher/polls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ title, options, duration })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('投票创建成功', 'success');
            bootstrap.Modal.getInstance(document.getElementById('create-poll-modal')).hide();
            // 重置表单
            document.getElementById('poll-title').value = '';
            document.getElementById('poll-duration').value = '';
            resetPollOptions();
            // 刷新投票列表
            fetchActivePollsTeacher();
            loadInteractionStats();
        } else {
            showAlert(data.message || '创建投票失败', 'error');
        }
    })
    .catch(error => {
        console.error('创建投票失败:', error);
        showAlert('创建投票失败，请重试', 'error');
    });
}

// 结束投票
function endPoll(pollId) {
    if (!confirm('确定要结束这个投票吗？')) return;
    
    fetch(`/api/teacher/polls/${pollId}/end`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('投票已结束', 'success');
            // 刷新投票列表
            fetchActivePollsTeacher();
            fetchEndedPollsTeacher();
            loadInteractionStats();
        } else {
            showAlert(data.message || '结束投票失败', 'error');
        }
    })
    .catch(error => {
        console.error('结束投票失败:', error);
        showAlert('结束投票失败，请重试', 'error');
    });
}

// 添加投票选项
function addPollOption() {
    const container = document.getElementById('poll-options-container');
    const optionCount = container.children.length + 1;
    
    const optionDiv = document.createElement('div');
    optionDiv.className = 'mb-2 d-flex align-items-center';
    optionDiv.innerHTML = `
        <input type="text" class="form-control poll-option-input" placeholder="选项${optionCount}">
        ${optionCount > 2 ? `
            <button type="button" class="btn btn-outline-danger btn-sm ms-2" onclick="this.parentElement.remove()">
                <i class="bi bi-trash"></i>
            </button>
        ` : ''}
    `;
    
    container.appendChild(optionDiv);
}

// 重置投票选项
function resetPollOptions() {
    const container = document.getElementById('poll-options-container');
    container.innerHTML = `
        <div class="mb-2 d-flex align-items-center">
            <input type="text" class="form-control poll-option-input" placeholder="选项1">
        </div>
        <div class="mb-2 d-flex align-items-center">
            <input type="text" class="form-control poll-option-input" placeholder="选项2">
        </div>
    `;
}

// 计算百分比
function calculatePercentage(count, total) {
    if (total === 0) return 0;
    return Math.round((count / total) * 100);
}

// 获取总投票数
function getTotalVotes(votes) {
    return Object.values(votes).reduce((sum, count) => sum + count, 0);
}

// 学生端 - 获取我的问题列表
function fetchMyQuestions() {
    const token = localStorage.getItem('token');
    if (!token) {
        showAlert('请先登录', 'danger');
        return;
    }

    fetch('/api/student/questions', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const questionsList = document.getElementById('my-questions-list');
            if (questionsList) {
                questionsList.innerHTML = '';
                
                if (data.questions.length === 0) {
                    questionsList.innerHTML = '<li class="list-group-item text-center">您还没有提出过问题</li>';
                    return;
                }
                
                data.questions.forEach(question => {
                    const urgent = question.is_urgent ? 
                        '<span class="badge bg-danger ms-2">紧急</span>' : '';
                    const subject = question.subject ? 
                        `<span class="badge bg-info ms-2">${question.subject}</span>` : '';
                    
                    const item = document.createElement('li');
                    item.className = 'list-group-item';
                    
                    let answerHtml = '';
                    if (question.answer) {
                        answerHtml = `
                            <div class="mt-2 p-2 bg-light rounded">
                                <strong>教师回答</strong>: ${question.answer.content}
                                <small class="text-muted d-block">
                                    回答时间: ${new Date(question.answer.created_at).toLocaleString()}
                                </small>
                            </div>
                        `;
                    } else {
                        answerHtml = `
                            <div class="mt-2">
                                <span class="badge bg-warning">待回答</span>
                            </div>
                        `;
                    }
                    
                    item.innerHTML = `
                        <div>
                            <strong>我的提问</strong>: ${question.content}
                            ${urgent}
                            ${subject}
                            <small class="text-muted d-block">
                                提问时间: ${new Date(question.created_at).toLocaleString()}
                            </small>
                        </div>
                        ${answerHtml}
                    `;
                    
                    questionsList.appendChild(item);
                });
            }
        } else {
            showAlert(data.message || '获取问题失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('获取问题失败，请检查网络连接', 'danger');
    });
}

// 学生端 - 提交新问题
function submitNewQuestion() {
    const token = localStorage.getItem('token');
    if (!token) {
        showAlert('请先登录', 'danger');
        return;
    }
    
    const content = document.getElementById('question-content-input').value;
    const subject = document.getElementById('question-subject-input').value;
    const isUrgent = document.getElementById('question-urgent-checkbox').checked;
    
    if (!content.trim()) {
        showAlert('请输入问题内容', 'warning');
        return;
    }
    
    fetch('/api/student/questions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: content,
            subject: subject,
            isUrgent: isUrgent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('问题提交成功', 'success');
            
            // 关闭模态框
            const modal = document.getElementById('ask-question-modal');
            const questionModal = bootstrap.Modal.getInstance(modal);
            questionModal.hide();
            
            // 刷新我的问题列表
            fetchMyQuestions();
            
            // 清空表单
            document.getElementById('question-content-input').value = '';
            document.getElementById('question-subject-input').value = '';
            document.getElementById('question-urgent-checkbox').checked = false;
        } else {
            showAlert(data.message || '提交问题失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('提交问题失败，请检查网络连接', 'danger');
    });
}

// 学生端 - 获取活跃投票列表
function fetchActivePollsStudent() {
    const token = localStorage.getItem('token');
    if (!token) {
        showAlert('请先登录', 'danger');
        return;
    }

    fetch('/api/student/polls/active', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const pollsList = document.getElementById('active-polls-list-student');
            if (pollsList) {
                pollsList.innerHTML = '';
                
                if (data.polls.length === 0) {
                    pollsList.innerHTML = '<div class="text-center py-3">暂无活跃投票</div>';
                    return;
                }
                
                data.polls.forEach(poll => {
                    // 计算每个选项的投票百分比
                    const totalVotes = Object.values(poll.votes || {}).reduce((a, b) => a + b, 0);
                    
                    const pollCard = document.createElement('div');
                    pollCard.className = 'card mb-3';
                    
                    let optionsHtml = '';
                    if (poll.options && Array.isArray(poll.options)) {
                        poll.options.forEach(option => {
                            const votes = poll.votes && poll.votes[option] ? poll.votes[option] : 0;
                            const percentage = totalVotes > 0 ? (votes / totalVotes * 100).toFixed(1) : 0;
                            
                            // 检查学生是否已投票及选择了哪个选项
                            const isSelected = poll.student_vote === option;
                            const buttonClass = isSelected ? 'btn-success' : 'btn-outline-primary';
                            const disabledAttr = poll.student_vote ? 'disabled' : '';
                            
                            optionsHtml += `
                                <div class="mb-2">
                                    <button class="btn ${buttonClass} w-100 text-start d-flex justify-content-between vote-btn"
                                            data-poll-id="${poll._id}"
                                            data-option="${option}"
                                            ${disabledAttr}>
                                        <span>${option}</span>
                                        <span>${votes}票 (${percentage}%)</span>
                                    </button>
                                </div>
                            `;
                        });
                    }
                    
                    pollCard.innerHTML = `
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">${poll.title}</h5>
                            <span class="badge bg-success">活跃</span>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                ${optionsHtml}
                            </div>
                            <div class="text-muted">
                                共计 ${totalVotes} 票 | 创建于 ${new Date(poll.created_at).toLocaleString()}
                                ${poll.student_vote ? '<div class="text-success mt-1">您已投票</div>' : ''}
                            </div>
                        </div>
                    `;
                    
                    pollsList.appendChild(pollCard);
                });
                
                // 添加投票按钮事件
                if (!poll.student_vote) {
                    document.querySelectorAll('.vote-btn:not([disabled])').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const pollId = this.getAttribute('data-poll-id');
                            const option = this.getAttribute('data-option');
                            submitVote(pollId, option);
                        });
                    });
                }
            }
        } else {
            showAlert(data.message || '获取投票失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('获取投票失败，请检查网络连接', 'danger');
    });
}

// 学生端 - 提交投票
function submitVote(pollId, option) {
    const token = localStorage.getItem('token');
    if (!token) {
        showAlert('请先登录', 'danger');
        return;
    }

    fetch(`/api/student/polls/${pollId}/vote`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            optionId: option
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('投票成功', 'success');
            
            // 刷新投票列表
            fetchActivePollsStudent();
        } else {
            showAlert(data.message || '投票失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('投票失败，请检查网络连接', 'danger');
    });
}

// 工具函数 - 显示提示信息
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) {
        // 如果不存在提示容器，创建一个
        const container = document.createElement('div');
        container.id = 'alerts-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    const alertId = `alert-${Date.now()}`;
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.id = alertId;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.getElementById('alerts-container').appendChild(alertElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 3000);
}

// 添加页面加载完成后的事件监听
document.addEventListener('DOMContentLoaded', function() {
    // 如果当前页面是教师互动管理页面
    if (document.getElementById('teacher-interactions-page')) {
        // 获取问题和投票列表
        fetchPendingQuestions();
        fetchAnsweredQuestions();
        fetchActivePollsTeacher();
        fetchEndedPollsTeacher();
        
        // 提交回答按钮事件
        const submitAnswerBtn = document.getElementById('submit-answer-btn');
        if (submitAnswerBtn) {
            submitAnswerBtn.addEventListener('click', submitAnswer);
        }
        
        // 创建投票按钮事件
        const createPollBtn = document.getElementById('create-poll-btn');
        if (createPollBtn) {
            createPollBtn.addEventListener('click', createNewPoll);
        }
        
        // 添加投票选项按钮事件
        const addOptionBtn = document.getElementById('add-option-btn');
        if (addOptionBtn) {
            addOptionBtn.addEventListener('click', addPollOption);
        }
    }
    
    // 如果当前页面是学生互动页面
    if (document.getElementById('student-interactions-page')) {
        // 获取我的问题和活跃投票列表
        fetchMyQuestions();
        fetchActivePollsStudent();
        
        // 提交问题按钮事件
        const submitQuestionBtn = document.getElementById('submit-question-btn');
        if (submitQuestionBtn) {
            submitQuestionBtn.addEventListener('click', submitNewQuestion);
        }
    }
}); 

// 教师互动页面初始化
function initTeacherInteractions() {
    if (!document.getElementById('teacher-interactions-page')) return;
    
    // 加载统计数据
    loadInteractionStats();
    // 加载问题列表
    fetchPendingQuestions();
    fetchAnsweredQuestions();
    // 加载投票列表
    fetchActivePollsTeacher();
    fetchEndedPollsTeacher();
    
    // 绑定创建投票事件
    document.getElementById('create-poll-btn').addEventListener('click', createNewPoll);
    document.getElementById('add-option-btn').addEventListener('click', addPollOption);
    document.getElementById('submit-answer-btn').addEventListener('click', submitAnswer);
}

/**
 * 加载互动统计数据
 */
function loadInteractionStats() {
    API.teacher.getInteractionStats()
    .then(response => {
        if (response.success) {
            document.getElementById('pending-questions-count').textContent = response.stats.pending_questions;
            document.getElementById('active-polls-count').textContent = response.stats.active_polls;
            document.getElementById('urgent-questions-count').textContent = response.stats.urgent_questions;
        }
    })
    .catch(error => {
        console.error('加载统计数据失败:', error);
        showApiError(error, '加载统计数据失败');
    });
}

/**
 * 获取待回答问题列表
 */
function fetchPendingQuestions() {
    API.teacher.getPendingQuestions()
    .then(response => {
        if (response.success) {
            const questionsList = document.getElementById('pending-questions-list');
            document.getElementById('pending-count').textContent = response.questions.length;
            
            if (response.questions.length === 0) {
                questionsList.innerHTML = '<li class="list-group-item text-center">暂无待回答问题</li>';
                return;
            }
            
            questionsList.innerHTML = response.questions.map(question => `
                <li class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${question.subject || '无主题'}</h6>
                            <p class="mb-1">${question.content}</p>
                            <small class="text-muted">
                                来自: ${question.student_name || '学生'} · 
                                ${formatTimeAgo(new Date(question.created_at))}
                                ${question.is_urgent ? ' · <span class="badge bg-danger">紧急</span>' : ''}
                            </small>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="openAnswerModal('${question._id}', '${question.content}')">
                            回答
                        </button>
                    </div>
                </li>
            `).join('');
        }
    })
    .catch(error => {
        console.error('获取待回答问题失败:', error);
        showApiError(error, '获取待回答问题失败');
    });
}

/**
 * 获取已回答问题列表
 */
function fetchAnsweredQuestions() {
    API.teacher.getAnsweredQuestions()
    .then(response => {
        if (response.success) {
            const questionsList = document.getElementById('answered-questions-list');
            document.getElementById('answered-count').textContent = response.questions.length;
            
            if (response.questions.length === 0) {
                questionsList.innerHTML = '<li class="list-group-item text-center">暂无已回答问题</li>';
                return;
            }
            
            questionsList.innerHTML = response.questions.map(question => `
                <li class="list-group-item">
                    <div>
                        <h6 class="mb-1">${question.subject || '无主题'}</h6>
                        <p class="mb-1">${question.content}</p>
                        <div class="bg-light p-2 rounded mt-2">
                            <p class="mb-1"><strong>回答：</strong>${question.answer.content}</p>
                            <small class="text-muted">
                                回答者: ${question.answer.teacher_name || '教师'} · 
                                ${formatTimeAgo(new Date(question.answer.created_at))}
                            </small>
                        </div>
                    </div>
                </li>
            `).join('');
        }
    })
    .catch(error => {
        console.error('获取已回答问题失败:', error);
        showApiError(error, '获取已回答问题失败');
    });
}

/**
 * 获取活跃投票列表（教师视图）
 */
function fetchActivePollsTeacher() {
    API.teacher.getActivePolls()
    .then(response => {
        if (response.success) {
            const pollsList = document.getElementById('active-polls-list');
            document.getElementById('active-polls-count-badge').textContent = response.polls.length;
            
            if (response.polls.length === 0) {
                pollsList.innerHTML = '<div class="text-center py-3">暂无活跃投票</div>';
                return;
            }
            
            pollsList.innerHTML = response.polls.map(poll => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${poll.title}</h5>
                        <div class="mb-3">
                            ${Object.entries(poll.votes).map(([option, count]) => `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span>${option}</span>
                                        <span>${count} 票</span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: ${calculatePercentage(count, getTotalVotes(poll.votes))}%" 
                                             aria-valuenow="${count}" aria-valuemin="0" 
                                             aria-valuemax="${getTotalVotes(poll.votes)}">
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                总投票数: ${getTotalVotes(poll.votes)} · 
                                创建时间: ${formatTimeAgo(new Date(poll.created_at))}
                            </small>
                            <button class="btn btn-danger btn-sm" onclick="endPoll('${poll._id}')">
                                结束投票
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    })
    .catch(error => {
        console.error('获取活跃投票失败:', error);
        showApiError(error, '获取活跃投票失败');
    });
}

/**
 * 获取已结束投票列表
 */
function fetchEndedPollsTeacher() {
    API.teacher.getEndedPolls()
    .then(response => {
        if (response.success) {
            const pollsList = document.getElementById('ended-polls-list');
            document.getElementById('ended-polls-count').textContent = response.polls.length;
            
            if (response.polls.length === 0) {
                pollsList.innerHTML = '<div class="text-center py-3">暂无已结束投票</div>';
                return;
            }
            
            pollsList.innerHTML = response.polls.map(poll => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${poll.title}</h5>
                        <div class="mb-3">
                            ${Object.entries(poll.votes).map(([option, count]) => `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span>${option}</span>
                                        <span>${count} 票</span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar bg-secondary" role="progressbar" 
                                             style="width: ${calculatePercentage(count, getTotalVotes(poll.votes))}%" 
                                             aria-valuenow="${count}" aria-valuemin="0" 
                                             aria-valuemax="${getTotalVotes(poll.votes)}">
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <small class="text-muted">
                            总投票数: ${getTotalVotes(poll.votes)} · 
                            结束时间: ${formatTimeAgo(new Date(poll.ended_at || poll.updated_at))}
                        </small>
                    </div>
                </div>
            `).join('');
        }
    })
    .catch(error => {
        console.error('获取已结束投票失败:', error);
        showApiError(error, '获取已结束投票失败');
    });
}

// 打开回答问题模态框
function openAnswerModal(questionId, content) {
    document.getElementById('question-id-input').value = questionId;
    document.getElementById('question-content').textContent = content;
    new bootstrap.Modal(document.getElementById('answer-modal')).show();
}

// 提交问题回答
function submitAnswer() {
    const questionId = document.getElementById('question-id-input').value;
    const content = document.getElementById('answer-content').value;
    
    if (!content.trim()) {
        showAlert('请输入回答内容', 'warning');
        return;
    }
    
    fetch(`/api/teacher/questions/${questionId}/answer`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('回答提交成功', 'success');
            bootstrap.Modal.getInstance(document.getElementById('answer-modal')).hide();
            // 刷新问题列表
            fetchPendingQuestions();
            fetchAnsweredQuestions();
            loadInteractionStats();
        } else {
            showAlert(data.message || '回答提交失败', 'error');
        }
    })
    .catch(error => {
        console.error('提交回答失败:', error);
        showAlert('回答提交失败，请重试', 'error');
    });
}

// 学生互动页面初始化
function initStudentInteractions() {
    // 加载我的问题列表
    fetchMyQuestions();
    // 加载活跃投票
    fetchActivePollsStudent();
    
    // 绑定提交问题事件
    document.getElementById('submit-question-btn').addEventListener('click', submitNewQuestion);
}

// 获取我的问题列表
async function fetchMyQuestions() {
    try {
        const response = await fetch('/api/student/questions', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('获取问题列表失败');
        }
        
        const data = await response.json();
        const questionsList = document.getElementById('my-questions-list');
        
        if (data.length === 0) {
            questionsList.innerHTML = '<li class="list-group-item text-center">暂无问题记录</li>';
            return;
        }
        
        questionsList.innerHTML = data.map(question => `
            <li class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">
                            ${question.subject ? question.subject : '无主题'}
                            ${question.is_urgent ? '<span class="badge bg-danger ms-2">紧急</span>' : ''}
                        </h6>
                        <p class="mb-1">${question.content}</p>
                        <small class="text-muted">
                            提问时间：${new Date(question.created_at).toLocaleString()}
                        </small>
                    </div>
                    <span class="badge ${question.status === 'pending' ? 'bg-warning' : 'bg-success'} ms-2">
                        ${question.status === 'pending' ? '待回答' : '已回答'}
                    </span>
                </div>
                ${question.answer ? `
                    <div class="mt-3 p-3 bg-light rounded">
                        <p class="mb-1"><strong>教师回答：</strong>${question.answer.content}</p>
                        <small class="text-muted">
                            回答时间：${new Date(question.answer.created_at).toLocaleString()}
                            回答教师：${question.answer.teacher_name}
                        </small>
                    </div>
                ` : ''}
            </li>
        `).join('');
        
    } catch (error) {
        console.error('获取问题列表失败:', error);
        showToast('错误', '获取问题列表失败，请稍后重试', 'error');
    }
}

// 提交新问题
async function submitNewQuestion() {
    const subjectInput = document.getElementById('question-subject-input');
    const contentInput = document.getElementById('question-content-input');
    const urgentCheckbox = document.getElementById('question-urgent-checkbox');
    
    if (!contentInput.value.trim()) {
        showToast('提示', '请输入问题内容', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/student/questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                subject: subjectInput.value.trim(),
                content: contentInput.value.trim(),
                is_urgent: urgentCheckbox.checked
            })
        });
        
        if (!response.ok) {
            throw new Error('提交问题失败');
        }
        
        // 清空表单
        subjectInput.value = '';
        contentInput.value = '';
        urgentCheckbox.checked = false;
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('ask-question-modal'));
        modal.hide();
        
        // 刷新问题列表
        fetchMyQuestions();
        
        showToast('成功', '问题提交成功', 'success');
        
    } catch (error) {
        console.error('提交问题失败:', error);
        showToast('错误', '提交问题失败，请稍后重试', 'error');
    }
}

// 获取活跃投票列表（学生视图）
async function fetchActivePollsStudent() {
    try {
        const response = await fetch('/api/student/polls/active', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('获取投票列表失败');
        }
        
        const data = await response.json();
        const pollsList = document.getElementById('active-polls-list-student');
        
        if (data.length === 0) {
            pollsList.innerHTML = '<div class="text-center">暂无活跃投票</div>';
            return;
        }
        
        pollsList.innerHTML = data.map(poll => `
            <div class="poll-item mb-4">
                <h6 class="mb-3">${poll.title}</h6>
                <form class="poll-form" data-poll-id="${poll._id}">
                    ${poll.options.map((option, index) => `
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" 
                                name="poll_${poll._id}" 
                                id="option_${poll._id}_${index}" 
                                value="${option}"
                                ${poll.hasVoted ? 'disabled' : ''}>
                            <label class="form-check-label" for="option_${poll._id}_${index}">
                                ${option}
                                ${poll.hasVoted ? `
                                    <span class="text-muted ms-2">
                                        (${poll.votes[option]} 票, 
                                        ${calculatePercentage(poll.votes[option], getTotalVotes(poll.votes))}%)
                                    </span>
                                ` : ''}
                            </label>
                        </div>
                    `).join('')}
                    ${!poll.hasVoted ? `
                        <button type="button" class="btn btn-primary btn-sm mt-2" 
                            onclick="submitVote('${poll._id}')">
                            提交投票
                        </button>
                    ` : ''}
                </form>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('获取投票列表失败:', error);
        showToast('错误', '获取投票列表失败，请稍后重试', 'error');
    }
}

// 提交投票
async function submitVote(pollId) {
    const form = document.querySelector(`form[data-poll-id="${pollId}"]`);
    const selectedOption = form.querySelector('input[type="radio"]:checked');
    
    if (!selectedOption) {
        showToast('提示', '请选择一个选项', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/student/polls/${pollId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                option: selectedOption.value
            })
        });
        
        if (!response.ok) {
            throw new Error('提交投票失败');
        }
        
        // 刷新投票列表
        fetchActivePollsStudent();
        showToast('成功', '投票成功', 'success');
        
    } catch (error) {
        console.error('提交投票失败:', error);
        showToast('错误', '提交投票失败，请稍后重试', 'error');
    }
}

// 计算投票百分比
function calculatePercentage(votes, total) {
    if (total === 0) return 0;
    return Math.round((votes / total) * 100);
}

// 计算总投票数
function getTotalVotes(votes) {
    return Object.values(votes).reduce((a, b) => a + b, 0);
}

// 显示提示消息
function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container') || createToastContainer();
    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// 创建Toast容器
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// 获取授权请求头
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    const token = localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
} 