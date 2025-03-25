"""
AI服务模块
提供大模型API调用功能，用于文本分析和总结
"""
import requests
import json
import logging
from flask import current_app
import time

class AIService:
    """AI服务类，提供对大模型API的调用"""
    
    def __init__(self):
        """初始化AI服务"""
        self.logger = logging.getLogger(__name__)
        
    def _call_ai_api(self, messages, temperature=0.7, max_tokens=1000):
        """
        调用大模型API
        
        Args:
            messages: 消息列表，格式为[{"role": "system", "content": "..."}, ...]
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数
            
        Returns:
            response_text: AI响应的文本
            success: 是否成功
        """
        if not current_app.config.get("AI_API_AVAILABLE", False):
            self.logger.warning("AI API未配置或不可用，无法进行文本分析")
            return "AI分析服务当前不可用，请检查系统配置。", False
        
        try:
            headers = {
                "Authorization": f"Bearer {current_app.config['AI_API_KEY']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": current_app.config["AI_MODEL"],
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 添加重试机制
            max_retries = 3
            retry_delay = 2  # 初始延迟2秒
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        current_app.config["AI_API_URL"], 
                        headers=headers, 
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result["choices"][0]["message"]["content"], True
                    elif response.status_code == 429:  # 速率限制
                        self.logger.warning(f"AI API速率限制，尝试第 {attempt+1}/{max_retries} 次重试")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        self.logger.error(f"AI API调用失败: {response.status_code} - {response.text}")
                        return f"AI分析失败: HTTP {response.status_code}", False
                        
                except requests.exceptions.Timeout:
                    self.logger.warning(f"AI API请求超时，尝试第 {attempt+1}/{max_retries} 次重试")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"AI API请求异常: {str(e)}")
                    return f"AI分析服务请求异常: {str(e)}", False
            
            return "AI分析服务暂时不可用，请稍后再试。", False
            
        except Exception as e:
            self.logger.error(f"调用AI API时发生异常: {str(e)}")
            return f"AI分析发生异常: {str(e)}", False

    def analyze_feedback(self, feedback_text):
        """
        分析反馈文本，识别情感和关键点
        
        Args:
            feedback_text: 反馈文本
            
        Returns:
            analysis: 分析结果，包含情感和关键点
            success: 是否成功
        """
        messages = [
            {"role": "system", "content": "你是一个教育领域的文本分析专家。你的任务是分析学生对课程的反馈，识别出情感倾向（正面、负面或中性）以及反馈中的关键点。"},
            {"role": "user", "content": f"请分析以下学生反馈，指出情感倾向（positive、negative或neutral）和主要关键点：\n\n{feedback_text}"}
        ]
        
        result, success = self._call_ai_api(messages)
        
        if not success:
            return {"sentiment": "neutral", "key_points": ["分析失败"]}, False
        
        # 尝试从结果中提取结构化信息
        try:
            # 识别情感
            sentiment = "neutral"
            if "positive" in result.lower() or "积极" in result or "正面" in result:
                sentiment = "positive"
            elif "negative" in result.lower() or "消极" in result or "负面" in result:
                sentiment = "negative"
            
            # 提取关键点
            key_points = []
            for line in result.split('\n'):
                line = line.strip()
                if line and line.startswith(('-', '•', '*', '1.', '2.', '3.', '关键点', '要点')):
                    clean_line = line.lstrip('-•*1234567890. ')
                    if clean_line:
                        key_points.append(clean_line)
            
            if not key_points:
                # 如果无法提取结构化关键点，则使用整个结果
                key_points = [result]
            
            analysis = {
                "sentiment": sentiment,
                "key_points": key_points,
                "full_analysis": result
            }
            
            return analysis, True
            
        except Exception as e:
            self.logger.error(f"解析AI分析结果时出错: {str(e)}")
            return {"sentiment": "neutral", "key_points": ["解析分析结果失败"], "full_analysis": result}, False
            
    def summarize_news(self, news_items, max_length=3):
        """
        对新闻列表进行摘要总结
        
        Args:
            news_items: 新闻项列表，每项包含标题和摘要
            max_length: 最大摘要数量
            
        Returns:
            summary: 总结文本
            categories: 识别出的新闻分类
            success: 是否成功
        """
        if not news_items:
            return "没有可用的新闻进行总结。", [], True
        
        # 准备新闻数据
        news_text = ""
        for i, item in enumerate(news_items[:10]):  # 限制为前10条新闻
            news_text += f"{i+1}. 标题: {item.get('title', '无标题')}\n"
            news_text += f"   摘要: {item.get('summary', '无摘要')}\n\n"
        
        messages = [
            {"role": "system", "content": "你是一个教育新闻分析专家。你的任务是对教育领域新闻进行分析和总结，提取重要信息，并识别新闻所属的类别（如教育政策、教学方法、考试升学等）。"},
            {"role": "user", "content": f"请对以下教育领域新闻进行分析，提供一个简短的总结（不超过{max_length}点），并指出每条新闻所属的类别：\n\n{news_text}"}
        ]
        
        result, success = self._call_ai_api(messages)
        
        if not success:
            return "无法生成新闻总结。", [], False
        
        # 尝试提取分类
        categories = []
        category_keywords = ["教育政策", "教学方法", "教育科技", "考试升学", "素质教育"]
        
        for keyword in category_keywords:
            if keyword in result:
                categories.append(keyword)
        
        if not categories:
            categories = ["教育资讯"]
        
        return result, categories, True
    
    def classify_news(self, title, content):
        """
        对单条新闻进行分类
        
        Args:
            title: 新闻标题
            content: 新闻内容
            
        Returns:
            category: 分类结果
            success: 是否成功
        """
        messages = [
            {"role": "system", "content": "你是一个教育新闻分类专家。你的任务是将教育新闻分类到以下类别之一：教育政策、教学方法、教育科技、考试升学、素质教育、其他。"},
            {"role": "user", "content": f"请将以下教育新闻分类到这些类别之一（教育政策、教学方法、教育科技、考试升学、素质教育、其他）：\n\n标题：{title}\n\n内容：{content}\n\n请只回复分类结果，不要解释。"}
        ]
        
        result, success = self._call_ai_api(messages, temperature=0.3, max_tokens=50)
        
        if not success:
            return "其他", False
        
        # 检查结果中是否包含预定义类别
        categories = ["教育政策", "教学方法", "教育科技", "考试升学", "素质教育"]
        
        for category in categories:
            if category in result:
                return category, True
        
        return "其他", True

# 单例模式
ai_service = AIService() 