#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻API路由 - 提供新闻查询、推送和管理功能
"""
from flask import Blueprint, request, jsonify, current_app
from src.services.news_service import news_service
from src.utils.ai_service import ai_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 创建蓝图
news_bp = Blueprint('news', __name__)

@news_bp.route('/list', methods=['GET'])
def list_news():
    """
    获取新闻列表
    
    查询参数:
    - source: 新闻源，可选
    - page: 页码，默认1
    - limit: 每页数量，默认10
    
    Returns:
        JSON: 新闻列表和分页信息
    """
    try:
        source = request.args.get('source')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 参数验证
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10
        
        result = news_service.get_news_list(source, limit, page)
        
        logger.info(f"获取新闻列表成功: source={source}, page={page}, limit={limit}, count={len(result['list'])}")
        
        return jsonify({
            'code': 200,
            'message': '获取新闻列表成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"获取新闻列表出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        })

@news_bp.route('/sources', methods=['GET'])
def list_sources():
    """
    获取支持的新闻源列表
    
    Returns:
        JSON: 新闻源列表
    """
    try:
        sources = news_service.get_sources()
        
        logger.info(f"获取新闻源列表成功: count={len(sources)}")
        
        return jsonify({
            'code': 200,
            'message': '获取新闻源列表成功',
            'data': sources
        })
    except Exception as e:
        logger.error(f"获取新闻源列表出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        })

@news_bp.route('/detail', methods=['GET'])
def get_news_detail():
    """
    获取新闻详情
    
    查询参数:
    - url: 新闻URL，必填
    
    Returns:
        JSON: 新闻详情
    """
    try:
        url = request.args.get('url')
        
        if not url:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数: url',
                'data': None
            })
        
        result = news_service.get_news_detail(url)
        
        if not result:
            logger.warning(f"未找到指定的新闻: url={url}")
            return jsonify({
                'code': 404,
                'message': '未找到指定的新闻',
                'data': None
            })
        
        logger.info(f"获取新闻详情成功: url={url}")
        
        return jsonify({
            'code': 200,
            'message': '获取新闻详情成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"获取新闻详情出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        })

@news_bp.route('/search', methods=['GET'])
def search_news():
    """
    搜索新闻
    
    查询参数:
    - query: 搜索关键词，必填
    - page: 页码，默认1
    - limit: 每页数量，默认10
    
    Returns:
        JSON: 搜索结果和分页信息
    """
    try:
        query = request.args.get('query')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数: query',
                'data': None
            })
        
        # 参数验证
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10
        
        result = news_service.search_news(query, limit, page)
        
        logger.info(f"搜索新闻成功: query={query}, page={page}, limit={limit}, count={len(result['list'])}")
        
        return jsonify({
            'code': 200,
            'message': '搜索新闻成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"搜索新闻出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        })

@news_bp.route('/summary', methods=['GET'])
def get_daily_summary():
    """
    获取每日新闻摘要
    
    Returns:
        JSON: 新闻摘要
    """
    try:
        summary = news_service.get_daily_summary()
        
        logger.info("获取新闻摘要成功")
        
        return jsonify({
            'code': 200,
            'message': '获取新闻摘要成功',
            'data': {
                'summary': summary,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        logger.error(f"获取新闻摘要出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        })

@news_bp.route('/update', methods=['POST'])
def update_news():
    """
    手动触发新闻更新
    
    Returns:
        JSON: 更新结果
    """
    try:
        # 检查管理员权限
        admin_token = request.headers.get('X-Admin-Token')
        if not admin_token or admin_token != current_app.config.get('ADMIN_TOKEN'):
            return jsonify({
                'code': 403,
                'message': '权限不足，需要管理员权限',
                'data': None
            })
        
        result = news_service.update_news()
        
        if result:
            logger.info("手动更新新闻数据成功")
            return jsonify({
                'code': 200,
                'message': '新闻更新任务已启动',
                'data': None
            })
        else:
            logger.error("手动更新新闻数据失败")
            return jsonify({
                'code': 500,
                'message': '新闻更新任务启动失败',
                'data': None
            })
    except Exception as e:
        logger.error(f"手动更新新闻数据出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        })
