"""
视频流接口路由模块
处理移动端首页视频流传输功能
使用共享摄像头资源，与情绪检测等模块协调工作
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse, FileResponse
import sys
import os
import logging
from typing import Generator, Optional
import time
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["video"]
)

class VideoStreamManager:
    """视频流管理器 - 展示版改为静态图流"""

    def __init__(self):
        self.is_streaming = False
        self.frame_rate = 30  # 帧率
        self.quality = 80     # JPEG质量

        # 展示版：静态图片路径与缓存
        self._root_dir = Path(__file__).resolve().parents[3]
        self._static_image_path = self._root_dir / 'static' / 'home.jpg'
        self._static_image_bytes: Optional[bytes] = None
        self._load_static_image()

        # 快照缓存目录（项目根/static/camera_cache）
        try:
            self._cache_dir = self._root_dir / 'static' / 'camera_cache'
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.getLogger(__name__).warning(f"创建快照缓存目录失败: {e}")
            self._cache_dir = None
        self._last_cache_write = 0.0

    def _load_static_image(self) -> None:
        """加载静态展示图片到内存，不存在则置空以便后续生成占位图"""
        try:
            if self._static_image_path.exists():
                self._static_image_bytes = self._static_image_path.read_bytes()
                logger.info(f"展示版视频流将使用静态图片: {self._static_image_path}")
            else:
                logger.warning(f"未找到静态图片: {self._static_image_path}，将使用占位图")
                self._static_image_bytes = None
        except Exception as e:
            logger.error(f"加载静态图片失败: {e}")
            self._static_image_bytes = None
        
    def get_camera_status(self) -> dict:
        """返回展示版状态：静态图模式始终可用"""
        try:
            return {
                "available": True,
                "running": True,
                "frame_rate": self.frame_rate,
                "quality": self.quality,
                "mode": "静态图模式"
            }
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                "available": False,
                "running": False,
                "frame_rate": self.frame_rate,
                "quality": self.quality,
                "mode": "未知"
            }
    
    def generate_frames(self) -> Generator[bytes, None, None]:
        """生成展示版视频帧：循环输出 static/home.jpg（若缺失则输出占位图）"""
        self.is_streaming = True
        frame_interval = 1.0 / self.frame_rate

        try:
            while self.is_streaming:
                start_time = time.time()

                frame_data: Optional[bytes] = self._static_image_bytes
                if not frame_data:
                    # 无静态图时，生成占位图
                    frame_data = self._generate_test_frame()

                if frame_data:
                    # 生成multipart数据
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                    # 写入快照缓存（每2秒一次，原子替换）
                    try:
                        if self._cache_dir is not None and (time.time() - self._last_cache_write) >= 2.0:
                            tmp_path = self._cache_dir / 'latest.tmp'
                            final_path = self._cache_dir / 'latest.jpg'
                            with open(tmp_path, 'wb') as f:
                                f.write(frame_data)
                            os.replace(tmp_path, final_path)
                            self._last_cache_write = time.time()
                    except Exception as e:
                        logger.debug(f"写入快照缓存失败: {e}")

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
    实时传输视频流（展示版：static/home.jpg）
    
    功能位置: Home.vue/Monitor.vue 视频区域
    优先级: 高 🔥
    
    Returns:
        StreamingResponse: MJPEG视频流
    """
    try:
        logger.info("开始视频流传输（展示版：静态图）")
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


@router.get("/video/fallback")
async def video_fallback():
    """
    视频流回退图片：直接返回 static/home.jpg；若缺失则返回最近缓存或占位图。
    前端在 <img> 加载 /api/video 失败时应切换到该URL。
    """
    try:
        # 优先返回展示静态图
        static_img = Path(__file__).resolve().parents[3] / 'static' / 'home.jpg'
        if static_img.exists():
            return FileResponse(str(static_img), media_type='image/jpeg', headers={"Cache-Control": "no-store"})

        # 其次，返回最近缓存的快照
        cache_dir = video_manager._cache_dir or (Path(__file__).resolve().parents[3] / 'static' / 'camera_cache')
        latest = cache_dir / 'latest.jpg'
        if latest.exists():
            return FileResponse(str(latest), media_type='image/jpeg', headers={"Cache-Control": "no-store"})

        # 最后兜底：动态生成一张简单提示图
        import cv2
        import numpy as np
        h, w = 360, 480
        img = np.full((h, w, 3), (230, 240, 245), dtype=np.uint8)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cv2.putText(img, "Fallback Snapshot", (40, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (70, 90, 120), 2)
        cv2.putText(img, ts, (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 120, 150), 2)
        ok, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ok:
            return Response(content=buf.tobytes(), media_type='image/jpeg', headers={"Cache-Control": "no-store"})
    except Exception as e:
        logger.error(f"回退图片生成失败: {e}")
    # 彻底失败时返回空响应
    raise HTTPException(status_code=500, detail="无法提供回退图片")


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
