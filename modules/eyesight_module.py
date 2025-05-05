"""视力保护模块 - 处理用眼健康相关的功能"""

import cv2
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
import plotly.graph_objects as go
from modules.database_module import DatabaseManager
from modules.logging_module import log_manager

class EyesightProtector:
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # 用眼距离标准（单位：厘米）
        self.distance_thresholds = {
            'too_close': 30,    # 过近
            'ideal_min': 35,    # 理想最小距离
            'ideal_max': 45,    # 理想最大距离
            'too_far': 50       # 过远
        }
        
        # 环境光照标准（单位：lux）
        self.light_thresholds = {
            'too_dark': 300,     # 过暗
            'ideal_min': 500,    # 理想最小照度
            'ideal_max': 1500,   # 理想最大照度
            'too_bright': 2000   # 过亮
        }
        
        # 眨眼频率标准（次/分钟）
        self.blink_thresholds = {
            'too_low': 12,      # 过低
            'ideal_min': 15,    # 理想最小频率
            'ideal_max': 20,    # 理想最大频率
            'too_high': 25      # 过高
        }
        
        self.screen_time_start = None
        self.last_break_time = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # 儿童用眼保护参数 - 根据最新儿童用眼卫生标准调整
        self.break_interval = 20  # 建议休息间隔（分钟）- 适用于儿童的更频繁休息
        self.break_duration = 5   # 建议休息时长（分钟）- 增加休息时间确保充分恢复
        self.min_safe_distance = 30  # 最小安全读写距离（厘米）
        self.max_safe_distance = 45  # 最大安全读写距离（厘米）
        
        # 照明标准（基于《中小学生学习用灯具》标准）
        self.min_light = 300      # 最低照度(lux)
        self.optimal_light = 500  # 最佳照度(lux)
        self.max_light = 750      # 最高照度(lux)
        
        # 儿童头部姿势限制 - 更严格的限制
        self.max_head_tilt = 15   # 最大头部倾斜角度
        self.max_head_down = 20   # 最大低头角度
        
        # 状态追踪
        self.continuous_usage_time = 0
        self.distance_warnings = []
        self.posture_warnings = []
        self.light_warnings = []
        self.blink_rate_history = []
        self.last_blink_check = time.time()
        
        # 儿童年龄相关参数
        self.age_group = {
            '6-8': {'face_width': 12.5, 'min_distance': 28},
            '9-12': {'face_width': 13.5, 'min_distance': 30},
            '13-15': {'face_width': 14.5, 'min_distance': 33}
        }
        self.current_age_group = '9-12'  # 默认年龄组
        
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
        # 获取当前年龄组的参数
        age_params = self.age_group[self.current_age_group]
        CHILD_FACE_WIDTH = age_params['face_width']  # cm
        
        # 台灯摄像头的视场角
        CAMERA_FOV = 65  # degrees
        
        # 使用移动平均来平滑距离计算
        raw_distance = (CHILD_FACE_WIDTH * frame_width) / (2 * face_width_pixels * np.tan(np.radians(CAMERA_FOV/2)))
        
        # 应用补偿因子，考虑到儿童不同阅读姿势的影响
        compensation_factor = 1.1  # 根据实际测试调整
        
        return raw_distance * compensation_factor
        
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
        
        # 检查是否需要休息 - 儿童更频繁的休息提醒
        if self.screen_time_start:
            current_time = datetime.now()
            time_since_last_break = (current_time - self.last_break_time).total_seconds() / 60
            
            if time_since_last_break >= self.break_interval:
                suggestions.append(f"小朋友已经认真学习{int(time_since_last_break)}分钟啦！来做个小游戏休息一下：\n1. 远远地看看窗外的小鸟和树叶\n2. 眨眨眼睛，像蝴蝶扇动翅膀\n3. 转转脖子，像小狮子环顾四周")
                
        # 检测阅读距离
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                distance = self.calculate_reading_distance(w, frame.shape[1])
                metrics['distance'] = distance
                
                if distance < self.min_safe_distance:
                    suggestions.append("小朋友，你离书本太近啦！\n让我们做个小游戏：\n1. 伸出小手臂，做一个'书本测量尺'\n2. 如果手够不到书本，说明距离刚刚好\n3. 保持这个距离，保护我们的小眼睛")
                elif distance > self.max_safe_distance:
                    suggestions.append("书本离得有点远呢，把书本和台灯放近一点点，找到最舒服的距离吧！")
                    
        # 检测照明情况
        light_levels = self.calculate_light_level(frame)
        metrics['light_levels'] = light_levels
        
        if light_levels['reading_area'] < self.min_light:
            suggestions.append("这里有点暗暗的，让我们：\n1. 调整一下台灯，让光线更亮一些\n2. 确保光线照到你读写的地方\n3. 现在光线暖暖的，眼睛会更舒服")
            self.light_warnings.append(time.time())
        elif light_levels['reading_area'] > self.max_light:
            suggestions.append("灯光有点太亮啦！让我们：\n1. 把台灯调暗一点点\n2. 调整台灯的位置\n3. 让光线温柔地照在书本上")
            
        # 检测眨眼频率
        blinks = self.detect_blink_rate(frame)
        if self.blink_rate_history:
            avg_blink_rate = np.mean(self.blink_rate_history[-5:])
            metrics['blink_rate'] = avg_blink_rate
            
            if avg_blink_rate < 12:
                suggestions.append("来玩个眨眨眼游戏：\n1. 数到三，一起眨眨眼\n2. 看看谁眨眼睛最可爱\n3. 眨眨眼睛，让眼睛休息一下")
                
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
        
    def set_age_group(self, age: int):
        """设置儿童年龄组
        
        Args:
            age: 儿童年龄
        """
        if age >= 6 and age <= 8:
            self.current_age_group = '6-8'
        elif age >= 9 and age <= 12:
            self.current_age_group = '9-12'
        elif age >= 13 and age <= 15:
            self.current_age_group = '13-15'
        else:
            self.current_age_group = '9-12'  # 默认年龄组
            
        # 更新相关参数
        age_params = self.age_group[self.current_age_group]
        self.min_safe_distance = age_params['min_distance']
        self.logger.info(f"更新年龄组为: {self.current_age_group}, 最小安全距离: {self.min_safe_distance}cm")

    def generate_light_radar_chart(self, start_time=None, end_time=None):
        """生成光照环境雷达图
        
        Returns:
            dict: 包含雷达图数据的字典
        """
        records = self.db_manager.get_eyesight_stats(start_time, end_time)
        if not records:
            return None
            
        # 按照时间段分组计算平均值
        morning = []    # 6:00-12:00
        afternoon = []  # 12:00-18:00
        evening = []    # 18:00-22:00
        
        for record in records:
            hour = record.timestamp.hour
            if 6 <= hour < 12:
                morning.append(record.ambient_light)
            elif 12 <= hour < 18:
                afternoon.append(record.ambient_light)
            elif 18 <= hour < 22:
                evening.append(record.ambient_light)
        
        # 计算每个时间段的平均光照强度
        avg_morning = np.mean(morning) if morning else 0
        avg_afternoon = np.mean(afternoon) if afternoon else 0
        avg_evening = np.mean(evening) if evening else 0
        
        # 创建雷达图
        categories = ['早晨 (6-12点)', '下午 (12-18点)', '晚上 (18-22点)']
        values = [avg_morning, avg_afternoon, avg_evening]
        
        fig = go.Figure()
        
        # 添加理想范围区域
        fig.add_trace(go.Scatterpolar(
            r=[self.light_thresholds['ideal_max']] * 3,
            theta=categories,
            fill='none',
            name='理想上限'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=[self.light_thresholds['ideal_min']] * 3,
            theta=categories,
            fill='tonext',
            name='理想范围'
        ))
        
        # 添加实际值
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            name='实际光照',
            line=dict(color='rgb(74, 144, 226)')
        ))
        
        # 更新布局
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max(values), self.light_thresholds['ideal_max']) * 1.2]
                )
            ),
            showlegend=True,
            title='光照环境分析'
        )
        
        return fig.to_json()
    
    def generate_usage_heatmap(self, start_time=None, end_time=None):
        """生成用眼时间热力图
        
        Returns:
            dict: 包含热力图数据的字典
        """
        records = self.db_manager.get_eyesight_stats(start_time, end_time)
        if not records:
            return None
            
        # 创建7x24的矩阵存储用眼时间（7天，每天24小时）
        usage_matrix = np.zeros((7, 24))
        
        # 遍历记录，填充矩阵
        for record in records:
            day = record.timestamp.weekday()
            hour = record.timestamp.hour
            usage_matrix[day][hour] += record.usage_duration / 3600  # 转换为小时
        
        # 创建热力图
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        hours = list(range(24))
        
        fig = go.Figure(data=go.Heatmap(
            z=usage_matrix,
            x=hours,
            y=days,
            colorscale='Blues',
            hoverongaps=False,
            hovertemplate='%{y} %{x}时: %{z:.1f}小时<extra></extra>'
        ))
        
        # 更新布局
        fig.update_layout(
            title='每周用眼时间分布',
            xaxis_title='小时',
            yaxis_title='星期',
            xaxis=dict(
                tickmode='array',
                ticktext=[f'{i}:00' for i in range(24)],
                tickvals=list(range(24))
            )
        )
        
        return fig.to_json()
    
    def analyze_eye_health(self, record):
        """分析单条用眼健康记录，生成建议
        
        Args:
            record: EyesightRecord对象
            
        Returns:
            dict: 包含分析结果和建议的字典
        """
        analysis = {
            'distance_status': 'normal',
            'light_status': 'normal',
            'blink_status': 'normal',
            'suggestions': []
        }
        
        # 分析视距
        if record.screen_distance < self.distance_thresholds['too_close']:
            analysis['distance_status'] = 'too_close'
            analysis['suggestions'].append('您离屏幕/书本太近了，请保持35-45厘米的适当距离。')
        elif record.screen_distance > self.distance_thresholds['too_far']:
            analysis['distance_status'] = 'too_far'
            analysis['suggestions'].append('您离屏幕/书本太远了，可以适当靠近一些。')
            
        # 分析光照
        if record.ambient_light < self.light_thresholds['too_dark']:
            analysis['light_status'] = 'too_dark'
            analysis['suggestions'].append('当前环境光线不足，建议适当增加照明。')
        elif record.ambient_light > self.light_thresholds['too_bright']:
            analysis['light_status'] = 'too_bright'
            analysis['suggestions'].append('当前环境光线过强，建议适当减弱照明或调整角度。')
            
        # 分析眨眼
        if record.blink_rate < self.blink_thresholds['too_low']:
            analysis['blink_status'] = 'too_low'
            analysis['suggestions'].append('您的眨眼频率过低，请记得多眨眼，避免眼睛干涩。')
        elif record.blink_rate > self.blink_thresholds['too_high']:
            analysis['blink_status'] = 'too_high'
            analysis['suggestions'].append('眨眼频率过高，可能表示眼疲劳，建议及时休息。')
            
        # 分析用眼时长
        if record.usage_duration > 40 * 60 and not record.break_taken:  # 40分钟
            analysis['suggestions'].append('您已连续用眼40分钟，建议遵循20-20-20法则：每20分钟看20英尺远处20秒。')
            
        return analysis
    
    def get_daily_report(self, date=None):
        """生成每日用眼健康报告
        
        Args:
            date: 指定日期，默认为今天
            
        Returns:
            dict: 包含报告数据的字典
        """
        if date is None:
            date = datetime.now().date()
        
        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())
        
        records = self.db_manager.get_eyesight_stats(start_time, end_time)
        if not records:
            return None
            
        report = {
            'date': date.strftime('%Y-%m-%d'),
            'total_usage': sum(r.usage_duration for r in records) / 3600,  # 总用眼时间（小时）
            'avg_distance': np.mean([r.screen_distance for r in records]),
            'avg_light': np.mean([r.ambient_light for r in records]),
            'avg_blink_rate': np.mean([r.blink_rate for r in records]),
            'warning_count': sum(r.warning_count for r in records),
            'break_count': sum(1 for r in records if r.break_taken),
            'distance_violations': len([r for r in records if r.screen_distance < self.distance_thresholds['too_close']]),
            'light_violations': len([r for r in records if r.ambient_light < self.light_thresholds['too_dark'] or 
                                   r.ambient_light > self.light_thresholds['too_bright']]),
            'suggestions': []
        }
        
        # 生成综合建议
        if report['total_usage'] > 4:
            report['suggestions'].append('今日用眼时间较长，建议适当控制使用时间。')
        if report['distance_violations'] > 5:
            report['suggestions'].append('今日多次出现不良用眼距离，请注意保持正确距离。')
        if report['light_violations'] > 5:
            report['suggestions'].append('今日光照环境多次不合适，建议调整照明条件。')
        if report['warning_count'] > 10:
            report['suggestions'].append('今日收到较多警告，建议明天多注意用眼卫生。')
        
        return report

# 创建全局视力保护管理器实例
eyesight_protector = EyesightProtector()