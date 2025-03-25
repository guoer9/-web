"""
行业新闻服务模块
提供新闻采集、过滤和推送功能
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import threading
import logging
import random
from bson.objectid import ObjectId
import json
from flask import current_app
from pymongo import MongoClient, DESCENDING
from utils.ai_service import ai_service

class NewsService:
    """行业新闻服务类"""
    
    # 新闻来源配置
    NEWS_SOURCES = [
        {
            "name": "中国教育新闻网",
            "url": "http://www.jyb.cn/rmtzgjyb/",
            "selector": "div.new_list li",
            "title_selector": "a",
            "link_selector": "a",
            "date_selector": "span",
            "date_format": "%Y-%m-%d"
        },
        {
            "name": "教育部官网",
            "url": "http://www.moe.gov.cn/jyb_xwfb/",
            "selector": "ul.list li",
            "title_selector": "a",
            "link_selector": "a",
            "date_selector": "span.date",
            "date_format": "%Y-%m-%d"
        }
    ]
    
    # 兴趣关键词配置
    INTEREST_KEYWORDS = {
        "教育政策": ["教育改革", "教育政策", "义务教育", "教育部", "新政策"],
        "教学方法": ["教学方法", "教学策略", "课堂教学", "教学模式", "教学创新"],
        "教育科技": ["教育科技", "在线教育", "人工智能", "智慧课堂", "教育信息化"],
        "考试升学": ["高考", "中考", "升学", "考试", "招生"],
        "素质教育": ["素质教育", "综合素质", "创新能力", "实践能力", "课外活动"]
    }
    
    def __init__(self):
        """初始化新闻服务"""
        self.logger = logging.getLogger(__name__)
        self.last_update = None
        self.update_interval = 3600  # 默认每小时更新一次
        self.scheduled_thread = None
        self.is_updating = False
        self.db = None
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        ]
        
    def _ensure_indexes(self):
        """确保创建必要的索引"""
        try:
            db = self.connect_db()
            if db:
                db.news.create_index([("title", "text"), ("summary", "text")])
                db.news.create_index("category")
                db.news.create_index("published_at")
                db.news.create_index("source")
                db.news.create_index("pushed")
        except Exception as e:
            self.logger.error(f"创建新闻索引失败: {str(e)}")
    
    def _scheduled_update(self):
        """定期更新新闻的线程方法"""
        while not self.stop_thread:
            try:
                self.fetch_all_news()
                # 每6小时更新一次
                for i in range(6 * 60 * 60):
                    if self.stop_thread:
                        break
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"定期更新新闻失败: {str(e)}")
                # 失败后等待30分钟再试
                time.sleep(30 * 60)
    
    def stop(self):
        """停止自动更新线程"""
        self.stop_thread = True
        if self.update_thread:
            self.update_thread.join(timeout=1)
    
    def fetch_all_news(self):
        """从所有配置的源获取新闻"""
        for source in self.NEWS_SOURCES:
            try:
                self.fetch_news_from_source(source)
            except Exception as e:
                self.logger.error(f"从 {source['name']} 获取新闻失败: {str(e)}")
    
    def fetch_news_from_source(self, source):
        """
        从指定源获取新闻
        
        Args:
            source: 新闻源配置
        """
        self.logger.info(f"正在从 {source['name']} 获取新闻...")
        
        try:
            # 获取HTML内容
            response = requests.get(source['url'], timeout=10)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻条目
            news_items = soup.select(source['selector'])
            
            count = 0
            for item in news_items:
                # 提取新闻标题和链接
                title_elem = item.select_one(source['title_selector'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                
                # 提取链接
                link_elem = item.select_one(source['link_selector'])
                if not link_elem or not link_elem.has_attr('href'):
                    continue
                    
                link = link_elem['href']
                # 处理相对URL
                if not link.startswith('http'):
                    if link.startswith('/'):
                        base_url = '/'.join(source['url'].split('/')[:3])
                        link = base_url + link
                    else:
                        link = source['url'] + link
                
                # 提取日期
                date_elem = item.select_one(source['date_selector'])
                if date_elem:
                    date_text = date_elem.get_text().strip()
                    try:
                        # 提取日期文本中的日期部分
                        date_match = re.search(r'\d{4}-\d{1,2}-\d{1,2}', date_text)
                        if date_match:
                            date_text = date_match.group(0)
                        published_date = datetime.strptime(date_text, source['date_format'])
                    except Exception:
                        # 日期解析失败，使用当前日期
                        published_date = datetime.now()
                else:
                    published_date = datetime.now()
                
                # 获取新闻摘要和分类
                summary, category = self._fetch_news_details(link, title)
                
                # 保存到数据库
                if self._save_news(title, summary, link, published_date, source['name'], category):
                    count += 1
            
            self.logger.info(f"从 {source['name']} 获取了 {count} 条新闻")
            
        except Exception as e:
            self.logger.error(f"从 {source['name']} 获取新闻时出错: {str(e)}")
            raise
    
    def _fetch_news_details(self, url, title):
        """
        获取新闻详情
        
        Args:
            url: 新闻链接
            title: 新闻标题
            
        Returns:
            summary: 新闻摘要
            category: 新闻分类
        """
        summary = ""
        category = "其他"
        
        try:
            # 获取HTML内容
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试提取文章正文
            content_selectors = [
                "div.article-content", "div.TRS_Editor", "div.content",
                "article", "div.text", "div.article-text", "div.article"
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if content:
                # 提取段落
                paragraphs = content.find_all('p')
                if paragraphs:
                    # 使用前3段作为摘要
                    summary_text = []
                    for p in paragraphs[:3]:
                        text = p.get_text().strip()
                        if text and len(text) > 10:  # 排除太短的段落
                            summary_text.append(text)
                    
                    summary = ' '.join(summary_text)
                    if len(summary) > 500:
                        summary = summary[:497] + '...'
            
            # 如果没有找到正文或摘要为空，使用标题作为摘要
            if not summary:
                summary = f"这是关于 {title} 的新闻报道。"
            
            # 根据标题和摘要分析分类
            category = self._categorize_news(title, summary)
            
        except Exception as e:
            self.logger.warning(f"获取新闻详情失败: {str(e)}")
        
        return summary, category
    
    def _categorize_news(self, title, summary):
        """
        根据标题和摘要对新闻进行分类
        
        Args:
            title: 新闻标题
            summary: 新闻摘要
            
        Returns:
            category: 新闻分类
        """
        text = title + " " + summary
        
        # 计算各分类的匹配得分
        scores = {}
        for category, keywords in self.INTEREST_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                scores[category] = score
        
        # 选择得分最高的分类
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # 默认分类
        return "其他"
    
    def _save_news(self, title, summary, link, published_date, source, category):
        """
        保存新闻到数据库
        
        Args:
            title: 新闻标题
            summary: 新闻摘要
            link: 新闻链接
            published_date: 发布日期
            source: 新闻来源
            category: 新闻分类
            
        Returns:
            success: 是否成功保存
        """
        # 检查新闻是否已存在
        existing = self.db.news.find_one({"link": link})
        if existing:
            return False
        
        # 创建新闻文档
        news = {
            "title": title,
            "summary": summary,
            "link": link,
            "published_date": published_date,
            "source": source,
            "category": category,
            "is_pushed": False,
            "push_count": 0,
            "created_at": datetime.now()
        }
        
        # 保存到数据库
        self.db.news.insert_one(news)
        return True
    
    def get_news_by_category(self, category=None, limit=20, skip=0):
        """
        获取特定分类的新闻
        
        Args:
            category: 新闻分类，为None则获取所有分类
            limit: 返回条数限制
            skip: 跳过条数
            
        Returns:
            news_list: 新闻列表
        """
        query = {}
        if category and category != "all":
            query["category"] = category
        
        # 按发布日期降序排序
        cursor = self.db.news.find(query).sort("published_date", -1).skip(skip).limit(limit)
        
        news_list = []
        for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        
        return news_list
    
    def search_news(self, query, limit=20, skip=0):
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            limit: 返回条数限制
            skip: 跳过条数
            
        Returns:
            news_list: 新闻列表
        """
        if not query:
            return self.get_news_by_category(limit=limit, skip=skip)
        
        # 使用文本索引搜索
        cursor = self.db.news.find(
            {"$text": {"$search": query}}
        ).sort([
            ("score", {"$meta": "textScore"}),
            ("published_date", -1)
        ]).skip(skip).limit(limit)
        
        news_list = []
        for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        
        return news_list
    
    def get_news_categories(self):
        """
        获取所有新闻分类
        
        Returns:
            categories: 分类列表
        """
        # 获取系统预定义的分类
        predefined = list(self.INTEREST_KEYWORDS.keys())
        
        # 从数据库中获取实际使用的分类
        cursor = self.db.news.distinct("category")
        db_categories = list(cursor)
        
        # 合并并去重
        all_categories = predefined + [c for c in db_categories if c not in predefined]
        return sorted(all_categories)
    
    def get_recent_news(self, days=7, limit=10):
        """
        获取最近的新闻
        
        Args:
            days: 天数，获取几天内的新闻
            limit: 返回条数限制
            
        Returns:
            news_list: 新闻列表
        """
        start_date = datetime.now() - timedelta(days=days)
        
        cursor = self.db.news.find({
            "published_date": {"$gte": start_date}
        }).sort("published_date", -1).limit(limit)
        
        news_list = []
        for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        
        return news_list
    
    def get_user_recommended_news(self, user_id, limit=10):
        """
        获取推荐给特定用户的新闻
        
        Args:
            user_id: 用户ID
            limit: 返回条数限制
            
        Returns:
            news_list: 新闻列表
        """
        # 获取用户兴趣
        user = self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user or not user.get("interests"):
            # 如果用户没有设置兴趣，返回最近的新闻
            return self.get_recent_news(limit=limit)
        
        # 根据用户兴趣搜索新闻
        interests = user.get("interests", [])
        
        # 构建查询条件
        query = {
            "$or": [
                {"category": {"$in": interests}},
                {"$text": {"$search": " ".join(interests)}}
            ]
        }
        
        # 查询并按相关性和日期排序
        cursor = self.db.news.find(query).sort([
            ("published_date", -1)
        ]).limit(limit * 2)  # 先获取更多，然后进行二次排序
        
        # 转换为列表
        candidates = []
        for news in cursor:
            news["_id"] = str(news["_id"])
            
            # 计算相关性分数
            relevance = 0
            if news["category"] in interests:
                relevance += 2
            
            for interest in interests:
                if interest.lower() in news["title"].lower():
                    relevance += 1
                if interest.lower() in news["summary"].lower():
                    relevance += 0.5
            
            news["relevance"] = relevance
            candidates.append(news)
        
        # 根据相关性排序
        candidates.sort(key=lambda x: (x["relevance"], x["published_date"]), reverse=True)
        
        # 添加一些随机性，避免推荐过于单一
        if len(candidates) > limit:
            # 将候选列表分为高相关性和低相关性两部分
            high_relevance = candidates[:int(limit * 0.7)]
            low_relevance = candidates[int(limit * 0.7):]
            
            # 随机选择一些低相关性的新闻
            random.shuffle(low_relevance)
            selected = high_relevance + low_relevance[:limit - len(high_relevance)]
            
            # 重新按发布日期排序
            selected.sort(key=lambda x: x["published_date"], reverse=True)
            return selected[:limit]
        
        return candidates[:limit]
    
    def mark_news_as_pushed(self, news_id):
        """
        标记新闻为已推送
        
        Args:
            news_id: 新闻ID
        """
        self.db.news.update_one(
            {"_id": ObjectId(news_id)},
            {"$set": {"is_pushed": True}, "$inc": {"push_count": 1}}
        )
    
    def get_unpushed_news(self, limit=10):
        """
        获取未推送的新闻
        
        Args:
            limit: 返回条数限制
            
        Returns:
            news_list: 新闻列表
        """
        cursor = self.db.news.find({
            "is_pushed": False
        }).sort("published_date", -1).limit(limit)
        
        news_list = []
        for news in cursor:
            news["_id"] = str(news["_id"])
            news_list.append(news)
        
        return news_list
    
    def get_random_user_agent(self):
        """获取随机User-Agent"""
        return random.choice(self.user_agent_list)
        
    def connect_db(self):
        """连接到MongoDB数据库"""
        if self.db is not None:
            return self.db
            
        try:
            from flask import current_app
            self.db = current_app.mongo_client.news
            # 确保索引存在
            self.db.news.create_index([("url", 1)], unique=True)
            self.db.news.create_index([("published_at", -1)])
            self.db.news.create_index([("category", 1)])
            return self.db
        except Exception as e:
            self.logger.error(f"连接数据库时出错: {str(e)}")
            return None
            
    def fetch_toutiao_news(self, category="教育", max_pages=3):
        """
        从今日头条抓取教育类新闻
        
        Args:
            category: 新闻类别，默认为教育
            max_pages: 最大抓取页数
            
        Returns:
            news_list: 抓取到的新闻列表
        """
        self.logger.info(f"开始从今日头条抓取{category}新闻")
        news_list = []
        
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.toutiao.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        try:
            # 抓取列表页
            for page in range(1, max_pages + 1):
                # 构造URL - 注意这里使用的是搜索接口
                search_url = f"https://so.toutiao.com/search?keyword={category}"
                if page > 1:
                    search_url += f"&page={page}"
                
                self.logger.debug(f"抓取页面: {search_url}")
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    self.logger.warning(f"页面抓取失败: {response.status_code}")
                    continue
                
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                article_elements = soup.select('div.result-content')
                
                if not article_elements:
                    self.logger.warning(f"未找到文章元素，可能需要更新选择器")
                    # 尝试另一种选择器
                    article_elements = soup.select('div.cs-card-content')
                
                if not article_elements:
                    self.logger.warning("未找到任何文章元素，页面结构可能已变化")
                    continue
                
                # 提取文章信息
                for article in article_elements:
                    try:
                        # 尝试不同的选择器组合来适应可能的页面结构
                        title_elem = article.select_one('a.cs-link-title') or article.select_one('div.title-box')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # 尝试获取链接
                        link_elem = article.select_one('a.cs-link-title') or article.select_one('a.link')
                        if not link_elem or not link_elem.has_attr('href'):
                            continue
                            
                        url = link_elem['href']
                        if url.startswith('//'):
                            url = 'https:' + url
                        elif not url.startswith('http'):
                            url = 'https://www.toutiao.com' + url
                        
                        # 尝试获取发布时间
                        time_elem = article.select_one('.cs-source-time') or article.select_one('.src-time')
                        published_time = time_elem.get_text(strip=True) if time_elem else '刚刚'
                        
                        # 转换时间格式
                        now = datetime.datetime.now()
                        if '刚刚' in published_time:
                            published_at = now
                        elif '分钟前' in published_time:
                            minutes = int(re.findall(r'(\d+)', published_time)[0])
                            published_at = now - datetime.timedelta(minutes=minutes)
                        elif '小时前' in published_time:
                            hours = int(re.findall(r'(\d+)', published_time)[0])
                            published_at = now - datetime.timedelta(hours=hours)
                        elif '昨天' in published_time:
                            published_at = now - datetime.timedelta(days=1)
                        else:
                            # 尝试解析日期格式
                            try:
                                published_at = datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M')
                            except:
                                published_at = now
                        
                        # 获取文章详情
                        article_content, summary = self.fetch_article_content(url, headers)
                        if not article_content:
                            summary = title  # 如果无法获取内容，使用标题作为摘要
                        
                        # 使用AI进行分类
                        category_result, success = ai_service.classify_news(title, article_content[:500] if article_content else title)
                        if not success:
                            category_result = "教育资讯"  # 默认分类
                        
                        news_item = {
                            'title': title,
                            'url': url,
                            'summary': summary,
                            'content': article_content,
                            'source': '今日头条',
                            'category': category_result,
                            'published_at': published_at,
                            'created_at': datetime.datetime.now(),
                            'pushed': False
                        }
                        
                        news_list.append(news_item)
                        self.logger.debug(f"抓取到新闻: {title}")
                        
                        # 随机延迟，避免请求过于密集
                        time.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        self.logger.error(f"处理文章时出错: {str(e)}")
                        continue
                
                # 页面间随机延迟
                time.sleep(random.uniform(3, 5))
            
            self.logger.info(f"成功抓取{len(news_list)}条新闻")
            return news_list
            
        except Exception as e:
            self.logger.error(f"抓取今日头条新闻时出错: {str(e)}")
            return []
    
    def fetch_article_content(self, url, headers):
        """
        抓取文章详情内容
        
        Args:
            url: 文章URL
            headers: 请求头
            
        Returns:
            content: 文章内容
            summary: 文章摘要
        """
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return "", ""
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种选择器来适应不同的页面结构
            content_elem = (
                soup.select_one('div.article-content') or 
                soup.select_one('div.content') or 
                soup.select_one('div.article-box') or
                soup.select_one('article')
            )
            
            if not content_elem:
                return "", ""
            
            # 提取正文内容
            paragraphs = content_elem.select('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            
            # 如果没有找到段落，尝试直接获取文本
            if not content:
                content = content_elem.get_text(strip=True)
            
            # 生成摘要（取前100个字）
            summary = content[:100] + '...' if len(content) > 100 else content
            
            return content, summary
            
        except Exception as e:
            self.logger.error(f"抓取文章内容时出错: {str(e)}")
            return "", ""
    
    def update_news(self):
        """更新新闻数据"""
        if self.is_updating:
            self.logger.info("新闻更新任务已在进行中")
            return False
            
        self.is_updating = True
        self.logger.info("开始更新新闻数据")
        
        try:
            # 连接数据库
            db = self.connect_db()
            if db is None:
                self.logger.error("无法连接到数据库，取消新闻更新")
                self.is_updating = False
                return False
            
            # 抓取今日头条教育新闻
            news_list = self.fetch_toutiao_news()
            
            if not news_list:
                self.logger.warning("未抓取到任何新闻，取消更新")
                self.is_updating = False
                return False
            
            # 保存到数据库
            insert_count = 0
            for news in news_list:
                try:
                    db.news.update_one(
                        {'url': news['url']},
                        {'$setOnInsert': news},
                        upsert=True
                    )
                    insert_count += 1
                except Exception as e:
                    self.logger.error(f"保存新闻时出错: {str(e)}")
            
            self.last_update = datetime.datetime.now()
            self.logger.info(f"新闻更新完成，新增{insert_count}条新闻")
            
            # 更新完成后，使用AI总结最新新闻
            self.generate_news_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新新闻时出错: {str(e)}")
            return False
        finally:
            self.is_updating = False
    
    def schedule_update(self, interval=3600):
        """
        计划定时更新新闻
        
        Args:
            interval: 更新间隔（秒）
        """
        def update_job():
            from flask import current_app
            while True:
                try:
                    with current_app.app_context():
                        self.update_news()
                except Exception as e:
                    self.logger.error(f"定时更新新闻时出错: {str(e)}")
                time.sleep(interval)
        
        self.update_interval = interval
        
        # 停止现有的线程
        if self.scheduled_thread and self.scheduled_thread.is_alive():
            self.logger.info("停止现有的新闻更新线程")
            # 无法直接停止线程，但下次循环不会再继续
        
        # 启动新线程
        self.scheduled_thread = threading.Thread(target=update_job, daemon=True)
        self.scheduled_thread.start()
        self.logger.info(f"已启动新闻自动更新，间隔{interval}秒")
    
    def get_recommended_news(self, user_id, limit=5):
        """
        为用户推荐新闻
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            news_list: 新闻列表
        """
        try:
            db = self.connect_db()
            if db is None:
                return []
            
            # 尝试获取用户兴趣
            user_interests = self.get_user_interests(user_id)
            
            if not user_interests:
                # 如果没有用户兴趣数据，返回最新新闻
                return self.get_recent_news(days=3, limit=limit)
            
            # 根据用户兴趣构建查询
            search_condition = {
                '$or': [
                    {'category': {'$in': user_interests}},
                    {'title': {'$regex': '|'.join(user_interests), '$options': 'i'}},
                    {'summary': {'$regex': '|'.join(user_interests), '$options': 'i'}}
                ]
            }
            
            cursor = db.news.find(search_condition).sort('published_at', DESCENDING).limit(limit)
            
            news_list = list(cursor)
            # 如果根据兴趣没有足够的新闻，补充最新新闻
            if len(news_list) < limit:
                recent_news = self.get_recent_news(days=3, limit=limit-len(news_list))
                # 避免重复
                existing_ids = [str(news.get('_id')) for news in news_list]
                for news in recent_news:
                    if str(news.get('_id')) not in existing_ids:
                        news_list.append(news)
            
            # 转换日期格式
            for news in news_list:
                if 'published_at' in news:
                    news['published_at'] = news['published_at'].strftime('%Y-%m-%d %H:%M:%S')
                if 'created_at' in news:
                    news['created_at'] = news['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                # 去除MongoDB的_id
                if '_id' in news:
                    news['id'] = str(news['_id'])
                    del news['_id']
            
            return news_list
            
        except Exception as e:
            self.logger.error(f"获取推荐新闻时出错: {str(e)}")
            return []
    
    def get_user_interests(self, user_id):
        """
        获取用户兴趣
        
        Args:
            user_id: 用户ID
            
        Returns:
            interests: 兴趣列表
        """
        try:
            db = self.connect_db()
            if db is None:
                return []
            
            # 查询用户记录
            user = db.users.find_one({'_id': user_id})
            if not user or 'interests' not in user:
                return []
            
            return user['interests']
            
        except Exception as e:
            self.logger.error(f"获取用户兴趣时出错: {str(e)}")
            return []
    
    def generate_news_summary(self):
        """
        生成新闻摘要
        
        Returns:
            summary: 摘要文本
            categories: 涉及的分类
        """
        try:
            # 获取最近一天的新闻
            news_list = self.get_recent_news(days=1, limit=10)
            
            if not news_list:
                return "今日暂无教育新闻更新。", []
            
            # 调用AI服务生成摘要
            summary, categories, success = ai_service.summarize_news(news_list)
            
            if not success:
                return "新闻摘要生成失败。", []
            
            # 保存摘要到数据库
            db = self.connect_db()
            if db is not None:
                db.news_summaries.insert_one({
                    'summary': summary,
                    'categories': categories,
                    'news_count': len(news_list),
                    'created_at': datetime.datetime.now()
                })
            
            return summary, categories
            
        except Exception as e:
            self.logger.error(f"生成新闻摘要时出错: {str(e)}")
            return "生成新闻摘要时出错。", []

# 创建单例实例
news_service = NewsService() 