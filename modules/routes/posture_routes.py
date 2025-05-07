"""
姿势监测相关路由模块
处理所有与姿势检测、视频流和监测状态相关的路由
"""

from flask import Blueprint, Response, request, jsonify
from . import routes_bp
from modules.posture_module import WebPostureMonitor, POSTURE_MODULE_AVAILABLE
from modules.video_stream_module import VideoStreamHandler

# 获取姿势监测实例
posture_monitor = WebPostureMonitor()
video_stream_handler = VideoStreamHandler()

# 全局应用状态
app_status = {
    'emotion_analysis_running': False,
    'last_error': '',
    'api_version': "1.1.0"
}

@routes_bp.route('/api/status')
def api_status():
    """获取API状态"""
    try:
        # 更新状态信息
        app_status['emotion_analysis_running'] = posture_monitor.is_running
        
        # 获取处理器状态
        is_posture_module_available = POSTURE_MODULE_AVAILABLE
        
        # 获取摄像头状态
        camera_status = {
            'initialized': posture_monitor.cap is not None and posture_monitor.cap.isOpened() if posture_monitor else False
        }
        
        return jsonify({
            'status': 'success',
            'app_status': app_status,
            'posture_module_available': is_posture_module_available,
            'camera_status': camera_status
        })
    except Exception as e:
        print(f"获取API状态出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取API状态失败: {str(e)}"
        })

@routes_bp.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """启动姿势监测"""
    try:
        if posture_monitor.is_running:
            return jsonify({
                'status': 'success',
                'message': '姿势监测已经在运行'
            })
        
        success = posture_monitor.start()
        if success:
            app_status['emotion_analysis_running'] = True
            return jsonify({
                'status': 'success',
                'message': '成功启动姿势监测'
            })
        else:
            app_status['last_error'] = '无法启动姿势监测'
            return jsonify({
                'status': 'error',
                'message': '无法启动姿势监测'
            })
    except Exception as e:
        print(f"启动姿势监测出错: {str(e)}")
        app_status['last_error'] = str(e)
        return jsonify({
            'status': 'error',
            'message': f"启动姿势监测失败: {str(e)}"
        })

@routes_bp.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """停止姿势监测"""
    try:
        if not posture_monitor.is_running:
            return jsonify({
                'status': 'success',
                'message': '姿势监测已经停止'
            })
        
        success = posture_monitor.stop()
        app_status['emotion_analysis_running'] = False
        
        return jsonify({
            'status': 'success',
            'message': '成功停止姿势监测'
        })
    except Exception as e:
        print(f"停止姿势监测出错: {str(e)}")
        app_status['last_error'] = str(e)
        return jsonify({
            'status': 'error',
            'message': f"停止姿势监测失败: {str(e)}"
        })

@routes_bp.route('/pose_video_feed')
def pose_video_feed():
    """提供姿势分析视频流"""
    try:
        print("请求姿势分析视频流")
        return Response(
            video_stream_handler.generate_pose_video_stream(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print(f"生成姿势分析视频流出错: {str(e)}")
        return "视频流生成失败", 500

@routes_bp.route('/emotion_video_feed')
def emotion_video_feed():
    """提供情绪分析视频流"""
    try:
        print("请求情绪分析视频流")
        return Response(
            video_stream_handler.generate_emotion_video_stream(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print(f"生成情绪分析视频流出错: {str(e)}")
        return "视频流生成失败", 500

@routes_bp.route('/api/get_pose_result')
def get_pose_result():
    """获取姿势分析结果"""
    try:
        if not posture_monitor.is_running:
            return jsonify({
                'status': 'error',
                'message': '姿势监测未启动'
            })
        
        result = posture_monitor.pose_result
        return jsonify({
            'status': 'success',
            'pose_result': result
        })
    except Exception as e:
        print(f"获取姿势分析结果出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取姿势分析结果失败: {str(e)}"
        })

@routes_bp.route('/api/get_emotion_result')
def get_emotion_result():
    """获取情绪分析结果"""
    try:
        if not posture_monitor.is_running:
            return jsonify({
                'status': 'error',
                'message': '姿势监测未启动'
            })
        
        result = posture_monitor.emotion_result
        return jsonify({
            'status': 'success',
            'emotion_result': result
        })
    except Exception as e:
        print(f"获取情绪分析结果出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取情绪分析结果失败: {str(e)}"
        })

@routes_bp.route('/api/get_emotion_params')
def get_emotion_params():
    """获取情绪分析参数"""
    try:
        params = posture_monitor.get_emotion_params()
        return jsonify({
            'status': 'success',
            'emotion_params': params
        })
    except Exception as e:
        print(f"获取情绪分析参数出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取情绪分析参数失败: {str(e)}"
        })

@routes_bp.route('/api/update_emotion_params', methods=['POST'])
def update_emotion_params():
    """更新情绪分析参数"""
    try:
        data = request.get_json()
        success = posture_monitor.update_emotion_params(data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '情绪分析参数已更新',
                'updated_params': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '更新情绪分析参数失败'
            })
    except Exception as e:
        print(f"更新情绪分析参数出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"更新情绪分析参数失败: {str(e)}"
        })