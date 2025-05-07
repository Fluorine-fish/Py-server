"""
仪表板相关路由模块
处理所有与用户仪表板显示相关的路由
"""

from flask import Blueprint, render_template, jsonify, request
from . import routes_bp
from modules.posture_module import PostureModule
from modules.database_module import DatabaseModule
import json

# 获取模块实例
posture_module = PostureModule()
db_module = DatabaseModule()

@routes_bp.route('/dashboard')
def dashboard():
    """主仪表板页面"""
    return render_template('new_dashboard.html')

@routes_bp.route('/parent_dashboard')
def parent_dashboard():
    """家长仪表板页面"""
    return render_template('parent_dashboard.html')

@routes_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """获取仪表板统计数据"""
    try:
        days = request.args.get('days', default=7, type=int)
        stats = db_module.get_dashboard_stats(days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/dashboard/daily_summary')
def daily_summary():
    """获取每日摘要数据"""
    try:
        date = request.args.get('date', default=None, type=str)
        summary = db_module.get_daily_summary(date)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/dashboard/posture_data')
def dashboard_posture_data():
    """获取仪表板的姿势数据"""
    try:
        timeframe = request.args.get('timeframe', default='day', type=str)
        data = posture_module.get_posture_data_for_dashboard(timeframe)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/dashboard/recent_events')
def recent_events():
    """获取最近姿势事件"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        events = db_module.get_recent_posture_events(limit)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/api/dashboard/usage_time')
def usage_time():
    """获取系统使用时间统计"""
    try:
        period = request.args.get('period', default='week', type=str)
        time_data = db_module.get_usage_time_stats(period)
        return jsonify(time_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500