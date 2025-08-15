import cv2
import threading
import time
import numpy as np
import logging
import os
import sys
from typing import Optional

# 添加上级目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入摄像头管理器
from modules.camera_manager import get_camera_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Camera:
    """
    摄像头封装类 - 使用中心化摄像头管理器
    """
    def __init__(self, src=0):
        # 获取全局摄像头管理器实例
        self.camera_manager = get_camera_manager(
            init=True,  # 自动初始化并启动
            camera_id=src,
            frame_width=640,
            frame_height=480,
            fps_target=30
        )
        
        # 注册为摄像头帧的消费者
        self.frame_queue = self.camera_manager.register_consumer("webserver_camera", max_queue_size=5)
        
        # 最新一帧（已编码为JPEG）
        self.frame = None
        self.lock = threading.Lock()
        
        # 启动帧处理线程
        self.running = True
        threading.Thread(target=self._process_frames, daemon=True, name="WebServerCamera").start()
        logger.info("WebServer摄像头帧处理线程已启动")
    
    def _process_frames(self):
        """处理从摄像头管理器接收到的帧"""
        while self.running:
            try:
                # 尝试从队列获取最新帧（超时等待100毫秒）
                try:
                    frame = self.frame_queue.get(timeout=0.1)
                except:
                    # 队列为空，尝试直接从管理器获取最新帧
                    frame = self.camera_manager.get_latest_frame()
                
                if frame is not None:
                    # 编码为JPEG
                    _, jpg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    with self.lock:
                        self.frame = jpg.tobytes()
                else:
                    # 如果仍然没有帧，生成一个模拟帧
                    self._generate_dummy_frame()
            
            except Exception as e:
                logger.error(f"处理视频帧出错: {str(e)}")
                # 如果发生错误，生成一个模拟帧
                self._generate_dummy_frame()
                time.sleep(0.1)
    
    def read(self):
        """读取当前帧"""
        with self.lock:
            return self.frame
    
    @property
    def cap(self):
        """获取原始摄像头对象（兼容性方法）"""
        if hasattr(self.camera_manager, 'cap'):
            return self.camera_manager.cap
        return None
    
    def start(self):
        """启动摄像头（兼容性方法）"""
        # 摄像头管理器在初始化时已启动
        pass
    
    def stop(self):
        """停止摄像头帧处理（不会停止全局摄像头管理器）"""
        self.running = False
        # 注销消费者
        self.camera_manager.unregister_consumer("webserver_camera")
        logger.info("WebServer摄像头帧处理已停止")
        
    def _generate_dummy_frame(self):
        """生成模拟帧，当无法获取真实帧时使用"""
        try:
            # 创建空白帧
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            dummy_frame[:] = (70, 120, 190)  # 蓝色背景
            
            # 添加文本信息
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cv2.putText(dummy_frame, "模拟摄像头模式", (180, 200), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(dummy_frame, timestamp, (200, 250), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(dummy_frame, "实时模拟视频流", (200, 300), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # 编码为JPEG
            _, jpg = cv2.imencode('.jpg', dummy_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            with self.lock:
                self.frame = jpg.tobytes()
        except Exception as e:
            logger.error(f"生成模拟帧出错: {str(e)}")

# 单例摄像头
camera = Camera(src=0)