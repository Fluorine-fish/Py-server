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

"""久坐监控模块 - 检测和提醒儿童久坐行为"""
import time
from datetime import datetime, timedelta
from .logging_module import log_manager
from .serial_module import SerialCommunicationHandler

class SittingMonitor:
    def __init__(self, serial_handler: SerialCommunicationHandler):
        self.serial_handler = serial_handler
        
        # 久坐检测参数（针对儿童设置更短的时间）
        self.sitting_threshold = 20  # 久坐阈值（分钟）
        self.warning_interval = 5    # 提醒间隔（分钟）
        self.break_duration = 3      # 建议休息时长（分钟）
        
        # 活动状态追踪
        self.last_movement_time = datetime.now()
        self.last_warning_time = datetime.now()
        self.is_sitting = False
        self.continuous_sitting_duration = 0
        
        # 活动检测阈值
        self.movement_threshold = 0.2  # 移动检测阈值（弧度）
        self.standing_threshold = 5.0  # 起立检测阈值（秒）
        
    def update_status(self, posture_data):
        """更新活动状态
        
        Args:
            posture_data: 包含姿势信息的字典
        """
        current_time = datetime.now()
        
        # 检测是否有显著移动
        if self._detect_movement(posture_data):
            if not self.is_sitting:
                self.last_movement_time = current_time
            self.is_sitting = True
            
        # 计算持续坐姿时间
        if self.is_sitting:
            self.continuous_sitting_duration = (current_time - self.last_movement_time).total_seconds() / 60
            
            # 检查是否需要发送久坐提醒
            if self._should_send_reminder():
                self.send_sitting_reminder()
                self.last_warning_time = current_time
        
    def _detect_movement(self, posture_data):
        """检测是否有显著移动
        
        Args:
            posture_data: 包含姿势信息的字典
            
        Returns:
            bool: 是否检测到显著移动
        """
        # 提取关键角度数据
        head_angle = posture_data.get('head_angle', 0)
        neck_angle = posture_data.get('neck_angle', 0)
        spine_angle = posture_data.get('spine_angle', 0)
        
        # 任何角度变化超过阈值都认为是显著移动
        return (abs(head_angle) > self.movement_threshold or
                abs(neck_angle) > self.movement_threshold or
                abs(spine_angle) > self.movement_threshold)
    
    def _should_send_reminder(self):
        """检查是否应该发送久坐提醒"""
        if not self.is_sitting:
            return False
            
        # 检查是否超过久坐阈值
        if self.continuous_sitting_duration < self.sitting_threshold:
            return False
            
        # 检查是否达到提醒间隔
        time_since_last_warning = (datetime.now() - self.last_warning_time).total_seconds() / 60
        return time_since_last_warning >= self.warning_interval
    
    def send_sitting_reminder(self):
        """发送久坐提醒"""
        try:
            success = self.serial_handler.send_sitting_reminder(int(self.continuous_sitting_duration))
            if success:
                log_manager.info(f"发送久坐提醒成功：已持续静坐 {int(self.continuous_sitting_duration)} 分钟")
            else:
                log_manager.error("发送久坐提醒失败")
        except Exception as e:
            log_manager.error(f"发送久坐提醒时出错: {str(e)}")
    
    def record_standing(self):
        """记录起立活动"""
        self.is_sitting = False
        self.continuous_sitting_duration = 0
        self.last_movement_time = datetime.now()
        log_manager.info("检测到起立活动，重置久坐计时")
    
    def get_status(self):
        """获取当前状态信息"""
        return {
            'is_sitting': self.is_sitting,
            'continuous_sitting_duration': self.continuous_sitting_duration,
            'last_movement': self.last_movement_time.isoformat(),
            'last_warning': self.last_warning_time.isoformat()
        }

# 创建全局久坐监控器实例
sitting_monitor = None

def initialize_monitor(serial_handler):
    """初始化久坐监控器"""
    global sitting_monitor
    sitting_monitor = SittingMonitor(serial_handler)
    return sitting_monitor