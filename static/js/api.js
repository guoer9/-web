/**
 * API工具函数库 - 封装后端API交互
 */

// API基础URL，使用相对路径来匹配当前域名
const API_BASE_URL = '/api';

/**
 * 获取授权请求头
 * @returns {Object} 包含授权信息的请求头对象
 */
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

/**
 * 通用API请求函数
 * @param {string} endpoint - API端点路径
 * @param {string} method - HTTP方法
 * @param {Object} data - 请求数据
 * @returns {Promise} 返回请求Promise
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: getAuthHeaders()
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const responseData = await response.json();
        
        if (!response.ok) {
            throw new Error(responseData.message || '请求失败');
        }
        
        return responseData;
    } catch (error) {
        console.error(`API请求失败 (${url}):`, error);
        throw error;
    }
}

// 用户认证API
const authAPI = {
    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} 登录结果
     */
    async login(username, password) {
        return apiRequest('/auth/login', 'POST', { username, password });
    },
    
    /**
     * 用户注册
     * @param {Object} userData - 用户数据
     * @returns {Promise} 注册结果
     */
    async register(userData) {
        return apiRequest('/auth/register', 'POST', userData);
    },
    
    /**
     * 用户登出
     * @returns {Promise} 登出结果
     */
    async logout() {
        return apiRequest('/auth/logout', 'POST');
    },
    
    /**
     * 获取当前用户信息
     * @returns {Promise} 用户信息
     */
    async getCurrentUser() {
        return apiRequest('/auth/me');
    }
};

// 教师API
const teacherAPI = {
    /**
     * 获取互动统计数据
     * @returns {Promise} 统计数据
     */
    async getInteractionStats() {
        return apiRequest('/teacher/interaction/stats');
    },
    
    /**
     * 获取待回答问题列表
     * @returns {Promise} 问题列表
     */
    async getPendingQuestions() {
        return apiRequest('/teacher/questions');
    },
    
    /**
     * 获取已回答问题列表
     * @returns {Promise} 问题列表
     */
    async getAnsweredQuestions() {
        return apiRequest('/teacher/questions/answered');
    },
    
    /**
     * 回答问题
     * @param {string} questionId - 问题ID
     * @param {string} content - 回答内容
     * @returns {Promise} 回答结果
     */
    async answerQuestion(questionId, content) {
        return apiRequest(`/teacher/questions/${questionId}/answer`, 'POST', { content });
    },
    
    /**
     * 创建投票
     * @param {string} title - 投票标题
     * @param {Array} options - 投票选项数组
     * @param {number} duration - 投票持续时间（可选）
     * @returns {Promise} 创建结果
     */
    async createPoll(title, options, duration = 0) {
        return apiRequest('/teacher/polls', 'POST', { title, options, duration });
    },
    
    /**
     * 获取活跃投票列表
     * @returns {Promise} 投票列表
     */
    async getActivePolls() {
        return apiRequest('/teacher/polls/active');
    },
    
    /**
     * 获取已结束投票列表
     * @returns {Promise} 投票列表
     */
    async getEndedPolls() {
        return apiRequest('/teacher/polls/ended');
    },
    
    /**
     * 结束投票
     * @param {string} pollId - 投票ID
     * @returns {Promise} 结束结果
     */
    async endPoll(pollId) {
        return apiRequest(`/teacher/polls/${pollId}/end`, 'POST');
    }
};

// 学生API
const studentAPI = {
    /**
     * 获取我的问题列表
     * @returns {Promise} 问题列表
     */
    async getMyQuestions() {
        return apiRequest('/student/questions');
    },
    
    /**
     * 提交新问题
     * @param {string} content - 问题内容
     * @param {string} subject - 问题主题（可选）
     * @param {boolean} isUrgent - 是否紧急（可选）
     * @returns {Promise} 提交结果
     */
    async createQuestion(content, subject = '', isUrgent = false) {
        return apiRequest('/student/questions', 'POST', { content, subject, is_urgent: isUrgent });
    },
    
    /**
     * 获取活跃投票列表
     * @returns {Promise} 投票列表
     */
    async getActivePolls() {
        return apiRequest('/student/polls/active');
    },
    
    /**
     * 提交投票
     * @param {string} pollId - 投票ID
     * @param {string} option - 选择的选项
     * @returns {Promise} 提交结果
     */
    async votePoll(pollId, option) {
        return apiRequest(`/student/polls/${pollId}/vote`, 'POST', { option });
    }
};

// 导出API对象
window.API = {
    auth: authAPI,
    teacher: teacherAPI,
    student: studentAPI
}; 