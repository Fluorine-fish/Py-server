"""
路由模块包
此包包含所有Flask路由相关的功能模块，分解自原routes.py
"""

from flask import Blueprint

# 创建统一的蓝图
routes_bp = Blueprint('routes', __name__)

# 导入所有子模块的路由
from . import base_routes
from . import serial_routes
from . import posture_routes
from . import system_routes
from . import dashboard_routes

# 路由就绪标志
routes_ready = True

# 服务实例，供路由模块使用
posture_monitor_service = None
video_stream_service = None
serial_handler_service = None

# 添加setup_services函数以便app.py可以导入
def setup_services(posture_monitor_instance=None, video_stream_instance=None, serial_handler_instance=None):
    """设置服务和共享资源"""
    global posture_monitor_service, video_stream_service, serial_handler_service
    
    # 保存服务实例供路由模块使用
    posture_monitor_service = posture_monitor_instance
    video_stream_service = video_stream_instance
    serial_handler_service = serial_handler_instance
    
    print("服务资源初始化完成")
    return True