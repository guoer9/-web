#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import time
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsScraper:
    """提供教育新闻信息的爬虫服务"""
    
    def __init__(self):
        """初始化新闻爬虫服务"""
        self.sources = [
            {"key": "edu", "name": "教育部新闻"},
            {"key": "china_edu", "name": "中国教育新闻网"},
            {"key": "people_edu", "name": "人民教育"},
            {"key": "xinhua_edu", "name": "新华教育"},
            {"key": "local_edu", "name": "地方教育资讯"}
        ]
        
        # 模拟数据
        self.sample_news = [
            {
                "title": "教育部发布新版义务教育课程标准",
                "url": "https://example.com/news/1",
                "source": "教育部新闻",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "教育部今日发布新版义务教育课程标准，着重强调学生核心素养培养，将于下学期正式实施。新标准更加注重学生创新思维和实践能力的培养。"
            },
            {
                "title": "全国教师教育改革创新经验交流会召开",
                "url": "https://example.com/news/2",
                "source": "中国教育新闻网",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "summary": "全国教师教育改革创新经验交流会在北京召开，来自全国各地的教育专家和一线教师代表分享了教育教学改革的新理念和有效做法。"
            },
            {
                "title": "国际教育评估显示中国学生数学成绩领先",
                "url": "https://example.com/news/3",
                "source": "人民教育",
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "最新一期国际学生评估项目(PISA)测试结果显示，中国学生在数学领域表现优异，但批判性思维和创新能力仍有提升空间。"
            },
            {
                "title": "多地出台政策鼓励校企合作培养职业技能人才",
                "url": "https://example.com/news/4",
                "source": "新华教育",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "summary": "全国多地教育部门出台新政策，鼓励职业院校与企业深度合作，共同培养适应产业需求的高技能人才，推动职业教育高质量发展。"
            },
            {
                "title": "教育大数据助力个性化学习成为新趋势",
                "url": "https://example.com/news/5",
                "source": "中国教育新闻网",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "随着教育信息化程度的提高，基于大数据分析的个性化学习方案正在全国范围内推广，帮助学生根据自身情况制定学习计划。"
            },
            {
                "title": "全国青少年科技创新大赛圆满结束",
                "url": "https://example.com/news/6",
                "source": "教育部新闻",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "第37届全国青少年科技创新大赛在上海落下帷幕，共有来自全国各地的1500多名青少年参与角逐，展示了创新项目和科研成果。"
            },
            {
                "title": "中小学心理健康教育全面推进",
                "url": "https://example.com/news/7",
                "source": "人民教育",
                "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                "summary": "教育部要求全国中小学配备专业心理健康教师，开设心理健康课程，建立学生心理档案，关注学生心理健康发展。"
            },
            {
                "title": "在线教育平台融资热度不减",
                "url": "https://example.com/news/8",
                "source": "新华教育",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "尽管疫情影响减弱，但在线教育平台依然保持高速发展，多家教育科技企业完成新一轮融资，市场规模持续扩大。"
            },
            {
                "title": "教育部严格规范校外培训机构管理",
                "url": "https://example.com/news/9",
                "source": "教育部新闻",
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "summary": "教育部发布新规，进一步规范校外培训机构的管理，要求培训机构不得占用国家法定节假日、休息日及寒暑假期组织学科类培训。"
            },
            {
                "title": "农村教育振兴计划取得显著成效",
                "url": "https://example.com/news/10",
                "source": "人民教育",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "summary": "近年来，通过实施农村教育振兴计划，农村学校办学条件得到显著改善，城乡教育差距逐步缩小，农村教师队伍建设加强。"
            },
            {
                "title": "高校科研创新能力评估报告发布",
                "url": "https://example.com/news/11",
                "source": "中国教育新闻网",
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "2023年度高校科研创新能力评估报告显示，国内高校在人工智能、生物医药等前沿领域取得重要突破，国际影响力不断提升。"
            },
            {
                "title": "教育部公布首批数字教育示范区名单",
                "url": "https://example.com/news/12",
                "source": "新华教育",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "教育部公布首批20个数字教育示范区名单，将在这些地区率先推进数字教育体系建设，探索智能化教学新模式。"
            },
            {
                "title": "新高考改革试点扩大到更多省份",
                "url": "https://example.com/news/13",
                "source": "教育部新闻",
                "date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
                "summary": "教育部宣布新高考改革试点范围将扩大到更多省份，强调\"选课走班\"和综合素质评价，减轻学生负担。"
            },
            {
                "title": "全国教育信息化工作会议在京召开",
                "url": "https://example.com/news/14",
                "source": "地方教育资讯",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "全国教育信息化工作会议在北京召开，会议强调要加快推进教育信息化进程，促进信息技术与教育教学深度融合。"
            },
            {
                "title": "世界读书日：多地学校开展阅读推广活动",
                "url": "https://example.com/news/15",
                "source": "地方教育资讯",
                "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "summary": "在世界读书日到来之际，全国各地学校纷纷开展形式多样的阅读推广活动，培养学生良好的阅读习惯和阅读兴趣。"
            }
        ]
        
        # 为每条新闻生成更多随机属性
        for news in self.sample_news:
            news_source = news["source"]
            for source in self.sources:
                if source["name"] == news_source:
                    news["source_key"] = source["key"]
                    break
            else:
                news["source_key"] = "other"
        
        logger.info("新闻爬虫服务初始化完成")
    
    def get_sources(self):
        """获取支持的新闻源列表"""
        return self.sources
    
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
        logger.info(f"获取新闻列表: source={source}, limit={limit}, page={page}")
        
        # 根据source筛选
        filtered_news = self.sample_news
        if source and source != "all":
            filtered_news = [news for news in self.sample_news if news.get("source_key") == source]
        
        # 计算总数和分页
        total = len(filtered_news)
        start = (page - 1) * limit
        end = start + limit
        paginated_news = filtered_news[start:end]
        
        # 模拟网络延迟
        time.sleep(0.2)
        
        return {
            "list": paginated_news,
            "total": total
        }
    
    def get_news_detail(self, url):
        """
        获取新闻详情
        
        Args:
            url: 新闻URL
        
        Returns:
            dict: 新闻详情信息
        """
        logger.info(f"获取新闻详情: url={url}")
        
        # 查找匹配的新闻
        for news in self.sample_news:
            if news["url"] == url:
                # 生成更详细的摘要
                detailed_summary = news["summary"] + " " + """
                本文详细介绍了相关政策的背景、主要内容和实施时间表。专家认为，这一举措将有效提升教育质量，
                促进教育公平。同时，文章也指出了实施过程中可能面临的挑战和应对策略。教育部门表示，
                将加强监督和指导，确保政策落实到位，并根据实施情况及时调整完善。
                """
                
                # 模拟网络延迟
                time.sleep(0.5)
                
                return {
                    "title": news["title"],
                    "url": news["url"],
                    "source": news["source"],
                    "date": news["date"],
                    "summary": detailed_summary,
                    "content": "新闻全文内容...",  # 实际应用中应提供完整内容
                    "keywords": ["教育", "改革", "创新"]  # 示例关键词
                }
        
        # 未找到匹配的新闻
        logger.warning(f"未找到匹配的新闻: url={url}")
        return None
    
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
        logger.info(f"搜索新闻: query={query}, limit={limit}, page={page}")
        
        if not query:
            return {"list": [], "total": 0}
        
        # 简单的关键词匹配
        matched_news = []
        for news in self.sample_news:
            if (re.search(query, news["title"], re.IGNORECASE) or 
                re.search(query, news["summary"], re.IGNORECASE)):
                matched_news.append(news)
        
        # 计算总数和分页
        total = len(matched_news)
        start = (page - 1) * limit
        end = start + limit
        paginated_news = matched_news[start:end]
        
        # 模拟网络延迟
        time.sleep(0.3)
        
        return {
            "list": paginated_news,
            "total": total
        }
    
    def get_daily_summary(self):
        """
        获取每日教育新闻摘要
        
        Returns:
            str: 新闻摘要文本
        """
        # 随机选择3-5条新闻生成摘要
        selected_news = random.sample(self.sample_news, min(5, len(self.sample_news)))
        titles = [news["title"] for news in selected_news]
        
        summary = f"今日教育热点（{datetime.now().strftime('%Y-%m-%d')}）：\n\n"
        summary += "· " + "\n· ".join(titles)
        summary += "\n\n教育部近期政策动向关注重点：素质教育深化改革、减轻学生负担、推进教育信息化、提升教师队伍素质。"
        
        return summary 