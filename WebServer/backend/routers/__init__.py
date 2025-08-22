"""
路由模块初始化文件
导入所有路由模块
"""

from .video_stream import router as video_router
from .realtime_data import router as realtime_router
from .lamp_control import router as lamp_router

__all__ = ["video_router", "realtime_router", "lamp_router"]
