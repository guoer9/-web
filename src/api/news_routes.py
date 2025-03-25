"""
新闻API路由 - 提供新闻查询、推送和管理功能
"""
from flask import Blueprint, request, jsonify, current_app
from services.news_service import news_service
from utils.ai_service import ai_service
import json
from datetime import datetime

news_bp = Blueprint('news', __name__)

@news_bp.route('/recent', methods=['GET'])
def get_recent_news():
    """获取最近新闻"""
    try:
        days = request.args.get('days', default=7, type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        # 参数验证
        if days < 1:
            days = 1
        elif days > 30:
            days = 30
            
        if limit < 1:
            limit = 10
        elif limit > 50:
            limit = 50
            
        news_list = news_service.get_recent_news(days=days, limit=limit)
        
        return jsonify({
            'success': True,
            'data': news_list,
            'count': len(news_list)
        })
    except Exception as e:
        current_app.logger.error(f"获取最近新闻时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"获取最近新闻时出错: {str(e)}"
        }), 500

@news_bp.route('/category/<category>', methods=['GET'])
def get_news_by_category(category):
    """按分类获取新闻"""
    try:
        limit = request.args.get('limit', default=20, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        # 参数验证
        if limit < 1:
            limit = 20
        elif limit > 50:
            limit = 50
            
        if skip < 0:
            skip = 0
            
        news_list = news_service.get_news_by_category(category, limit=limit, skip=skip)
        
        return jsonify({
            'success': True,
            'data': news_list,
            'count': len(news_list)
        })
    except Exception as e:
        current_app.logger.error(f"按分类获取新闻时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"按分类获取新闻时出错: {str(e)}"
        }), 500

@news_bp.route('/search', methods=['GET'])
def search_news():
    """搜索新闻"""
    try:
        query = request.args.get('query', '')
        limit = request.args.get('limit', default=20, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': "搜索关键词不能为空"
            }), 400
            
        # 参数验证
        if limit < 1:
            limit = 20
        elif limit > 50:
            limit = 50
            
        if skip < 0:
            skip = 0
            
        news_list = news_service.search_news(query, limit=limit, skip=skip)
        
        return jsonify({
            'success': True,
            'data': news_list,
            'count': len(news_list)
        })
    except Exception as e:
        current_app.logger.error(f"搜索新闻时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"搜索新闻时出错: {str(e)}"
        }), 500

@news_bp.route('/categories', methods=['GET'])
def get_news_categories():
    """获取新闻分类"""
    try:
        categories = news_service.get_news_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        current_app.logger.error(f"获取新闻分类时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"获取新闻分类时出错: {str(e)}"
        }), 500

@news_bp.route('/recommended/<user_id>', methods=['GET'])
def get_recommended_news(user_id):
    """获取推荐新闻"""
    try:
        limit = request.args.get('limit', default=5, type=int)
        
        # 参数验证
        if limit < 1:
            limit = 5
        elif limit > 20:
            limit = 20
            
        news_list = news_service.get_recommended_news(user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'data': news_list,
            'count': len(news_list)
        })
    except Exception as e:
        current_app.logger.error(f"获取推荐新闻时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"获取推荐新闻时出错: {str(e)}"
        }), 500

@news_bp.route('/push/<news_id>', methods=['POST'])
def mark_news_pushed(news_id):
    """标记新闻为已推送"""
    try:
        result = news_service.mark_news_pushed(news_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': "新闻已标记为已推送"
            })
        else:
            return jsonify({
                'success': False,
                'error': "新闻标记失败，可能不存在"
            }), 404
    except Exception as e:
        current_app.logger.error(f"标记新闻推送状态时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"标记新闻推送状态时出错: {str(e)}"
        }), 500

@news_bp.route('/unpushed', methods=['GET'])
def get_unpushed_news():
    """获取未推送的新闻"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        
        # 参数验证
        if limit < 1:
            limit = 10
        elif limit > 30:
            limit = 30
            
        news_list = news_service.get_unpushed_news(limit=limit)
        
        return jsonify({
            'success': True,
            'data': news_list,
            'count': len(news_list)
        })
    except Exception as e:
        current_app.logger.error(f"获取未推送新闻时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"获取未推送新闻时出错: {str(e)}"
        }), 500

@news_bp.route('/fetch', methods=['POST'])
def fetch_news():
    """手动触发新闻抓取"""
    try:
        # 检查管理员权限
        admin_token = request.headers.get('X-Admin-Token')
        if not admin_token or admin_token != current_app.config.get('ADMIN_TOKEN'):
            return jsonify({
                'success': False,
                'error': "权限不足，需要管理员权限"
            }), 403
            
        # 执行新闻更新
        result = news_service.update_news()
        
        if result:
            return jsonify({
                'success': True,
                'message': "新闻更新任务已启动"
            })
        else:
            return jsonify({
                'success': False,
                'error': "新闻更新任务启动失败"
            }), 500
    except Exception as e:
        current_app.logger.error(f"手动触发新闻抓取时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"手动触发新闻抓取时出错: {str(e)}"
        }), 500

@news_bp.route('/summary', methods=['GET'])
def get_news_summary():
    """获取今日新闻摘要"""
    try:
        summary, categories = news_service.generate_news_summary()
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'categories': categories,
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        current_app.logger.error(f"获取新闻摘要时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"获取新闻摘要时出错: {str(e)}"
        }), 500

@news_bp.route('/analyze/feedback', methods=['POST'])
def analyze_feedback():
    """分析反馈文本"""
    try:
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': "缺少必要的反馈文本"
            }), 400
            
        feedback_text = data['text']
        
        analysis, success = ai_service.analyze_feedback(feedback_text)
        
        if success:
            return jsonify({
                'success': True,
                'data': analysis
            })
        else:
            return jsonify({
                'success': False,
                'error': "反馈分析失败"
            }), 500
    except Exception as e:
        current_app.logger.error(f"分析反馈文本时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"分析反馈文本时出错: {str(e)}"
        }), 500 