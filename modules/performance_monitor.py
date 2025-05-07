"""
性能监控模块 - 提供性能监控和自适应优化功能
从原始posture_module.py拆分而来，减少单个文件代码量
"""
import time
from collections import deque

# 性能优化相关常量
TARGET_FPS = 25.0  # 目标帧率
FPS_THRESHOLD_LOW = 15.0  # 低帧率阈值，低于此值降低分辨率
FPS_THRESHOLD_HIGH = 28.0  # 高帧率阈值，高于此值可以尝试提高分辨率
RESOLUTION_ADJUST_INTERVAL = 5.0  # 分辨率调整间隔（秒）

class PerformanceMonitor:
    """性能监控和自适应优化器"""
    
    def __init__(self, resolution_levels):
        """
        初始化性能监控器
        
        Args:
            resolution_levels: 可用的分辨率级别列表 [(width, height), ...]
        """
        self.resolution_levels = resolution_levels
        self.current_resolution_index = 1  # 从中等分辨率开始
        self.last_resolution_adjust_time = 0
        self.adaptive_resolution = True  # 是否启用自适应分辨率
        
        # 性能优化参数
        self.skip_frames_when_slow = True  # 在处理过慢时允许跳帧
        self.skip_count = 0  # 当前跳帧计数
        self.max_consecutive_skips = 3  # 最大连续跳帧数
        
        # 性能监控
        self.performance_stats = {
            'camera_errors': 0,
            'processing_times': deque(maxlen=100),
            'skipped_frames': 0,
            'last_reconnect_time': 0,
            'reconnect_interval': 10.0  # 重连间隔（秒）
        }
    
    def get_current_resolution(self):
        """
        获取当前处理分辨率
        
        Returns:
            (width, height): 当前处理分辨率
        """
        return self.resolution_levels[self.current_resolution_index]
    
    def adjust_resolution(self, pose_fps, emotion_fps):
        """
        根据当前帧率动态调整处理分辨率
        
        Args:
            pose_fps: 姿势处理帧率
            emotion_fps: 情绪处理帧率
            
        Returns:
            changed: 分辨率是否变更
        """
        current_time = time.time()
        
        # 检查是否到达调整间隔
        if not self.adaptive_resolution or (current_time - self.last_resolution_adjust_time) < RESOLUTION_ADJUST_INTERVAL:
            return False
            
        process_fps = min(pose_fps, emotion_fps)
        changed = False
        
        # 当帧率过低时降低分辨率
        if process_fps < FPS_THRESHOLD_LOW and self.current_resolution_index < len(self.resolution_levels) - 1:
            self.current_resolution_index += 1
            self.last_resolution_adjust_time = current_time
            changed = True
            
        # 当帧率足够高时提高分辨率
        elif process_fps > FPS_THRESHOLD_HIGH and self.current_resolution_index > 0:
            self.current_resolution_index -= 1
            self.last_resolution_adjust_time = current_time
            changed = True
        
        return changed
    
    def should_skip_frame(self, camera_fps):
        """
        根据当前处理性能决定是否需要跳过当前帧
        
        Args:
            camera_fps: 摄像头帧率
            
        Returns:
            skip: 是否应该跳过这一帧
        """
        if not self.skip_frames_when_slow:
            self.skip_count = 0
            return False
        
        # 计算平均处理时间
        avg_processing_time = 0
        if self.performance_stats['processing_times']:
            avg_processing_time = sum(self.performance_stats['processing_times']) / len(self.performance_stats['processing_times'])
        
        # 处理时间超过帧间时间的90%时需要跳帧
        frame_time = 1.0 / camera_fps if camera_fps > 0 else 0.033  # 默认30fps
        
        if avg_processing_time > frame_time * 0.9:
            # 需要跳帧但不超过最大连续跳帧数
            if self.skip_count < self.max_consecutive_skips:
                self.skip_count += 1
                self.performance_stats['skipped_frames'] += 1
                return True
            else:
                # 达到最大跳帧数，重置计数并处理这一帧
                self.skip_count = 0
                return False
        else:
            # 处理时间可接受，不需要跳帧
            self.skip_count = 0
            return False
    
    def record_processing_time(self, processing_time):
        """
        记录一帧的处理时间
        
        Args:
            processing_time: 处理时间(秒)
        """
        self.performance_stats['processing_times'].append(processing_time)
    
    def record_camera_error(self):
        """记录一次摄像头错误"""
        self.performance_stats['camera_errors'] += 1
    
    def should_reconnect(self, consecutive_failures):
        """
        是否应该尝试重新连接摄像头
        
        Args:
            consecutive_failures: 连续失败次数
            
        Returns:
            should_reconnect: 是否应该重新连接
        """
        current_time = time.time()
        
        if (consecutive_failures > 5 and 
            (current_time - self.performance_stats['last_reconnect_time']) > self.performance_stats['reconnect_interval']):
            self.performance_stats['last_reconnect_time'] = current_time
            return True
        
        return False
    
    def set_resolution_mode(self, adaptive=True, resolution_index=None):
        """
        设置分辨率模式
        
        Args:
            adaptive: 是否启用自适应分辨率调整
            resolution_index: 如果不使用自适应模式，设置固定分辨率索引
            
        Returns:
            success: 设置是否成功
        """
        self.adaptive_resolution = adaptive
        
        if resolution_index is not None and 0 <= resolution_index < len(self.resolution_levels):
            self.current_resolution_index = resolution_index
            
        return True
    
    def set_performance_mode(self, skip_frames=None, max_skips=None):
        """
        设置性能优化模式
        
        Args:
            skip_frames: 是否在处理过慢时跳帧
            max_skips: 最大连续跳帧数
            
        Returns:
            success: 设置是否成功
        """
        if skip_frames is not None:
            self.skip_frames_when_slow = skip_frames
        
        if max_skips is not None and max_skips > 0:
            self.max_consecutive_skips = max_skips
        
        return True
    
    def get_performance_stats(self):
        """
        获取性能统计信息
        
        Returns:
            stats: 性能统计信息字典
        """
        avg_processing_ms = 0
        if self.performance_stats['processing_times']:
            avg_processing_ms = sum(self.performance_stats['processing_times']) / len(self.performance_stats['processing_times']) * 1000
        
        width, height = self.resolution_levels[self.current_resolution_index]
        
        return {
            'skipped_frames': self.performance_stats['skipped_frames'],
            'camera_errors': self.performance_stats['camera_errors'],
            'avg_processing_time_ms': round(avg_processing_ms, 2),
            'current_resolution': f"{width}x{height}",
            'adaptive_mode': self.adaptive_resolution,
            'skip_frames_enabled': self.skip_frames_when_slow,
            'max_consecutive_skips': self.max_consecutive_skips
        }