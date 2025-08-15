"""
视频流接口路由模块
处理移动端首页视频流传输功能
使用共享摄像头资源，与情绪检测等模块协调工作
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import sys
import os
import logging
from typing import Generator
import time

# 添加上级目录到路径以导入共享摄像头
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from video_stream import camera

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["video"]
)

class VideoStreamManager:
    """视频流管理器 - 使用共享摄像头"""
    
    def __init__(self):
        self.shared_camera = camera  # 使用共享摄像头实例
        self.is_streaming = False
        self.frame_rate = 30  # 帧率
        self.quality = 80     # JPEG质量
        
    def get_camera_status(self) -> dict:
        """获取共享摄像头状态"""
        try:
            # 检查摄像头是否可用，如果物理摄像头不可用但运行模式正常，我们也认为它是可用的（因为有模拟摄像头）
            is_available = False
            
            # 如果有物理摄像头并且已打开
            if self.shared_camera.cap and self.shared_camera.cap.isOpened():
                is_available = True
            # 如果没有物理摄像头但仍在运行（使用模拟摄像头）
            elif self.shared_camera.running:
                is_available = True
                
            return {
                "available": is_available,
                "running": self.shared_camera.running,
                "frame_rate": self.frame_rate,
                "quality": self.quality,
                "mode": "模拟摄像头" if not (self.shared_camera.cap and self.shared_camera.cap.isOpened()) and self.shared_camera.running else "物理摄像头"
            }
        except Exception as e:
            logger.error(f"获取摄像头状态失败: {e}")
            return {
                "available": False,
                "running": False,
                "frame_rate": self.frame_rate,
                "quality": self.quality,
                "mode": "未知"
            }
    
    def generate_frames(self) -> Generator[bytes, None, None]:
        """从共享摄像头生成视频帧数据"""
        self.is_streaming = True
        frame_interval = 1.0 / self.frame_rate
        
        try:
            while self.is_streaming:
                start_time = time.time()
                
                # 从共享摄像头获取帧数据
                frame_data = self.shared_camera.read()
                
                if frame_data is None:
                    # 如果没有帧数据，生成测试帧
                    frame_data = self._generate_test_frame()
                
                if frame_data:
                    # 生成multipart数据
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                
                # 控制帧率
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except Exception as e:
            logger.error(f"视频流生成错误: {e}")
        finally:
            self.is_streaming = False
    
    def _generate_test_frame(self) -> bytes:
        """生成单个测试帧（当摄像头不可用时）"""
        import cv2
        import numpy as np
        
        try:
            # 创建测试图像
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (50, 100, 150)  # 蓝灰色背景
            
            # 添加文本信息
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cv2.putText(frame, "CAMERA NOT AVAILABLE", (150, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, timestamp, (180, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, "Waiting for camera...", (170, 300), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', frame, 
                                     [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            
            if ret:
                return buffer.tobytes()
                
        except Exception as e:
            logger.error(f"测试帧生成错误: {e}")
            
        return b''

# 全局视频流管理器实例
video_manager = VideoStreamManager()

@router.get("/video")
async def video_stream():
    """
    实时传输摄像头视频流
    
    功能位置: Home.vue 视频区域
    优先级: 高 🔥
    使用共享摄像头资源，与其他模块协调工作
    
    Returns:
        StreamingResponse: MJPEG视频流
    """
    try:
        logger.info("开始视频流传输（使用共享摄像头）")
        return StreamingResponse(
            video_manager.generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        logger.error(f"视频流启动失败: {e}")
        raise HTTPException(status_code=500, detail=f"视频流服务错误: {str(e)}")


@router.get("/video/status")
async def video_status():
    """
    获取视频流状态
    
    Returns:
        dict: 视频流状态信息
    """
    status = video_manager.get_camera_status()
    status["streaming"] = video_manager.is_streaming
    return status

@router.post("/video/config")
async def update_video_config(frame_rate: int = 30, quality: int = 80):
    """
    更新视频流配置
    
    Args:
        frame_rate: 帧率 (1-60)
        quality: JPEG质量 (1-100)
    
    Returns:
        dict: 配置更新结果
    """
    try:
        # 验证参数
        if not (1 <= frame_rate <= 60):
            raise HTTPException(status_code=400, detail="帧率必须在1-60之间")
        if not (1 <= quality <= 100):
            raise HTTPException(status_code=400, detail="质量必须在1-100之间")
        
        video_manager.frame_rate = frame_rate
        video_manager.quality = quality
        
        logger.info(f"视频配置已更新: 帧率={frame_rate}, 质量={quality}")
        
        return {
            "success": True,
            "message": "视频配置已更新",
            "config": {
                "frame_rate": frame_rate,
                "quality": quality
            }
        }
        
    except Exception as e:
        logger.error(f"配置更新失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置更新错误: {str(e)}")
