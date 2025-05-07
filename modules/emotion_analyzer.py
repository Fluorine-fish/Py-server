"""
情绪分析器模块 - 提供情绪识别和分析功能
从原始posture_module.py拆分而来，减少单个文件代码量
"""
import os
import sys
import cv2

# 尝试导入posture_analysis模块
try:
    # 确保能找到posture_analysis包
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(parent_dir))
    
    from posture_analysis.realtime_posture_analysis import (
        EmotionAnalyzer, EmotionState, mp_face_mesh,
        mp_drawing, mp_drawing_styles,
        EMOTION_SMOOTHING_WINDOW, MOUTH_OPEN_RATIO_THRESHOLD,
        EYE_OPEN_RATIO_THRESHOLD, BROW_DOWN_THRESHOLD
    )
    EMOTION_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"导入情绪分析模块失败：{str(e)}")
    EMOTION_MODULE_AVAILABLE = False
    
    # 定义占位符常量和类，避免程序崩溃
    class EmotionState:
        NEUTRAL = 0
        HAPPY = 1
        ANGRY = 3
        SAD = 4
    
    EMOTION_SMOOTHING_WINDOW = 7
    MOUTH_OPEN_RATIO_THRESHOLD = 0.45
    EYE_OPEN_RATIO_THRESHOLD = 0.25
    BROW_DOWN_THRESHOLD = 0.04

# 全局参数设置
emotion_params = {
    'emotion_smoothing_window': EMOTION_SMOOTHING_WINDOW,
    'mouth_open_ratio_threshold': MOUTH_OPEN_RATIO_THRESHOLD,
    'eye_open_ratio_threshold': EYE_OPEN_RATIO_THRESHOLD,
    'brow_down_threshold': BROW_DOWN_THRESHOLD
}

def process_emotion_frame(frame, emotion_analyzer):
    """
    处理情绪分析
    
    Args:
        frame: 输入图像帧
        emotion_analyzer: 情绪分析器实例
    
    Returns:
        results: 包含情绪分析结果的字典
    """
    if not EMOTION_MODULE_AVAILABLE:
        return {
            'display_frame': frame,
            'emotion': None,
            'face_landmarks': None
        }
    
    results = {
        'display_frame': frame,
        'emotion': None,
        'face_landmarks': None
    }
    
    try:
        # 更新情绪分析器的所有参数
        emotion_analyzer.emotion_smoothing_window = emotion_params['emotion_smoothing_window']
        emotion_analyzer.mouth_open_ratio_threshold = emotion_params['mouth_open_ratio_threshold']
        emotion_analyzer.eye_open_ratio_threshold = emotion_params['eye_open_ratio_threshold']
        emotion_analyzer.brow_down_threshold = emotion_params['brow_down_threshold']
        
        # 分析情绪
        emotion_state, face_landmarks, _ = emotion_analyzer.analyze(frame)
        
        # 绘制情绪界面
        display_frame = frame.copy()
        if face_landmarks:
            # 绘制面部关键点
            mp_drawing.draw_landmarks(
                image=display_frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            
            # 显示当前情绪状态
            emotion_text = f"Emotion: {emotion_state.name}"
            cv2.putText(display_frame, emotion_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 250), 2)
        
        results = {
            'display_frame': display_frame,
            'emotion': emotion_state,
            'face_landmarks': face_landmarks
        }
        
        return results
    except Exception as e:
        print(f"情绪处理异常: {str(e)}")
        return results

def create_emotion_analyzer():
    """
    创建情绪分析器实例
    
    Returns:
        emotion_analyzer: EmotionAnalyzer实例或None
    """
    if not EMOTION_MODULE_AVAILABLE:
        return None
    
    try:
        return EmotionAnalyzer()
    except Exception as e:
        print(f"创建情绪分析器失败: {str(e)}")
        return None

def get_emotion_params():
    """
    获取当前情绪分析参数
    
    Returns:
        params: 情绪分析参数字典
    """
    return {
        'emotion_smoothing_window': emotion_params['emotion_smoothing_window'],
        'mouth_open_ratio_threshold': emotion_params['mouth_open_ratio_threshold'],
        'eye_open_ratio_threshold': emotion_params['eye_open_ratio_threshold'],
        'brow_down_threshold': emotion_params['brow_down_threshold']
    }

def update_emotion_params(params):
    """
    更新情绪分析参数
    
    Args:
        params: 包含要更新参数的字典
    
    Returns:
        success: 更新是否成功
    """
    global emotion_params
    try:
        if 'emotion_smoothing_window' in params:
            value = int(params['emotion_smoothing_window'])
            if 1 <= value <= 30:
                emotion_params['emotion_smoothing_window'] = value
        
        if 'mouth_open_ratio_threshold' in params:
            value = float(params['mouth_open_ratio_threshold'])
            if 0.1 <= value <= 1.0:
                emotion_params['mouth_open_ratio_threshold'] = value
        
        if 'eye_open_ratio_threshold' in params:
            value = float(params['eye_open_ratio_threshold'])
            if 0.05 <= value <= 0.5:
                emotion_params['eye_open_ratio_threshold'] = value
        
        if 'brow_down_threshold' in params:
            value = float(params['brow_down_threshold'])
            if 0.01 <= value <= 0.2:
                emotion_params['brow_down_threshold'] = value
        
        return True
    except Exception as e:
        print(f"更新情绪参数失败: {str(e)}")
        return False