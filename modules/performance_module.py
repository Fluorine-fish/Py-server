import cv2
import numpy as np
import psutil
import time
from threading import Lock
import logging
import threading
from collections import deque
from typing import Dict, List

class PerformanceOptimizer:
    def __init__(self):
        self.memory_monitor = MemoryMonitor()
        self.camera_manager = CameraManager()
        self.network_adapter = NetworkAdapter()
        self.error_handler = ErrorHandler()
        
class MemoryMonitor:
    def __init__(self, max_memory_percent=75):
        self.max_memory_percent = max_memory_percent
        self.frame_buffer = []
        self.buffer_lock = Lock()
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # 60秒检查一次
        
    def check_memory_usage(self):
        """检查内存使用情况"""
        memory = psutil.Process().memory_percent()
        return memory <= self.max_memory_percent
        
    def manage_frame_buffer(self, frame):
        """管理帧缓冲区"""
        current_time = time.time()
        
        # 定期清理
        if current_time - self.last_cleanup > self.cleanup_interval:
            with self.buffer_lock:
                # 只保留最近5秒的帧
                cutoff_time = current_time - 5
                self.frame_buffer = [f for f in self.frame_buffer if f['timestamp'] > cutoff_time]
            self.last_cleanup = current_time
            
        # 检查内存使用
        if not self.check_memory_usage():
            with self.buffer_lock:
                # 清理一半的缓存
                self.frame_buffer = self.frame_buffer[len(self.frame_buffer)//2:]
                
        # 添加新帧
        with self.buffer_lock:
            self.frame_buffer.append({
                'frame': frame,
                'timestamp': current_time
            })
            
    def get_recent_frames(self, seconds=1):
        """获取最近的帧"""
        current_time = time.time()
        with self.buffer_lock:
            return [f['frame'] for f in self.frame_buffer 
                   if current_time - f['timestamp'] <= seconds]
                   
class CameraManager:
    def __init__(self):
        self.current_camera = None
        self.camera_lock = Lock()
        self.fallback_resolutions = [
            (1920, 1080),
            (1280, 720),
            (854, 480),
            (640, 480),
            (320, 240)
        ]
        
    def initialize_camera(self, camera_id=0):
        """初始化摄像头"""
        with self.camera_lock:
            if self.current_camera is not None:
                self.current_camera.release()
                
            # 尝试不同的后端
            backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2]
            
            for backend in backends:
                camera = cv2.VideoCapture(camera_id + backend)
                if camera.isOpened():
                    # 尝试设置最佳分辨率
                    for resolution in self.fallback_resolutions:
                        camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
                        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
                        
                        # 检查是否成功设置
                        actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
                        actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        
                        if actual_width > 0 and actual_height > 0:
                            self.current_camera = camera
                            return True
                            
                    # 如果无法设置任何分辨率，也返回成功
                    self.current_camera = camera
                    return True
                    
            return False
            
    def read_frame(self):
        """读取帧"""
        with self.camera_lock:
            if self.current_camera is None:
                return None
                
            ret, frame = self.current_camera.read()
            if not ret:
                # 尝试重新初始化摄像头
                if self.initialize_camera():
                    return self.read_frame()
                return None
                
            return frame
            
    def release(self):
        """释放摄像头"""
        with self.camera_lock:
            if self.current_camera is not None:
                self.current_camera.release()
                self.current_camera = None
                
class NetworkAdapter:
    def __init__(self):
        self.quality = 90
        self.min_quality = 10
        self.max_quality = 100
        self.target_size = 100 * 1024  # 目标100KB
        self.adaptation_rate = 0.1
        
    def adapt_quality(self, frame_size):
        """根据帧大小调整质量"""
        if frame_size > self.target_size:
            # 降低质量
            self.quality = max(self.min_quality, 
                             self.quality - self.adaptation_rate * (frame_size / self.target_size))
        else:
            # 提高质量
            self.quality = min(self.max_quality, 
                             self.quality + self.adaptation_rate)
        return int(self.quality)
        
    def compress_frame(self, frame):
        """压缩帧"""
        if frame is None:
            return None
            
        # 编码
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
        _, encoded = cv2.imencode('.jpg', frame, encode_param)
        
        # 调整质量
        self.adapt_quality(len(encoded))
        
        return encoded
        
class ErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.max_retries = 3
        self.error_threshold = 5
        self.recovery_interval = 60  # 60秒后重置错误计数
        self.last_error_time = 0
        
    def handle_error(self, error_type, error_message):
        """处理错误"""
        current_time = time.time()
        
        # 重置错误计数
        if current_time - self.last_error_time > self.recovery_interval:
            self.error_count = 0
            
        self.error_count += 1
        self.last_error_time = current_time
        
        # 记录错误
        logging.error(f"Error type: {error_type}, Message: {error_message}")
        
        # 检查是否需要系统重置
        if self.error_count >= self.error_threshold:
            return 'reset'
        elif self.error_count >= self.max_retries:
            return 'retry'
        else:
            return 'continue'
            
    def reset_error_count(self):
        """重置错误计数"""
        self.error_count = 0
        self.last_error_time = 0

