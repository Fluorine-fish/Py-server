"""
摄像头管理器模块 - 提供中心化摄像头管理和视频帧共享
"""
import cv2
import threading
import time
import numpy as np
import queue
from typing import Dict, List, Optional, Callable
import logging
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CameraManager:
    """
    中心化摄像头管理器
    负责摄像头的初始化、帧获取和分发给不同模块
    """
    def __init__(self, 
                camera_id: int = 0, 
                frame_width: int = 640, 
                frame_height: int = 480,
                fps_target: int = 30):
        """
        初始化摄像头管理器
        
        Args:
            camera_id: 摄像头ID或路径
            frame_width: 视频帧宽度
            frame_height: 视频帧高度
            fps_target: 目标帧率
        """
        self.camera_id = camera_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps_target = fps_target
        self.frame_interval = 1.0 / fps_target
        
        # 摄像头实例
        self.cap = None
        self.running = False
        self.last_frame = None
        self.frame_count = 0
        self.last_frame_time = 0
        self.fps = 0
        
        # 线程锁和队列
        self.lock = threading.Lock()
        
        # 消费者注册表 {consumer_id: queue}
        self.consumers: Dict[str, queue.Queue] = {}
        
        # 消费者回调函数 {consumer_id: callback_function}
        self.callbacks: Dict[str, Callable] = {}
        
        # 错误恢复相关
        self.reconnect_count = 0
        self.max_reconnects = 20  # 增加最大重连次数
        self.reconnect_interval = 3  # 减少重连等待时间
        self.last_reconnect_time = 0
        self.camera_open_retry_count = 0
        self.max_open_retries = 5
        
        # 可用视频源列表
        self.video_sources = [0, 1, 2, 3, "/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
        
        # 添加模拟摄像头选项（当真实摄像头不可用时）
        self.use_dummy_camera = False
        self.dummy_frame_index = 0
        self.dummy_frames = []
        
        # 初始化摄像头
        self._init_camera()
        
    def _init_camera(self):
        """初始化摄像头，如果失败则尝试其他视频源"""
        # 重置模拟摄像头标志
        self.use_dummy_camera = False
        
        # 释放之前的摄像头实例
        if self.cap is not None:
            self.cap.release()
            time.sleep(0.5)  # 等待资源释放
        
        # 尝试打开指定的摄像头
        try:
            logger.info(f"尝试打开摄像头: {self.camera_id}")
            self.cap = cv2.VideoCapture(self.camera_id)
            
            # 设置摄像头参数
            if self.cap.isOpened():
                # 设置分辨率
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                
                # 设置帧率
                self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
                
                # 设置缓冲区大小
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # 尝试设置编码格式为MJPG（如果支持）
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                
                # 读取一帧测试摄像头是否正常工作
                ret, test_frame = self.cap.read()
                if not ret or test_frame is None or test_frame.size == 0:
                    logger.warning(f"摄像头 {self.camera_id} 虽然打开但无法读取帧")
                    self.cap.release()
                else:
                    logger.info(f"摄像头 {self.camera_id} 初始化成功，分辨率: {self.frame_width}x{self.frame_height}")
                    self.camera_open_retry_count = 0
                    return True
                
        except Exception as e:
            logger.error(f"打开摄像头 {self.camera_id} 时出错: {str(e)}")
            if self.cap is not None:
                self.cap.release()
        
        # 如果指定摄像头打开失败，尝试其他视频源
        logger.warning(f"摄像头 {self.camera_id} 打开失败，尝试其他视频源...")
        
        # 循环尝试不同的摄像头设备
        for src in self.video_sources:
            if src == self.camera_id:
                continue
                
            try:
                logger.info(f"尝试打开视频源: {src}")
                self.cap = cv2.VideoCapture(src)
                
                if self.cap.isOpened():
                    # 设置分辨率
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    
                    # 设置帧率
                    self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
                    
                    # 设置缓冲区大小
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # 读取一帧测试摄像头是否正常工作
                    ret, test_frame = self.cap.read()
                    if not ret or test_frame is None or test_frame.size == 0:
                        logger.warning(f"视频源 {src} 虽然打开但无法读取帧")
                        self.cap.release()
                        continue
                    
                    logger.info(f"成功打开视频源: {src}")
                    self.camera_id = src
                    self.camera_open_retry_count = 0
                    return True
            except Exception as e:
                logger.error(f"打开视频源 {src} 时出错: {str(e)}")
                if self.cap is not None:
                    self.cap.release()
                    
        # 增加重试计数
        self.camera_open_retry_count += 1
        
        # 如果重试次数过多，切换到模拟摄像头模式
        if self.camera_open_retry_count >= self.max_open_retries:
            logger.warning(f"连续 {self.camera_open_retry_count} 次尝试打开摄像头都失败，切换到模拟摄像头模式")
            self.cap = None
            return self._init_dummy_camera()
            
        # 所有视频源都失败
        logger.error("所有摄像头源都打开失败")
        self.cap = None
        return False
    
    def _generate_error_frame(self, message="摄像头未连接"):
        """生成错误帧"""
        frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        frame[:] = (50, 50, 200)  # 红色背景
        
        # 添加错误文本
        cv2.putText(frame, message, (self.frame_width // 4, self.frame_height // 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cv2.putText(frame, timestamp, (self.frame_width // 4, self.frame_height // 2 + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        return frame
        
    def _init_dummy_camera(self):
        """初始化模拟摄像头，创建一系列测试图像"""
        logger.info("初始化模拟摄像头...")
        self.dummy_frames = []
        
        # 生成10个不同的模拟帧
        for i in range(10):
            # 创建基础帧
            frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
            # 生成渐变背景
            for y in range(self.frame_height):
                for x in range(self.frame_width):
                    b = int(255 * x / self.frame_width)
                    g = int(255 * y / self.frame_height)
                    r = int(255 * (1 - (x + y) / (self.frame_width + self.frame_height)))
                    frame[y, x] = [b, g, r]
            
            # 添加一些动态内容
            radius = 50 + 20 * (i % 5)
            center = (self.frame_width // 2 + 100 * np.cos(i * 36 * np.pi/180), 
                      self.frame_height // 2 + 100 * np.sin(i * 36 * np.pi/180))
            cv2.circle(frame, (int(center[0]), int(center[1])), radius, (255, 255, 255), -1)
            
            # 添加文本
            cv2.putText(frame, f"模拟摄像头 #{i+1}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cv2.putText(frame, timestamp, (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            self.dummy_frames.append(frame)
            
        self.use_dummy_camera = True
        logger.info(f"模拟摄像头初始化完成，生成了 {len(self.dummy_frames)} 个测试帧")
        return True
        
    def _get_dummy_frame(self):
        """获取下一个模拟摄像头帧"""
        if not self.dummy_frames:
            self._init_dummy_camera()
            
        frame = self.dummy_frames[self.dummy_frame_index].copy()
        self.dummy_frame_index = (self.dummy_frame_index + 1) % len(self.dummy_frames)
        
        # 添加当前时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cv2.putText(frame, timestamp, (self.frame_width - 200, self.frame_height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                   
        return frame
    
    def start(self):
        """启动摄像头帧捕获线程"""
        if self.running:
            return True
            
        if self.cap is None and not self._init_camera():
            logger.error("摄像头初始化失败，无法启动捕获线程")
            return False
            
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True, name="CameraCapture").start()
        logger.info("摄像头捕获线程已启动")
        return True
    
    def _capture_loop(self):
        """主捕获循环"""
        consecutive_errors = 0
        last_status_log_time = 0
        frame_times = []  # 记录最近帧处理时间，用于平滑帧率计算
        
        while self.running:
            try:
                current_time = time.time()
                
                # 定期输出状态信息
                if (current_time - last_status_log_time) > 60:  # 每分钟输出一次状态
                    status = self.get_status()
                    logger.info(f"摄像头状态: {status}")
                    last_status_log_time = current_time
                
                # 处理模拟摄像头模式
                if self.use_dummy_camera:
                    frame = self._get_dummy_frame()
                    with self.lock:
                        self.last_frame = frame.copy()
                    
                    # 分发帧给所有消费者
                    self._distribute_frame(frame)
                    
                    # 计算帧率
                    time_diff = current_time - self.last_frame_time
                    if time_diff >= 1.0:  # 每秒更新一次帧率
                        self.fps = self.frame_count / time_diff
                        self.frame_count = 0
                        self.last_frame_time = current_time
                    
                    self.frame_count += 1
                    
                    # 控制帧率
                    elapsed = time.time() - current_time
                    sleep_time = max(0, self.frame_interval - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    continue
                
                # 检查摄像头连接状态
                if self.cap is None or not self.cap.isOpened():
                    # 尝试重连
                    if (current_time - self.last_reconnect_time) > self.reconnect_interval:
                        logger.info("尝试重新连接摄像头...")
                        if self._init_camera():
                            logger.info("摄像头重连成功")
                            consecutive_errors = 0
                        else:
                            logger.warning("摄像头重连失败")
                        
                        self.last_reconnect_time = current_time
                        self.reconnect_count += 1
                        
                    # 生成错误帧或使用模拟摄像头
                    if self.use_dummy_camera:
                        frame = self._get_dummy_frame()
                    else:
                        frame = self._generate_error_frame("正在尝试重新连接摄像头...")
                        
                    with self.lock:
                        self.last_frame = frame.copy()
                        
                    # 分发错误帧给所有消费者
                    self._distribute_frame(frame)
                    time.sleep(0.5)
                    continue
                
                # 读取一帧
                start_read_time = time.time()
                ret, frame = self.cap.read()
                read_time = time.time() - start_read_time
                
                # 如果读取时间过长，记录警告
                if read_time > 0.5:
                    logger.warning(f"摄像头帧读取时间过长: {read_time:.3f}秒")
                
                # 计算帧率
                frame_times.append(current_time)
                # 只保留最近100帧的时间
                if len(frame_times) > 100:
                    frame_times.pop(0)
                
                # 至少有2个帧时间时才计算帧率
                if len(frame_times) > 1:
                    time_span = frame_times[-1] - frame_times[0]
                    if time_span > 0:
                        self.fps = (len(frame_times) - 1) / time_span
                
                # 处理读取失败的情况
                if not ret or frame is None or frame.size == 0:
                    consecutive_errors += 1
                    logger.warning(f"读取视频帧失败，连续错误: {consecutive_errors}")
                    
                    # 连续错误过多，尝试重新初始化摄像头
                    if consecutive_errors > 10:
                        logger.error("连续读取错误过多，尝试重新初始化摄像头")
                        if not self._init_camera():
                            logger.warning("摄像头重新初始化失败，尝试使用模拟摄像头")
                            self._init_dummy_camera()
                        consecutive_errors = 0
                    
                    # 生成错误帧或使用模拟摄像头
                    if self.use_dummy_camera:
                        frame = self._get_dummy_frame()
                    else:
                        frame = self._generate_error_frame("视频信号丢失")
                    
                    with self.lock:
                        self.last_frame = frame.copy()
                    
                    # 分发帧给所有消费者
                    self._distribute_frame(frame)
                    time.sleep(0.1)  # 减少等待时间，加快恢复
                    continue
                
                # 成功读取一帧
                consecutive_errors = 0
                self.frame_count += 1
                
                # 保存当前帧
                with self.lock:
                    self.last_frame = frame.copy()
                
                # 分发帧给所有消费者
                self._distribute_frame(frame)
                
                # 控制帧率
                elapsed = time.time() - current_time
                sleep_time = max(0, self.frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"视频捕获错误: {str(e)}")
                consecutive_errors += 1
                
                # 如果连续错误过多，尝试使用模拟摄像头
                if consecutive_errors > 15 and not self.use_dummy_camera:
                    logger.warning("连续错误过多，切换到模拟摄像头模式")
                    self._init_dummy_camera()
                    consecutive_errors = 0
                
                time.sleep(0.5)
    
    def _distribute_frame(self, frame):
        """分发帧给所有消费者"""
        # 处理基于队列的消费者
        for consumer_id, q in list(self.consumers.items()):
            try:
                # 如果队列满，移除最旧的帧
                if q.full():
                    try:
                        q.get_nowait()
                    except:
                        pass
                
                # 添加新帧
                q.put_nowait(frame.copy())
            except Exception as e:
                logger.error(f"向消费者 {consumer_id} 分发帧时出错: {str(e)}")
        
        # 处理回调函数
        for consumer_id, callback in list(self.callbacks.items()):
            try:
                callback(frame.copy())
            except Exception as e:
                logger.error(f"调用消费者 {consumer_id} 的回调函数时出错: {str(e)}")
    
    def register_consumer(self, consumer_id: str, max_queue_size: int = 5) -> queue.Queue:
        """
        注册一个帧消费者
        
        Args:
            consumer_id: 消费者ID
            max_queue_size: 队列最大大小
            
        Returns:
            指向该消费者的队列
        """
        if consumer_id in self.consumers:
            logger.warning(f"消费者 {consumer_id} 已存在，返回现有队列")
            return self.consumers[consumer_id]
        
        # 创建新队列
        q = queue.Queue(maxsize=max_queue_size)
        self.consumers[consumer_id] = q
        logger.info(f"消费者 {consumer_id} 注册成功")
        return q
    
    def register_callback(self, consumer_id: str, callback: Callable):
        """
        注册回调函数
        
        Args:
            consumer_id: 消费者ID
            callback: 回调函数，接收一帧图像作为参数
        """
        self.callbacks[consumer_id] = callback
        logger.info(f"消费者 {consumer_id} 回调函数注册成功")
    
    def unregister_consumer(self, consumer_id: str):
        """注销一个帧消费者"""
        if consumer_id in self.consumers:
            del self.consumers[consumer_id]
            logger.info(f"消费者 {consumer_id} 注销成功")
        
        if consumer_id in self.callbacks:
            del self.callbacks[consumer_id]
            logger.info(f"消费者 {consumer_id} 回调函数注销成功")
    
    def get_latest_frame(self):
        """获取最新帧"""
        with self.lock:
            if self.last_frame is None:
                return self._generate_error_frame()
            return self.last_frame.copy()
    
    def get_status(self):
        """获取摄像头状态"""
        status = {
            "running": self.running,
            "connected": (self.cap is not None and self.cap.isOpened()) or self.use_dummy_camera,
            "is_dummy": self.use_dummy_camera,
            "camera_id": self.camera_id,
            "fps": round(self.fps, 2),
            "resolution": f"{self.frame_width}x{self.frame_height}",
            "target_fps": self.fps_target,
            "consumers": list(self.consumers.keys()) + list(self.callbacks.keys()),
            "consumer_count": len(self.consumers) + len(self.callbacks),
            "reconnect_count": self.reconnect_count,
            "retry_count": self.camera_open_retry_count,
            "uptime": time.time() - self.last_reconnect_time if self.last_reconnect_time > 0 else 0
        }
        
        # 如果摄像头已连接，尝试获取其属性
        if self.cap is not None and self.cap.isOpened():
            try:
                status["actual_width"] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                status["actual_height"] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                status["actual_fps"] = round(self.cap.get(cv2.CAP_PROP_FPS), 1)
                status["backend"] = int(self.cap.get(cv2.CAP_PROP_BACKEND))
            except:
                pass
                
        return status
    
    def stop(self):
        """停止摄像头帧捕获"""
        self.running = False
        time.sleep(0.5)  # 等待捕获线程退出
        
        # 清空所有队列
        for q in self.consumers.values():
            while not q.empty():
                try:
                    q.get_nowait()
                except:
                    pass
        
        # 释放摄像头资源
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        logger.info("摄像头管理器已停止")

# 全局单例实例
_camera_manager_instance = None

def get_camera_manager(init=False, **kwargs):
    """
    获取摄像头管理器的全局单例实例
    
    Args:
        init: 是否初始化摄像头
        **kwargs: 传递给CameraManager的参数
        
    Returns:
        CameraManager实例
    """
    global _camera_manager_instance
    
    if _camera_manager_instance is None:
        _camera_manager_instance = CameraManager(**kwargs)
        if init:
            _camera_manager_instance.start()
    
    return _camera_manager_instance
