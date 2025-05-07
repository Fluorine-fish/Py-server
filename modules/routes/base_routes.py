"""
基础路由模块
处理主页和其他基本页面路由
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from . import routes_bp
import os
import time
import json
from datetime import datetime

# 全局变量，存储当前版本和更新时间
VERSION = "2.5.0"
LAST_UPDATE = "2025-05-07"

@routes_bp.route('/')
def index():
    """主页路由"""
    return render_template('index.html')

# 删除重复的dashboard路由，这个已经在dashboard_routes.py中定义

# 删除重复的parent_dashboard路由，这个已经在dashboard_routes.py中定义

@routes_bp.route('/health')
def health_check():
    """健康检查路由"""
    return jsonify({
        'status': 'ok',
        'message': '服务正常运行'
    })

@routes_bp.route('/info')
def api_info():
    """API信息路由"""
    return jsonify({
        'name': '姿势监测系统',
        'version': '1.0.0',
        'endpoints': [
            '/api/start_monitor',
            '/api/stop_monitor',
            '/api/status',
            '/api/video_feed',
            '/api/get_fps_info',
            '/api/analytics/session_data',
            # 其他端点...
        ]
    })

# 获取系统基本信息
@routes_bp.route('/api/system_info')
def system_info():
    """获取系统基本信息，包括版本号和更新时间"""
    info = {
        'version': VERSION,
        'last_update': LAST_UPDATE,
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'running'
    }
    return jsonify(info)

# 加载配置
@routes_bp.route('/api/load_config')
def load_config():
    """加载系统配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        
        if not os.path.exists(config_path):
            # 如果配置文件不存在，返回默认配置
            default_config = {
                "camera_id": 0,
                "fps_limit": 30,
                "detection_interval": 1,
                "serial_port": "",
                "baud_rate": 9600,
                "threshold_angle": 30
            }
            return jsonify(default_config)
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 保存配置
@routes_bp.route('/api/save_config', methods=['POST'])
def save_config():
    """保存系统配置"""
    try:
        config = request.json
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500