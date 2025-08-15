"""
视频状态API模块
提供摄像头状态的API接口，支持前端UI检测视频流可用性
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from modules.camera_manager import get_camera_manager

def register_video_status_routes(app):
    """
    注册视频状态路由
    """
    camera_manager = get_camera_manager()
    
    @app.get('/api/video/status')
    async def video_status():
        """
        获取视频流状态API
        
        返回:
            JSON: 包含摄像头状态信息
        """
        try:
            # 检查摄像头是否可用
            is_available = False
            mode = "未知"
            
            # 如果有物理摄像头并且已打开
            if camera_manager.cap and camera_manager.cap.isOpened():
                is_available = True
                mode = "物理摄像头"
            # 如果没有物理摄像头但仍在运行（使用模拟摄像头）
            elif camera_manager.running:
                is_available = True
                mode = "模拟摄像头"
                
            return {
                "available": is_available,
                "running": camera_manager.running,
                "frame_rate": 30,
                "quality": 85,
                "mode": mode,
                "streaming": True
            }
            
        except Exception as e:
            return {
                "available": False,
                "running": False,
                "frame_rate": 30,
                "quality": 85,
                "mode": "错误",
                "streaming": False,
                "error": str(e)
            }
