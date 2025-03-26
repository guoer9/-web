#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻服务模块
提供新闻数据访问和处理功能
"""
import logging
import threading
import time
import random
from datetime import datetime, timedelta
import schedule
from src.services.news_scraper import NewsScraper

logger = logging.getLogger(__name__)

class NewsService:
    """新闻服务，提供新闻相关功能的封装"""
    
    def __init__(self):
        """初始化新闻服务"""
        self.news_scraper = NewsScraper()
        self.update_thread = None
        self.is_running = False
        self.last_update_time = None
        logger.info("新闻服务初始化完成")
    
    def get_sources(self):
        """
        获取支持的新闻源列表
        
        Returns:
            list: 新闻源列表
        """
        return self.news_scraper.get_sources()
    
    def get_news_list(self, source=None, limit=10, page=1):
        """
        获取新闻列表
        
        Args:
            source: 新闻源标识
            limit: 每页数量
            page: 页码
        
        Returns:
            dict: 包含新闻列表和总数的字典
        """
        return self.news_scraper.get_news_list(source, limit, page)
    
    def get_news_detail(self, url):
        """
        获取新闻详情
        
        Args:
            url: 新闻URL
        
        Returns:
            dict: 新闻详情信息
        """
        return self.news_scraper.get_news_detail(url)
    
    def search_news(self, query, limit=10, page=1):
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            limit: 每页数量
            page: 页码
        
        Returns:
            dict: 包含搜索结果和总数的字典
        """
        return self.news_scraper.search_news(query, limit, page)
    
    def get_daily_summary(self):
        """
        获取每日教育新闻摘要
        
        Returns:
            str: 新闻摘要文本
        """
        return self.news_scraper.get_daily_summary()
    
    def update_news(self):
        """更新新闻数据，定时调用"""
        try:
            logger.info("开始更新新闻数据")
            # 模拟更新过程
            time.sleep(2)
            self.last_update_time = time.time()
            logger.info("新闻数据更新完成")
            return True
        except Exception as e:
            logger.error(f"更新新闻数据失败: {str(e)}")
            return False
    
    def schedule_update(self, interval=3600):
        """
        启动定时更新
        
        Args:
            interval: 更新间隔（秒）
        """
        if self.is_running:
            logger.warning("新闻更新服务已经在运行中")
            return False
        
        def run_continuously():
            """持续运行调度器"""
            self.is_running = True
            logger.info(f"新闻更新服务已启动，更新间隔: {interval}秒")
            
            # 每隔指定时间执行一次更新
            schedule.every(interval).seconds.do(self.update_news)
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        
        # 启动更新线程
        self.update_thread = threading.Thread(target=run_continuously)
        self.update_thread.daemon = True
        self.update_thread.start()
        return True
    
    def stop_update(self):
        """停止定时更新"""
        if not self.is_running:
            logger.warning("新闻更新服务未运行")
            return False
        
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=10)
        
        logger.info("新闻更新服务已停止")
        return True

# 创建全局服务实例
news_service = NewsService() 