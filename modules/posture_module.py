"""
姿势分析模块 - 提供姿势和表情分析功能
重构版本 - 将功能分解到多个模块中以减少单个文件的代码量
"""
import os
import sys
import cv2
import time
import threading
import queue
from collections import deque
from config import DB_CONFIG

# 导入拆分后的模块
from modules.posture_core import (
    FPSCounter, process_pose_frame, POSTURE_MODULE_AVAILABLE,
    mp_pose, OCCLUSION_FRAMES_THRESHOLD, CLEAR_FRAMES_THRESHOLD
)
from modules.emotion_analyzer import (
    create_emotion_analyzer, process_emotion_frame, 
    get_emotion_params, update_emotion_params, EMOTION_MODULE_AVAILABLE
)
from modules.camera_handler import (
    init_camera, resize_frame, find_available_cameras,
    CAMERA_FPS_TARGET, RESOLUTION_LEVELS, PROCESS_WIDTH, PROCESS_HEIGHT
)
from modules.performance_monitor import (
    PerformanceMonitor, TARGET_FPS
)

# 尝试导入posture_analysis模块
try:
    # 确保能找到posture_analysis包
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(parent_dir))
    
    from posture_analysis.realtime_posture_analysis import (
        EmotionState
    )
except ImportError as e:
    print(f"导入姿势分析模块失败：{str(e)}")
    # EmotionState已在emotion_analyzer中定义，此处不需要重复定义

