"""
数据分析API路由
提供教学数据分析和可视化的接口
"""
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from bson.objectid import ObjectId
import json
from src.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)

# 初始化数据分析服务
def get_analytics_service():
    return AnalyticsService(current_app.mongo)

@analytics_bp.route('/interaction-report', methods=['GET'])
def get_interaction_report():
    """获取互动数据报告"""
    try:
        # 获取请求参数
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify({"error": "缺少必要参数：teacher_id"}), 400
            
        # 解析日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # 获取报告数据
        analytics_service = get_analytics_service()
        report_data = analytics_service.generate_interaction_report(
            ObjectId(teacher_id), start_date, end_date
        )
        
        return jsonify({
            "success": True,
            "report": report_data
        })
    except Exception as e:
        current_app.logger.error(f"获取互动报告错误: {str(e)}")
        return jsonify({"error": f"获取互动报告失败: {str(e)}"}), 500

@analytics_bp.route('/feedback-report', methods=['GET'])
def get_feedback_report():
    """获取反馈数据报告"""
    try:
        # 获取请求参数
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify({"error": "缺少必要参数：teacher_id"}), 400
            
        # 解析日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # 获取报告数据
        analytics_service = get_analytics_service()
        report_data = analytics_service.generate_feedback_report(
            ObjectId(teacher_id), start_date, end_date
        )
        
        return jsonify({
            "success": True,
            "report": report_data
        })
    except Exception as e:
        current_app.logger.error(f"获取反馈报告错误: {str(e)}")
        return jsonify({"error": f"获取反馈报告失败: {str(e)}"}), 500

@analytics_bp.route('/student-engagement', methods=['GET'])
def get_student_engagement():
    """获取学生参与度数据"""
    try:
        # 获取请求参数
        class_id = request.args.get('class_id')
        if not class_id:
            return jsonify({"error": "缺少必要参数：class_id"}), 400
            
        # 解析日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # 获取学生参与度数据
        analytics_service = get_analytics_service()
        engagement_data = analytics_service.get_student_engagement_data(
            ObjectId(class_id), start_date, end_date
        )
        
        return jsonify({
            "success": True,
            "engagement_data": engagement_data
        })
    except Exception as e:
        current_app.logger.error(f"获取学生参与度数据错误: {str(e)}")
        return jsonify({"error": f"获取学生参与度数据失败: {str(e)}"}), 500

@analytics_bp.route('/dashboard-summary', methods=['GET'])
def get_dashboard_summary():
    """获取教师仪表盘汇总数据"""
    try:
        # 获取请求参数
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify({"error": "缺少必要参数：teacher_id"}), 400
            
        analytics_service = get_analytics_service()
        
        # 获取最近30天的互动报告
        interaction_report = analytics_service.generate_interaction_report(ObjectId(teacher_id))
        
        # 获取最近30天的反馈报告
        feedback_report = analytics_service.generate_feedback_report(ObjectId(teacher_id))
        
        # 提取汇总数据
        summary_data = {
            "interaction_summary": interaction_report["summary"],
            "feedback_summary": feedback_report["summary"],
            "recent_feedback_sentiment": {
                "positive_percentage": feedback_report["summary"]["positive_feedback_percentage"],
                "negative_percentage": feedback_report["summary"]["negative_feedback_percentage"]
            },
            "charts": {
                "interaction_distribution": interaction_report["charts"].get("interaction_type_distribution"),
                "sentiment_distribution": feedback_report["charts"].get("sentiment_distribution")
            }
        }
        
        return jsonify({
            "success": True,
            "summary": summary_data
        })
    except Exception as e:
        current_app.logger.error(f"获取仪表盘汇总数据错误: {str(e)}")
        return jsonify({"error": f"获取仪表盘汇总数据失败: {str(e)}"}), 500 