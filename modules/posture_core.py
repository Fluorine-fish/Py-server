"""
姿势分析核心模块 - 提供姿势分析的核心功能
从原始posture_module.py拆分而来，减少单个文件代码量
"""
import os
import sys
import cv2
import time
from collections import deque

# 尝试导入posture_analysis模块
try:
    # 确保能找到posture_analysis包
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(parent_dir))
    
    from posture_analysis.realtime_posture_analysis import (
        PostureMonitor, mp_pose, mp_drawing, mp_drawing_styles,
        check_occlusion, calculate_head_angle, 
        VISIBILITY_THRESHOLD, HEAD_ANGLE_THRESHOLD,
        OCCLUSION_FRAMES_THRESHOLD, CLEAR_FRAMES_THRESHOLD
    )
    POSTURE_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"导入姿势分析模块失败：{str(e)}")
    POSTURE_MODULE_AVAILABLE = False
    
    # 定义占位符常量
    OCCLUSION_FRAMES_THRESHOLD = 10
    CLEAR_FRAMES_THRESHOLD = 5
    HEAD_ANGLE_THRESHOLD = 45

# 帧率计算类
class FPSCounter:
    """计算并跟踪帧率"""
    def __init__(self, window_size=10):  # 减小窗口大小为10以获得更实时的帧率
        """
        Args:
            window_size: 计算平均帧率的时间窗口大小（帧数）
        """
        self.window_size = window_size
        self.timestamps = deque(maxlen=window_size)
        self.last_fps = 0
        self.total_frames = 0
    
    def update(self):
        """记录一帧的时间戳并更新帧率"""
        self.timestamps.append(time.time())
        self.total_frames += 1
        
        # 至少需要2个时间戳才能计算帧率
        if len(self.timestamps) >= 2:
            # 计算时间差（秒）
            time_diff = self.timestamps[-1] - self.timestamps[0]
            if time_diff > 0:
                # 修正帧率计算公式: 在窗口内完成的帧数除以时间差
                self.last_fps = len(self.timestamps) / time_diff
            else:
                self.last_fps = 0
        
        return self.last_fps
    
    def get_fps(self):
        """获取当前帧率"""
        return self.last_fps
    
    def get_total_frames(self):
        """获取总帧数"""
        return self.total_frames
    
    def reset(self):
        """重置帧率计数器"""
        self.timestamps.clear()
        self.last_fps = 0
        # 不重置total_frames，这样可以保留总计数

def process_pose_frame(frame, pose_processor, occlusion_counter, clear_counter, last_valid_angle):
    """
    处理姿势检测
    
    Args:
        frame: 输入图像帧
        pose_processor: MediaPipe姿势检测器
        occlusion_counter: 遮挡计数器
        clear_counter: 清晰计数器
        last_valid_angle: 最后有效的角度
        
    Returns:
        results: 包含姿势检测结果的字典
    """
    if not POSTURE_MODULE_AVAILABLE:
        return {
            'display_frame': frame,
            'angle': None,
            'is_bad_posture': False,
            'is_occluded': True,
            'status': 'Module Not Available',
            'occlusion_counter': occlusion_counter,
            'clear_counter': clear_counter,
            'last_valid_angle': last_valid_angle
        }
    
    results = {
        'display_frame': frame,
        'angle': None,
        'is_bad_posture': False,
        'is_occluded': True,
        'status': 'No Detection',
        'occlusion_counter': occlusion_counter,
        'clear_counter': clear_counter,
        'last_valid_angle': last_valid_angle
    }
    
    try:
        # 姿势检测
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose_processor.process(frame_rgb)
        if not pose_results.pose_landmarks:
            return results
        
        # 遮挡检测
        is_occluded, occlusion_status = check_occlusion(pose_results.pose_landmarks.landmark)
        
        # 更新计数器
        if is_occluded:
            occlusion_counter = min(occlusion_counter + 1, OCCLUSION_FRAMES_THRESHOLD)
            clear_counter = max(0, clear_counter - 1)
        else:
            clear_counter = min(clear_counter + 1, CLEAR_FRAMES_THRESHOLD)
            occlusion_counter = max(0, occlusion_counter - 1)
        
        final_occlusion = occlusion_counter >= OCCLUSION_FRAMES_THRESHOLD
        valid_detection = clear_counter >= CLEAR_FRAMES_THRESHOLD
        
        # 头部角度计算
        angle_info = calculate_head_angle(pose_results.pose_landmarks.landmark, frame.shape)
        angle = None
        is_bad_posture = False
        points = {}
        
        if angle_info[0] is not None:
            angle, is_bad_posture, points = angle_info
            last_valid_angle = angle
        
        # 绘制姿势关键点和信息
        display_frame = frame.copy()
        
        # 绘制姿势关键点
        mp_drawing.draw_landmarks(
            display_frame,
            pose_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        # 绘制状态信息
        state_text = f"State: {'Occluded' if final_occlusion else 'Tracking'}"
        color = (0, 0, 255) if final_occlusion else (0, 255, 0)
        cv2.putText(display_frame, state_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # 绘制角度信息
        if angle is not None and valid_detection and not final_occlusion:
            status_color = (0, 0, 255) if is_bad_posture else (0, 255, 0)
            text = f"Angle: {angle:.1f}° {'[BAD]' if is_bad_posture else '[GOOD]'}"
            cv2.putText(display_frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            if points:
                cv2.line(display_frame, tuple(points['mid_shoulder']), tuple(points['nose']), (0, 255, 0), 2)
        elif final_occlusion and last_valid_angle:
            text = f"Occluded | Last: {last_valid_angle:.1f}°"
            cv2.putText(display_frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 更新结果
        results = {
            'display_frame': display_frame,
            'angle': angle if angle is not None else (last_valid_angle if final_occlusion else None),
            'is_bad_posture': is_bad_posture,
            'is_occluded': final_occlusion,
            'status': occlusion_status if final_occlusion else 'Tracking',
            'occlusion_counter': occlusion_counter,
            'clear_counter': clear_counter,
            'last_valid_angle': last_valid_angle
        }
        
        return results
    except Exception as e:
        print(f"姿势处理异常: {str(e)}")
        return results