class PerformanceMonitor:
    def __init__(self, window_size: int = 60):
        """初始化性能监控器
        
        Args:
            window_size: 性能指标的滑动窗口大小（秒）
        """
        self.window_size = window_size
        self.cpu_usage = deque(maxlen=window_size)
        self.memory_usage = deque(maxlen=window_size)
        self.gpu_usage = deque(maxlen=window_size)
        self.disk_io = deque(maxlen=window_size)
        self.network_io = deque(maxlen=window_size)
        
        self.monitoring = False
        self.monitor_thread = None
        
        # 性能警告阈值
        self.thresholds = {
            'cpu': 80.0,  # CPU使用率警告阈值
            'memory': 85.0,  # 内存使用率警告阈值
            'disk_io': 80.0,  # 磁盘IO使用率警告阈值
            'gpu': 85.0  # GPU使用率警告阈值（如果可用）
        }
        
        # 性能优化建议
        self._optimization_suggestions = []
        
    def start_monitoring(self):
        """开始性能监控"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """性能监控主循环"""
        while self.monitoring:
            # 收集性能指标
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # 收集网络IO
            net_io = psutil.net_io_counters()
            
            # 更新性能指标队列
            self.cpu_usage.append(cpu)
            self.memory_usage.append(memory)
            self.disk_io.append(disk)
            self.network_io.append((net_io.bytes_sent, net_io.bytes_recv))
            
            # 检查性能问题并生成建议
            self._check_performance_issues()
            
            time.sleep(1)
            
    def _check_performance_issues(self):
        """检查性能问题并生成优化建议"""
        self._optimization_suggestions.clear()
        
        # 检查CPU使用率
        avg_cpu = np.mean(self.cpu_usage) if self.cpu_usage else 0
        if avg_cpu > self.thresholds['cpu']:
            self._optimization_suggestions.append({
                'component': 'CPU',
                'severity': 'high' if avg_cpu > 90 else 'medium',
                'message': f'CPU使用率过高 ({avg_cpu:.1f}%)',
                'suggestion': '考虑减少视频处理分辨率或帧率'
            })
            
        # 检查内存使用率
        avg_memory = np.mean(self.memory_usage) if self.memory_usage else 0
        if avg_memory > self.thresholds['memory']:
            self._optimization_suggestions.append({
                'component': 'Memory',
                'severity': 'high' if avg_memory > 90 else 'medium',
                'message': f'内存使用率过高 ({avg_memory:.1f}%)',
                'suggestion': '检查内存泄漏或减少缓存大小'
            })
            
        # 检查磁盘IO
        avg_disk = np.mean(self.disk_io) if self.disk_io else 0
        if avg_disk > self.thresholds['disk_io']:
            self._optimization_suggestions.append({
                'component': 'Disk',
                'severity': 'medium',
                'message': f'磁盘使用率过高 ({avg_disk:.1f}%)',
                'suggestion': '考虑清理临时文件或优化存储策略'
            })
            
    def get_performance_metrics(self) -> Dict:
        """获取当前性能指标"""
        return {
            'cpu': {
                'current': self.cpu_usage[-1] if self.cpu_usage else 0,
                'average': np.mean(self.cpu_usage) if self.cpu_usage else 0,
                'history': list(self.cpu_usage)
            },
            'memory': {
                'current': self.memory_usage[-1] if self.memory_usage else 0,
                'average': np.mean(self.memory_usage) if self.memory_usage else 0,
                'history': list(self.memory_usage)
            },
            'disk': {
                'current': self.disk_io[-1] if self.disk_io else 0,
                'average': np.mean(self.disk_io) if self.disk_io else 0,
                'history': list(self.disk_io)
            },
            'network': {
                'current': self.network_io[-1] if self.network_io else (0, 0),
                'history': list(self.network_io)
            }
        }
        
    def get_optimization_suggestions(self) -> List[Dict]:
        """获取性能优化建议"""
        return self._optimization_suggestions
        
    def set_threshold(self, component: str, value: float):
        """设置性能警告阈值
        
        Args:
            component: 组件名称 ('cpu', 'memory', 'disk_io', 'gpu')
            value: 阈值（百分比）
        """
        if component in self.thresholds and 0 <= value <= 100:
            self.thresholds[component] = value
            return True
        return False

class BandwidthAdaptor:
    def __init__(self, initial_quality: int = 90):
        """初始化带宽适配器
        
        Args:
            initial_quality: 初始视频质量（1-100）
        """
        self.current_quality = initial_quality
        self.network_speed_history = deque(maxlen=30)  # 30秒历史记录
        self.last_adjustment_time = 0
        self.adjustment_interval = 5  # 5秒调整间隔
        
        # 带宽阈值（字节/秒）
        self.bandwidth_thresholds = {
            'low': 500000,    # 500KB/s
            'medium': 2000000,  # 2MB/s
            'high': 5000000    # 5MB/s
        }
        
    def update_network_speed(self, bytes_per_second: float):
        """更新网络速度历史记录
        
        Args:
            bytes_per_second: 当前网络速度（字节/秒）
        """
        self.network_speed_history.append(bytes_per_second)
        
        current_time = time.time()
        if current_time - self.last_adjustment_time >= self.adjustment_interval:
            self._adjust_quality()
            self.last_adjustment_time = current_time
            
    def _adjust_quality(self):
        """根据网络状况调整视频质量"""
        if not self.network_speed_history:
            return
            
        avg_speed = np.mean(self.network_speed_history)
        
        # 根据网络速度调整质量
        if avg_speed < self.bandwidth_thresholds['low']:
            self.current_quality = max(30, self.current_quality - 20)
        elif avg_speed < self.bandwidth_thresholds['medium']:
            self.current_quality = max(50, self.current_quality - 10)
        elif avg_speed > self.bandwidth_thresholds['high']:
            self.current_quality = min(90, self.current_quality + 10)
        else:
            self.current_quality = min(70, max(60, self.current_quality))
            
    def get_recommended_quality(self) -> int:
        """获取推荐的视频质量设置"""
        return self.current_quality
        
    def get_network_status(self) -> Dict:
        """获取网络状态信息"""
        avg_speed = np.mean(self.network_speed_history) if self.network_speed_history else 0
        return {
            'current_quality': self.current_quality,
            'average_speed_bps': avg_speed,
            'speed_history': list(self.network_speed_history),
            'bandwidth_level': self._get_bandwidth_level(avg_speed)
        }
        
    def _get_bandwidth_level(self, speed: float) -> str:
        """获取带宽等级"""
        if speed < self.bandwidth_thresholds['low']:
            return 'low'
        elif speed < self.bandwidth_thresholds['medium']:
            return 'medium'
        else:
            return 'high'
            
    def set_bandwidth_threshold(self, level: str, value: int):
        """设置带宽阈值
        
        Args:
            level: 级别 ('low', 'medium', 'high')
            value: 阈值（字节/秒）
        """
        if level in self.bandwidth_thresholds:
            self.bandwidth_thresholds[level] = value
            return True
        return False

class ErrorRecovery:
    def __init__(self):
        """初始化错误恢复系统"""
        self.error_history = deque(maxlen=100)
        self.recovery_actions = {
            'camera_error': self._handle_camera_error,
            'network_error': self._handle_network_error,
            'processing_error': self._handle_processing_error
        }
        
    def handle_error(self, error_type: str, error_details: Dict):
        """处理错误并尝试恢复
        
        Args:
            error_type: 错误类型
            error_details: 错误详情
        """
        self.error_history.append({
            'type': error_type,
            'details': error_details,
            'timestamp': time.time()
        })
        
        if error_type in self.recovery_actions:
            return self.recovery_actions[error_type](error_details)
        return False
        
    def _handle_camera_error(self, details: Dict):
        """处理摄像头错误"""
        # 实现摄像头重连逻辑
        try:
            if details.get('device'):
                # 尝试重新打开摄像头
                import cv2
                cap = cv2.VideoCapture(details['device'])
                if cap.isOpened():
                    cap.release()
                    return True
        except Exception:
            pass
        return False
        
    def _handle_network_error(self, details: Dict):
        """处理网络错误"""
        # 实现网络错误恢复逻辑
        try:
            import socket
            # 尝试重新建立连接
            if details.get('host') and details.get('port'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((details['host'], details['port']))
                sock.close()
                return True
        except Exception:
            pass
        return False
        
    def _handle_processing_error(self, details: Dict):
        """处理处理错误"""
        # 实现处理错误恢复逻辑
        try:
            if details.get('process_id'):
                process = psutil.Process(details['process_id'])
                if process.status() == psutil.STATUS_ZOMBIE:
                    process.terminate()
                return True
        except Exception:
            pass
        return False
        
    def get_error_history(self) -> List[Dict]:
        """获取错误历史记录"""
        return list(self.error_history)
        
    def clear_error_history(self):
        """清除错误历史记录"""
        self.error_history.clear()

# 创建全局性能管理器实例
performance_monitor = PerformanceMonitor()
bandwidth_adaptor = BandwidthAdaptor()
error_recovery = ErrorRecovery()