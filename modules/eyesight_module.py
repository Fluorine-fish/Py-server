import cv2
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
from .logging_module import log_manager

class EyesightProtector:
    def __init__(self):
        self.screen_time_start = None
        self.last_break_time = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # 儿童用眼保护参数
        self.break_interval = 30  # 建议休息间隔（分钟）- 因为是小孩子所以缩短到30分钟
        self.break_duration = 3   # 建议休息时长（分钟）
        self.min_safe_distance = 33  # 最小安全读写距离（厘米）- 根据儿童用眼卫生标准
        self.max_safe_distance = 40  # 最大安全读写距离（厘米）
        
        # 照明标准（基于《中小学生学习用灯具》标准）
        self.min_light = 300      # 最低照度(lux)
        self.optimal_light = 500  # 最佳照度(lux)
        self.max_light = 750      # 最高照度(lux)
        
        # 头部角度限制
        self.max_head_tilt = 20   # 最大头部倾斜角度
        self.max_head_down = 25   # 最大低头角度
        
        # 状态追踪
        self.continuous_usage_time = 0
        self.distance_warnings = []
        self.posture_warnings = []
        self.light_warnings = []
        self.blink_rate_history = []
        self.last_blink_check = time.time()
        
        # 初始化日志记录
        self.logger = logging.getLogger('system')
        
    def start_screen_time_tracking(self):
        """开始追踪屏幕使用时间"""
        self.screen_time_start = datetime.now()
        self.last_break_time = datetime.now()
        self.logger.info("开始追踪屏幕使用时间")
        
    def calculate_reading_distance(self, face_width_pixels: int, frame_width: int) -> float:
        """根据人脸宽度估算读写距离
        
        针对儿童读写场景优化的距离计算
        Args:
            face_width_pixels: 图像中人脸宽度（像素）
            frame_width: 图像宽度（像素）
            
        Returns:
            估算的阅读距离（厘米）
        """
        # 儿童平均脸部宽度（8-12岁）约为13.5厘米
        CHILD_FACE_WIDTH = 13.5  # cm
        # 台灯摄像头的视场角
        CAMERA_FOV = 65  # degrees
        
        # 计算距离
        distance = (CHILD_FACE_WIDTH * frame_width) / (2 * face_width_pixels * np.tan(np.radians(CAMERA_FOV/2)))
        return distance
        
    def detect_blink_rate(self, frame) -> int:
        """检测眨眼频率
        
        Args:
            frame: 视频帧
            
        Returns:
            估算的每分钟眨眼次数
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        blinks = 0
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            if len(eyes) == 2:  # 检测到两只眼睛
                for (ex, ey, ew, eh) in eyes:
                    eye_roi = roi_gray[ey:ey+eh, ex:ex+ew]
                    # 使用眼睛区域的平均亮度来估计眨眼
                    if np.mean(eye_roi) < 50:  # 阈值可调整
                        blinks += 1
                        
        # 更新眨眼历史记录
        current_time = time.time()
        time_diff = current_time - self.last_blink_check
        if time_diff >= 60:  # 每分钟更新一次
            blinks_per_minute = int(blinks * (60 / time_diff))
            self.blink_rate_history.append(blinks_per_minute)
            self.last_blink_check = current_time
            
        return blinks

    def calculate_light_level(self, frame) -> Dict[str, float]:
        """计算照明水平
        
        考虑台灯光源和环境光的综合效果
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 将图像分为上中下三个区域
        height = gray.shape[0]
        top = gray[0:height//3]
        middle = gray[height//3:2*height//3]
        bottom = gray[2*height//3:]
        
        # 计算各区域亮度
        avg_top = np.mean(top)
        avg_middle = np.mean(middle)
        avg_bottom = np.mean(bottom)
        
        # 重点关注阅读区域（中下部分）
        reading_area = np.mean([avg_middle, avg_bottom])
        
        # 粗略转换为lux (考虑台灯光源特性)
        # 由于台灯为定向光源，需要调整转换系数
        reading_lux = reading_area * 6.5  # 调整后的转换系数
        ambient_lux = avg_top * 4.5       # 环境光转换系数
        
        return {
            'reading_area': reading_lux,
            'ambient': ambient_lux,
            'overall': (reading_lux + ambient_lux) / 2
        }

    def detect_head_posture(self, face_landmarks) -> Dict[str, float]:
        """检测头部姿势
        
        针对儿童读写场景的头部姿势检测
        """
        if not face_landmarks:
            return None
            
        # 计算头部倾斜角度和低头角度
        # 这里需要根据实际的face_landmarks结构来实现
        # 返回示例：
        return {
            'tilt_angle': 15.0,  # 头部左右倾斜角度
            'down_angle': 20.0   # 头部低垂角度
        }

    def process_frame(self, frame) -> Tuple[Dict, List[str]]:
        """处理视频帧并生成保护建议"""
        if frame is None:
            return {}, []
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        metrics = {
            'face_detected': len(faces) > 0,
            'distance': None,
            'light_levels': None,
            'head_posture': None,
            'blink_rate': None,
            'continuous_usage_time': self.continuous_usage_time
        }
        
        suggestions = []
        
        # 检查是否需要休息
        if self.screen_time_start:
            current_time = datetime.now()
            time_since_last_break = (current_time - self.last_break_time).total_seconds() / 60
            
            if time_since_last_break >= self.break_interval:
                suggestions.append(f"孩子已经连续用眼{int(time_since_last_break)}分钟了，建议休息{self.break_duration}分钟，可以做做眼保健操或远眺放松一下")
                
        # 检测阅读距离
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                distance = self.calculate_reading_distance(w, frame.shape[1])
                metrics['distance'] = distance
                
                if distance < self.min_safe_distance:
                    suggestions.append("提醒孩子保持正确的读写距离，不要离得太近，可以用一个拳头的距离作为参考")
                    self.distance_warnings.append(time.time())
                elif distance > self.max_safe_distance:
                    suggestions.append("建议调整台灯位置或坐姿，当前与读写内容的距离略远")
                    
        # 检测照明情况
        light_levels = self.calculate_light_level(frame)
        metrics['light_levels'] = light_levels
        
        if light_levels['reading_area'] < self.min_light:
            suggestions.append("当前照明不足，建议调整台灯角度或调高亮度")
            self.light_warnings.append(time.time())
        elif light_levels['reading_area'] > self.max_light:
            suggestions.append("当前照明太强，可能会导致视觉疲劳，建议适当调低台灯亮度")
            
        # 检测眨眼频率
        blinks = self.detect_blink_rate(frame)
        if self.blink_rate_history:
            avg_blink_rate = np.mean(self.blink_rate_history[-5:])  # 取最近5次记录的平均值
            metrics['blink_rate'] = avg_blink_rate
            
            if avg_blink_rate < 12:  # 正常眨眼频率约为每分钟12-15次
                suggestions.append("请注意适当眨眼，避免眼睛疲劳")
                
        # 记录性能指标
        log_manager.log_performance({
            'module': 'eyesight',
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
        return metrics, suggestions
        
    def take_break(self):
        """记录休息时间"""
        self.last_break_time = datetime.now()
        self.continuous_usage_time = 0
        self.logger.info("用户开始休息")
        
    def get_usage_statistics(self) -> Dict:
        """获取使用统计信息
        
        Returns:
            Dict: 包含使用时间、警告次数等统计信息
        """
        if not self.screen_time_start:
            return {}
            
        current_time = datetime.now()
        total_usage_time = (current_time - self.screen_time_start).total_seconds() / 3600
        
        # 清理超过1小时的警告记录
        cutoff_time = time.time() - 3600
        self.distance_warnings = [t for t in self.distance_warnings if t > cutoff_time]
        self.light_warnings = [t for t in self.light_warnings if t > cutoff_time]
        self.posture_warnings = [t for t in self.posture_warnings if t > cutoff_time]
                                
        return {
            'total_usage_time': round(total_usage_time, 2),  # 小时
            'continuous_usage_time': self.continuous_usage_time,  # 分钟
            'distance_warnings_last_hour': len(self.distance_warnings),
            'light_warnings_last_hour': len(self.light_warnings),
            'posture_warnings_last_hour': len(self.posture_warnings),
            'average_blink_rate': np.mean(self.blink_rate_history[-10:]) if self.blink_rate_history else None
        }
        
    def reset_statistics(self):
        """重置统计信息"""
        self.screen_time_start = datetime.now()
        self.last_break_time = datetime.now()
        self.continuous_usage_time = 0
        self.distance_warnings.clear()
        self.blink_rate_history.clear()
        self.logger.info("重置视力保护统计信息")

# 创建全局视力保护管理器实例
eyesight_protector = EyesightProtector()