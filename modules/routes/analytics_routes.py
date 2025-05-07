"""
分析相关路由模块
处理所有与数据分析、报告生成相关的路由
"""

from flask import Blueprint, jsonify, request, send_file
from . import routes_bp
from modules.analytics_module import AnalyticsModule
from modules.database_module import DatabaseModule
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# 获取模块实例
analytics_module = AnalyticsModule()
db_module = DatabaseModule()

@routes_bp.route('/api/analytics/session_data')
def get_session_data():
    """获取当前会话数据"""
    try:
        session_data = analytics_module.get_current_session_data()
        return jsonify(session_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/analytics/historical_data')
def get_historical_data():
    """获取历史数据"""
    try:
        days = request.args.get('days', default=7, type=int)
        data = analytics_module.get_historical_data(days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/analytics/generate_report')
def generate_report():
    """生成分析报告"""
    try:
        report_type = request.args.get('type', default='daily', type=str)
        date_str = request.args.get('date', default=None, type=str)
        
        if date_str is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
        report_data = analytics_module.generate_report(report_type, date)
        return jsonify(report_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/analytics/download_report')
def download_report():
    """下载分析报告"""
    try:
        report_type = request.args.get('type', default='daily', type=str)
        date_str = request.args.get('date', default=None, type=str)
        format_type = request.args.get('format', default='pdf', type=str)
        
        if date_str is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
        report_path = analytics_module.create_downloadable_report(report_type, date, format_type)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"{report_type}_report_{date.strftime('%Y-%m-%d')}.{format_type}"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/analytics/posture_stats')
def get_posture_stats():
    """获取姿势统计数据"""
    try:
        time_period = request.args.get('period', default='day', type=str)
        stats = analytics_module.get_posture_statistics(time_period)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/analytics/trend_analysis')
def get_trend_analysis():
    """获取趋势分析数据"""
    try:
        days = request.args.get('days', default=30, type=int)
        analysis = analytics_module.analyze_trends(days)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500