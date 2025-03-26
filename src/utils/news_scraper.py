import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
from typing import List, Dict, Any, Optional

# 设置日志
logger = logging.getLogger(__name__)

class NewsScraperError(Exception):
    """新闻爬虫自定义异常"""
    pass

class NewsItem:
    """新闻条目数据类"""
    def __init__(self, title: str, url: str, source: str, date: str, summary: Optional[str] = None):
        self.title = title
        self.url = url
        self.source = source
        self.date = date
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，方便JSON序列化"""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'date': self.date,
            'summary': self.summary
        }

class NewsScraper:
    """教育新闻爬虫"""
    
    # 支持的新闻源
    SOURCES = {
        'edu': {
            'name': '中国教育部',
            'url': 'http://www.moe.gov.cn/jyb_xwfb/s5147/list.htm',
            'encoding': 'utf-8'
        },
        'higher_edu': {
            'name': '高等教育',
            'url': 'http://www.moe.gov.cn/s78/A08/gjs_left/s3704/s6145/s6147/s6148/',
            'encoding': 'utf-8'
        },
        'k12': {
            'name': '基础教育',
            'url': 'http://www.moe.gov.cn/s78/A06/index.html',
            'encoding': 'utf-8'
        },
        'people_edu': {
            'name': '人民网教育',
            'url': 'http://edu.people.com.cn/GB/index.html',
            'encoding': 'GB2312'
        },
        'sina_edu': {
            'name': '新浪教育',
            'url': 'https://edu.sina.com.cn/',
            'encoding': 'utf-8'
        }
    }
    
    def __init__(self, timeout: int = 10, use_proxy: bool = False):
        """
        初始化新闻爬虫
        
        Args:
            timeout: 请求超时时间（秒）
            use_proxy: 是否使用代理（暂未实现）
        """
        self.timeout = timeout
        self.use_proxy = use_proxy
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 模拟数据，用于演示模式
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """生成模拟数据用于演示"""
        return {
            'edu': [
                {
                    'title': '教育部发布2023年全国教育事业发展统计公报',
                    'url': 'http://www.moe.gov.cn/jyb_xwfb/s5147/202307/t20230728_673517.html',
                    'source': '中国教育部',
                    'date': '2023-07-28',
                    'summary': '教育部今日发布2023年全国教育事业发展统计公报，公报显示，2022年全国教育经费总投入为58382亿元，比上年增长5.5%。'
                },
                {
                    'title': '教育部部署2023年秋季学期中小学教育教学工作',
                    'url': 'http://www.moe.gov.cn/jyb_xwfb/s5147/202308/t20230825_675438.html',
                    'source': '中国教育部',
                    'date': '2023-08-25',
                    'summary': '教育部今日发布通知，部署2023年秋季学期中小学教育教学工作，强调要深入落实"双减"政策，推进义务教育优质均衡发展。'
                },
                {
                    'title': '全国高校教师教学创新大赛成功举办',
                    'url': 'http://www.moe.gov.cn/jyb_xwfb/s5147/202309/t20230910_677219.html',
                    'source': '中国教育部',
                    'date': '2023-09-10',
                    'summary': '由教育部主办的第三届全国高校教师教学创新大赛日前成功举办，来自全国各地的高校教师展示了创新教学成果。'
                }
            ],
            'higher_edu': [
                {
                    'title': '高校创新创业教育改革取得新进展',
                    'url': 'http://www.moe.gov.cn/s78/A08/gjs_left/s3704/s6145/s6147/s6148/202307/t20230715_672561.html',
                    'source': '高等教育',
                    'date': '2023-07-15',
                    'summary': '教育部发布通报显示，全国高校创新创业教育改革成效显著，2022年大学生创业率达到3.5%，比上年提高0.5个百分点。'
                },
                {
                    'title': '关于实施"高校科技创新能力提升计划"的通知',
                    'url': 'http://www.moe.gov.cn/s78/A08/gjs_left/s3704/s6145/s6147/s6148/202308/t20230802_674231.html',
                    'source': '高等教育',
                    'date': '2023-08-02',
                    'summary': '为促进高校科技创新能力提升，教育部、科技部联合启动"高校科技创新能力提升计划"，支持高校开展原创性、引领性科研。'
                }
            ],
            'k12': [
                {
                    'title': '教育部印发义务教育课程方案和课程标准（2023年修订版）',
                    'url': 'http://www.moe.gov.cn/s78/A06/202307/t20230720_673011.html',
                    'source': '基础教育',
                    'date': '2023-07-20',
                    'summary': '教育部印发义务教育课程方案和课程标准（2023年修订版），进一步优化了课程结构，强化了劳动教育。'
                },
                {
                    'title': '全国中小学生校外培训监管平台正式上线',
                    'url': 'http://www.moe.gov.cn/s78/A06/202308/t20230810_675022.html',
                    'source': '基础教育',
                    'date': '2023-08-10',
                    'summary': '教育部宣布全国中小学生校外培训监管平台正式上线，将进一步规范校外培训机构行为，减轻学生课外负担。'
                }
            ],
            'people_edu': [
                {
                    'title': '2023年全国高考录取工作基本结束',
                    'url': 'http://edu.people.com.cn/n1/2023/0825/c1053-32726584.html',
                    'source': '人民网教育',
                    'date': '2023-08-25',
                    'summary': '教育部通报，2023年全国高考录取工作已基本结束，共录取新生755.5万人，比去年增加5.3万人。'
                },
                {
                    'title': '教育部公布2023年全国教书育人楷模名单',
                    'url': 'http://edu.people.com.cn/n1/2023/0909/c1053-32731476.html',
                    'source': '人民网教育',
                    'date': '2023-09-09',
                    'summary': '在第39个教师节来临之际，教育部公布了2023年全国教书育人楷模名单，共10名教师获此殊荣。'
                }
            ],
            'sina_edu': [
                {
                    'title': '国家教育数字化战略行动启动实施',
                    'url': 'https://edu.sina.com.cn/zxx/2023-07-18/doc-imsxuwst9862541.shtml',
                    'source': '新浪教育',
                    'date': '2023-07-18',
                    'summary': '教育部等九部门联合发布通知，启动实施国家教育数字化战略行动，促进信息技术与教育教学融合创新。'
                },
                {
                    'title': '2023届高校毕业生就业质量报告发布',
                    'url': 'https://edu.sina.com.cn/gaokao/2023-08-20/doc-imsxuwus3459875.shtml',
                    'source': '新浪教育',
                    'date': '2023-08-20',
                    'summary': '教育部发布2023届高校毕业生就业质量报告，就业率达91.6%，较去年同期提高1.2个百分点。'
                }
            ]
        }
    
    def fetch_news(self, source: str = 'edu', limit: int = 10, page: int = 1, demo_mode: bool = True) -> List[Dict[str, Any]]:
        """
        获取指定来源的教育新闻
        
        Args:
            source: 新闻源，支持的值包括'edu', 'higher_edu', 'k12', 'people_edu', 'sina_edu'
            limit: 返回的新闻条目数量
            page: 页码
            demo_mode: 是否使用演示模式
            
        Returns:
            新闻条目列表
        """
        source = source.lower()
        if source not in self.SOURCES:
            raise NewsScraperError(f"不支持的新闻源: {source}")
        
        try:
            # 演示模式返回模拟数据
            if demo_mode:
                logger.info(f"使用演示模式获取新闻，源: {source}")
                return self.mock_data.get(source, [])[:limit]
            
            # 实际爬取新闻
            news_source = self.SOURCES[source]
            url = news_source['url']
            encoding = news_source['encoding']
            
            logger.info(f"正在从 {url} 获取新闻")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = encoding
            
            if response.status_code != 200:
                logger.error(f"请求失败: {response.status_code}")
                raise NewsScraperError(f"请求失败，状态码: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据不同来源解析新闻
            if source == 'edu':
                return self._parse_edu_news(soup, limit)
            elif source == 'higher_edu':
                return self._parse_higher_edu_news(soup, limit)
            elif source == 'k12':
                return self._parse_k12_news(soup, limit)
            elif source == 'people_edu':
                return self._parse_people_edu_news(soup, limit)
            elif source == 'sina_edu':
                return self._parse_sina_edu_news(soup, limit)
            
        except requests.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            raise NewsScraperError(f"网络请求异常: {str(e)}")
        except Exception as e:
            logger.error(f"爬取新闻失败: {str(e)}")
            raise NewsScraperError(f"爬取新闻失败: {str(e)}")
    
    def _parse_edu_news(self, soup: BeautifulSoup, limit: int) -> List[Dict[str, Any]]:
        """解析教育部官网新闻"""
        news_items = []
        try:
            news_list = soup.select('.wp_article_list .list_item')
            for item in news_list[:limit]:
                title_elem = item.select_one('.Article_Title a')
                date_elem = item.select_one('.Article_PublishDate')
                
                if title_elem and date_elem:
                    title = title_elem.text.strip()
                    url = title_elem['href']
                    # 处理相对URL
                    if not url.startswith('http'):
                        url = 'http://www.moe.gov.cn' + url
                    
                    date = date_elem.text.strip()
                    
                    news_item = NewsItem(
                        title=title,
                        url=url,
                        source=self.SOURCES['edu']['name'],
                        date=date
                    )
                    news_items.append(news_item.to_dict())
            
            logger.info(f"成功解析教育部新闻 {len(news_items)} 条")
            return news_items
        except Exception as e:
            logger.error(f"解析教育部新闻失败: {str(e)}")
            return []
    
    def _parse_higher_edu_news(self, soup: BeautifulSoup, limit: int) -> List[Dict[str, Any]]:
        """解析高等教育新闻"""
        # 实际实现类似于_parse_edu_news
        # 为简化示例，这里返回模拟数据
        return self.mock_data.get('higher_edu', [])[:limit]
    
    def _parse_k12_news(self, soup: BeautifulSoup, limit: int) -> List[Dict[str, Any]]:
        """解析基础教育新闻"""
        # 实际实现类似于_parse_edu_news
        # 为简化示例，这里返回模拟数据
        return self.mock_data.get('k12', [])[:limit]
    
    def _parse_people_edu_news(self, soup: BeautifulSoup, limit: int) -> List[Dict[str, Any]]:
        """解析人民网教育新闻"""
        # 实际实现类似于_parse_edu_news
        # 为简化示例，这里返回模拟数据
        return self.mock_data.get('people_edu', [])[:limit]
    
    def _parse_sina_edu_news(self, soup: BeautifulSoup, limit: int) -> List[Dict[str, Any]]:
        """解析新浪教育新闻"""
        # 实际实现类似于_parse_edu_news
        # 为简化示例，这里返回模拟数据
        return self.mock_data.get('sina_edu', [])[:limit]
    
    def get_news_summary(self, url: str) -> Optional[str]:
        """
        获取新闻摘要
        
        Args:
            url: 新闻URL
            
        Returns:
            新闻摘要
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logger.error(f"请求失败: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试提取新闻内容的第一段作为摘要
            content = soup.select_one('.TRS_Editor p, .article-content p, .article p')
            if content:
                summary = content.text.strip()
                # 限制摘要长度
                if len(summary) > 200:
                    summary = summary[:197] + '...'
                return summary
            
            return None
        except Exception as e:
            logger.error(f"获取新闻摘要失败: {str(e)}")
            return None


def demo():
    """演示如何使用新闻爬虫"""
    scraper = NewsScraper()
    
    # 获取教育部新闻
    print("获取教育部新闻:")
    edu_news = scraper.fetch_news(source='edu', limit=3, demo_mode=True)
    for i, news in enumerate(edu_news, 1):
        print(f"{i}. {news['title']} ({news['date']})")
        print(f"   来源: {news['source']}")
        print(f"   链接: {news['url']}")
        if news['summary']:
            print(f"   摘要: {news['summary']}")
        print()
    
    # 获取高等教育新闻
    print("\n获取高等教育新闻:")
    higher_edu_news = scraper.fetch_news(source='higher_edu', limit=2, demo_mode=True)
    for i, news in enumerate(higher_edu_news, 1):
        print(f"{i}. {news['title']} ({news['date']})")
        print(f"   来源: {news['source']}")
        print(f"   链接: {news['url']}")
        if news['summary']:
            print(f"   摘要: {news['summary']}")
        print()


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行演示
    demo() 