class WebPostureMonitor:
    """适配Web服务的姿势监测器"""
    def __init__(self, video_stream_handler=None):
        self.cap = None
        self.pose = None
        self.emotion_analyzer = None
        self.is_running = False
        self.thread = None
        self.video_stream_handler = video_stream_handler
        
        # 初始化性能监控器
        self.performance_monitor = PerformanceMonitor(RESOLUTION_LEVELS)
        
        # 初始化处理分辨率
        self.process_width, self.process_height = self.performance_monitor.get_current_resolution()
        
        # 初始化帧率计数器
        self.capture_fps = FPSCounter()  # 摄像头捕获帧率
        self.pose_process_fps = FPSCounter()  # 姿势处理帧率
        self.emotion_process_fps = FPSCounter()  # 情绪处理帧率
        
        # 存储最新分析结果
        self.pose_result = {
            'angle': 0,
            'is_bad_posture': False,
            'is_occluded': False,
            'status': 'Initialized'
        }
        self.emotion_result = {
            'emotion': 'NEUTRAL',
            'emotion_code': 0
        }
        
        # 帧率信息
        self.fps_info = {
            'capture_fps': 0,
            'pose_process_fps': 0,
            'emotion_process_fps': 0
        }
        
        # 初始化遮挡计数器
        self.occlusion_counter = 0
        self.clear_counter = 0
        self.last_valid_angle = None
        
        # 采样策略
        self.resize_method = 'subsampling'  # 'resize' 或 'subsampling'
    
    def start(self):
        """启动姿势分析线程"""
        if self.is_running:
            print("分析系统已经在运行中")
            return True
            
        self.is_running = True
        self.cap, success = init_camera()
        
        if not success or not self.cap or not self.cap.isOpened():
            self.is_running = False
            print("无法初始化摄像头，姿势分析系统启动失败")
            return False
            
        if POSTURE_MODULE_AVAILABLE:
            try:
                print("正在初始化姿势分析和情绪分析组件...")
                
                # 使用正确的MediaPipe姿势检测
                self.pose = mp_pose.Pose(
                    static_image_mode=False,    # 视频流模式
                    model_complexity=1,         # 模型复杂度（0-2）降低以提高性能
                    smooth_landmarks=True,      # 启用关键点平滑
                    min_detection_confidence=0.6, # 降低到0.6以提高检测率
                    min_tracking_confidence=0.5
                )
                
                # 创建情绪分析器实例
                self.emotion_analyzer = create_emotion_analyzer()
                
                # 重置计数器和性能统计
                self.capture_fps.reset()
                self.pose_process_fps.reset()
                self.emotion_process_fps.reset()
                
                # 启动处理线程
                self.thread = threading.Thread(target=self._process_frames)
                self.thread.daemon = True
                self.thread.start()
                
                print("姿势分析系统启动成功")
                return True
            except Exception as e:
                self.is_running = False
                print(f"启动姿势分析系统失败，错误详情: {e}")
                import traceback
                traceback.print_exc()  # 打印详细错误堆栈
                return False
        else:
            self.is_running = False
            print("姿势分析模块不可用，请检查posture_analysis包是否正确安装")
            return False
    
    def stop(self):
        """停止姿势分析线程"""
        self.is_running = False
        
        if self.thread:
            try:
                self.thread.join(timeout=2.0)
            except Exception:
                pass
            self.thread = None
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        print("姿势分析系统已停止")
        return True
    
    def _process_frames(self):
        """处理视频帧的主循环"""
        if not POSTURE_MODULE_AVAILABLE:
            return
        
        last_fps_update_time = time.time()
        consecutive_read_failures = 0
        last_frame_time = time.time()
        
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                current_time = time.time()
                
                # 如果摄像头出现多次错误，尝试重新连接摄像头
                if self.performance_monitor.should_reconnect(consecutive_read_failures):
                    print(f"连续 {consecutive_read_failures} 次读取失败，尝试重新初始化摄像头...")
                    self.cap.release()
                    self.cap, success = init_camera()
                    if not success:
                        print("重新初始化摄像头失败，暂停1秒后重试")
                        time.sleep(1)
                        continue
                    consecutive_read_failures = 0
                
                # 读取摄像头帧
                ret, frame = self.cap.read()
                if not ret:
                    consecutive_read_failures += 1
                    self.performance_monitor.record_camera_error()
                    print("无法读取摄像头帧")
                    time.sleep(0.01)
                    continue
                
                # 重置错误计数器
                consecutive_read_failures = 0
                
                # 更新捕获帧率
                self.capture_fps.update()
                
                # 计算帧间隔
                frame_interval = current_time - last_frame_time
                last_frame_time = current_time
                
                # 检查是否需要跳过这一帧以提高性能
                if self.performance_monitor.should_skip_frame(CAMERA_FPS_TARGET):
                    # 跳过这一帧，但仍提供最后处理的结果给视频流
                    continue
                
                # 根据当前性能动态调整处理分辨率
                if self.performance_monitor.adjust_resolution(
                    self.pose_process_fps.get_fps(), 
                    self.emotion_process_fps.get_fps()
                ):
                    # 分辨率变更，更新当前值
                    self.process_width, self.process_height = self.performance_monitor.get_current_resolution()
                    # 重置帧率计数器
                    self.pose_process_fps.reset()
                    self.emotion_process_fps.reset()
                
                # 记录处理开始时间
                process_start_time = time.time()
                
                # 调整帧尺寸进行处理
                processed_frame = resize_frame(
                    frame, 
                    self.process_width, 
                    self.process_height, 
                    method=self.resize_method
                )
                
                pose_frame = processed_frame.copy()
                emotion_frame = processed_frame.copy()
                
                # 处理姿势
                pose_results = process_pose_frame(
                    pose_frame, 
                    self.pose, 
                    self.occlusion_counter, 
                    self.clear_counter, 
                    self.last_valid_angle
                )
                
                # 更新计数器
                self.occlusion_counter = pose_results['occlusion_counter']
                self.clear_counter = pose_results['clear_counter']
                self.last_valid_angle = pose_results['last_valid_angle']
                
                self.pose_process_fps.update()  # 更新姿势处理帧率
                
                # 处理情绪
                emotion_results = process_emotion_frame(emotion_frame, self.emotion_analyzer)
                self.emotion_process_fps.update()  # 更新情绪处理帧率
                
                # 记录处理时间
                process_time = time.time() - process_start_time
                self.performance_monitor.record_processing_time(process_time)
                
                # 添加处理时间和分辨率信息到显示帧
                size_text = f"{self.process_width}x{self.process_height}"
                cv2.putText(pose_results['display_frame'], 
                          f"Proc: {process_time*1000:.1f}ms {size_text}", 
                          (pose_results['display_frame'].shape[1] - 200, 25), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                # 将处理后的帧放入队列供Web端点使用
                if self.video_stream_handler:
                    self.video_stream_handler.add_pose_frame(pose_results['display_frame'])
                    self.video_stream_handler.add_emotion_frame(emotion_results['display_frame'])
                
                # 更新结果状态
                self.pose_result = {
                    'angle': pose_results['angle'] if pose_results['angle'] is not None else 0,
                    'is_bad_posture': pose_results['is_bad_posture'],
                    'is_occluded': pose_results['is_occluded'],
                    'status': pose_results['status']
                }
                
                self.emotion_result = {
                    'emotion': emotion_results['emotion'].name if emotion_results['emotion'] else 'UNKNOWN',
                    'emotion_code': emotion_results['emotion'].value if emotion_results['emotion'] else -1
                }
                
                # 每0.5秒更新一次帧率信息
                if current_time - last_fps_update_time >= 0.5:
                    perf_stats = self.performance_monitor.get_performance_stats()
                    self.fps_info = {
                        'capture_fps': round(self.capture_fps.get_fps(), 1),
                        'pose_process_fps': round(self.pose_process_fps.get_fps(), 1),
                        'emotion_process_fps': round(self.emotion_process_fps.get_fps(), 1),
                        'process_resolution': perf_stats['current_resolution'],
                        'avg_process_time_ms': perf_stats['avg_processing_time_ms']
                    }
                    last_fps_update_time = current_time
                
                # 根据实际帧率动态调整延迟时间
                current_fps = min(self.pose_process_fps.get_fps(), self.emotion_process_fps.get_fps())
                target_interval = 1.0 / TARGET_FPS
                
                # 如果处理太快，增加一点延迟以减少CPU使用
                if process_time < target_interval * 0.8:
                    time.sleep(min(0.001, (target_interval - process_time) * 0.5))
            except Exception as e:
                print(f"处理帧异常: {str(e)}")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)
    
    def get_emotion_params(self):
        """获取当前情绪分析参数"""
        return get_emotion_params()
    
    def update_emotion_params(self, params):
        """更新情绪分析参数"""
        return update_emotion_params(params)
    
    def get_fps_info(self):
        """获取帧率信息"""
        # 添加更多性能统计信息
        perf_stats = self.performance_monitor.get_performance_stats()
        extended_info = {
            **self.fps_info,
            'skipped_frames': perf_stats['skipped_frames'],
            'camera_errors': perf_stats['camera_errors'],
            'adaptive_resolution': perf_stats['adaptive_mode'],
            'skip_frames_enabled': perf_stats['skip_frames_enabled']
        }
        return extended_info
    
    def set_resolution_mode(self, adaptive=True, resolution_index=None):
        """设置分辨率模式"""
        return self.performance_monitor.set_resolution_mode(adaptive, resolution_index)
    
    def set_performance_mode(self, skip_frames=None, use_separate_grab=None):
        """设置性能优化模式"""
        return self.performance_monitor.set_performance_mode(skip_frames)

# 添加PostureModule作为WebPostureMonitor的别名以兼容现有代码
PostureModule = WebPostureMonitor