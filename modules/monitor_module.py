"""
监控器模块 - 处理坐姿和久坐检测
"""
import time
from datetime import datetime, timedelta
import numpy as np
from .serial_module import SerialCommunicationHandler
from .posture_module import PostureDetector
from .logging_module import log_manager

class ChildMonitor:
    def __init__(self, serial_handler: SerialCommunicationHandler):
        self.serial_handler = serial_handler
        self.posture_detector = PostureDetector()
        
        # 坐姿监控参数
        self.bad_posture_threshold = 20  # 连续不良姿势的阈值（秒）
        self.continuous_bad_posture_start = None  # 开始不良姿势的时间
        self.last_posture_warning = 0  # 上次姿势警告时间
        self.posture_warning_cooldown = 60  # 姿势警告冷却时间（秒）
        
        # 久坐监控参数
        self.sitting_threshold = 30  # 久坐时间阈值（分钟）
        self.sitting_start_time = None  # 开始坐下的时间
        self.last_sitting_warning = 0  # 上次久坐警告时间
        self.sitting_warning_cooldown = 300  # 久坐警告冷却时间（秒）
        
        # 活动记录
        self.activity_history = []  # 存储活动记录
        self.max_history_size = 1000  # 最大历史记录数量
        
    def process_frame(self, frame):
        """处理单帧图像"""
        current_time = time.time()
        
        # 检测姿势
        posture_result = self.posture_detector.detect_posture(frame)
        
        # 处理姿势监控
        if posture_result['quality'] in ['bad', 'severe']:
            if self.continuous_bad_posture_start is None:
                self.continuous_bad_posture_start = current_time
            elif (current_time - self.continuous_bad_posture_start >= self.bad_posture_threshold and 
                  current_time - self.last_posture_warning >= self.posture_warning_cooldown):
                self._trigger_posture_warning()
                self.last_posture_warning = current_time
        else:
            self.continuous_bad_posture_start = None
        
        # 处理久坐监控
        if not posture_result['is_occluded']:
            if self.sitting_start_time is None:
                self.sitting_start_time = current_time
            elif (current_time - self.sitting_start_time >= self.sitting_threshold * 60 and 
                  current_time - self.last_sitting_warning >= self.sitting_warning_cooldown):
                self._trigger_sitting_warning()
                self.last_sitting_warning = current_time
        else:
            # 如果检测不到人，重置久坐计时
            self.sitting_start_time = None
        
        # 记录活动
        self._record_activity(posture_result)
        
        return {
            'posture_status': posture_result['quality'],
            'head_angle': posture_result['angle'],
            'is_occluded': posture_result['is_occluded'],
            'continuous_bad_posture_time': (current_time - self.continuous_bad_posture_start) if self.continuous_bad_posture_start else 0,
            'sitting_time': (current_time - self.sitting_start_time) if self.sitting_start_time else 0
        }
    
    def _trigger_posture_warning(self):
        """触发姿势警告"""
        log_manager.warning("检测到不良姿势，发送提醒")
        # 发送姿势矫正指令到机械臂
        correction_data = {
            'command': 'posture_correction',
            'angle': self.posture_detector.last_valid_angle
        }
        self.serial_handler.send_command(correction_data)
    
    def _trigger_sitting_warning(self):
        """触发久坐警告"""
        log_manager.warning("检测到久坐行为，发送提醒")
        # 发送久坐提醒指令到机械臂
        reminder_data = {
            'command': 'sitting_reminder',
            'duration': int((time.time() - self.sitting_start_time) / 60)  # 转换为分钟
        }
        self.serial_handler.send_command(reminder_data)
    
    def _record_activity(self, posture_result):
        """记录活动数据"""
        activity = {
            'timestamp': datetime.now(),
            'posture_quality': posture_result['quality'],
            'head_angle': posture_result['angle'],
            'is_occluded': posture_result['is_occluded']
        }
        
        self.activity_history.append(activity)
        if len(self.activity_history) > self.max_history_size:
            self.activity_history.pop(0)
    
    def get_statistics(self, time_range=None):
        """获取统计数据
        
        Args:
            time_range: 可选的时间范围（小时），默认返回所有记录的统计
        
        Returns:
            统计数据字典
        """
        if not self.activity_history:
            return {
                'total_records': 0,
                'good_posture_percentage': 0,
                'bad_posture_percentage': 0,
                'average_head_angle': 0,
                'max_continuous_bad_posture': 0,
                'max_continuous_sitting': 0
            }
        
        if time_range:
            cutoff_time = datetime.now() - timedelta(hours=time_range)
            filtered_history = [record for record in self.activity_history 
                             if record['timestamp'] >= cutoff_time]
        else:
            filtered_history = self.activity_history
        
        if not filtered_history:
            return {
                'total_records': 0,
                'good_posture_percentage': 0,
                'bad_posture_percentage': 0,
                'average_head_angle': 0,
                'max_continuous_bad_posture': 0,
                'max_continuous_sitting': 0
            }
        
        # 计算基本统计数据
        total_records = len(filtered_history)
        good_postures = sum(1 for record in filtered_history 
                          if record['posture_quality'] == 'good')
        bad_postures = sum(1 for record in filtered_history 
                         if record['posture_quality'] in ['bad', 'severe'])
        
        valid_angles = [record['head_angle'] for record in filtered_history 
                       if record['head_angle'] is not None]
        
        return {
            'total_records': total_records,
            'good_posture_percentage': (good_postures / total_records) * 100,
            'bad_posture_percentage': (bad_postures / total_records) * 100,
            'average_head_angle': np.mean(valid_angles) if valid_angles else 0,
            'max_continuous_bad_posture': self._calculate_max_continuous_bad_posture(filtered_history),
            'max_continuous_sitting': self._calculate_max_continuous_sitting(filtered_history)
        }
    
    def _calculate_max_continuous_bad_posture(self, history):
        """计算最长连续不良姿势时间（秒）"""
        if not history:
            return 0
        
        max_duration = 0
        current_duration = 0
        last_timestamp = None
        
        for record in history:
            if record['posture_quality'] in ['bad', 'severe']:
                if last_timestamp:
                    time_diff = (record['timestamp'] - last_timestamp).total_seconds()
                    if time_diff < 5:  # 允许5秒内的间隔
                        current_duration += time_diff
                    else:
                        current_duration = 0
                last_timestamp = record['timestamp']
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
                last_timestamp = None
        
        return max_duration
    
    def _calculate_max_continuous_sitting(self, history):
        """计算最长连续久坐时间（分钟）"""
        if not history:
            return 0
        
        max_duration = 0
        current_duration = 0
        last_timestamp = None
        
        for record in history:
            if not record['is_occluded']:
                if last_timestamp:
                    time_diff = (record['timestamp'] - last_timestamp).total_seconds()
                    if time_diff < 60:  # 允许1分钟内的间隔
                        current_duration += time_diff
                    else:
                        current_duration = 0
                last_timestamp = record['timestamp']
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
                last_timestamp = None
        
        return max_duration / 60  # 转换为分钟
    
    def reset_warnings(self):
        """重置所有警告计时器"""
        self.continuous_bad_posture_start = None
        self.last_posture_warning = 0
        self.sitting_start_time = None
        self.last_sitting_warning = 0
    
    def reconfigure(self, config):
        """重新配置监控参数
        
        Args:
            config: 包含新配置的字典
        """
        if 'bad_posture_threshold' in config:
            self.bad_posture_threshold = config['bad_posture_threshold']
        if 'sitting_threshold' in config:
            self.sitting_threshold = config['sitting_threshold']
        if 'posture_warning_cooldown' in config:
            self.posture_warning_cooldown = config['posture_warning_cooldown']
        if 'sitting_warning_cooldown' in config:
            self.sitting_warning_cooldown = config['sitting_warning_cooldown']
        
        # 同时更新姿势检测器的参数
        if 'head_angle_threshold' in config:
            self.posture_detector.reconfigure(
                head_angle_threshold=config['head_angle_threshold']
            )