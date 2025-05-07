"""
系统相关路由模块
处理所有与系统性能、帧率优化和调整相关的路由
"""

from flask import Blueprint, request, jsonify, Response
from . import routes_bp
from modules.posture_module import WebPostureMonitor
from modules.video_stream_module import VideoStreamHandler

# 获取需要的实例
posture_monitor = WebPostureMonitor()
video_stream_handler = VideoStreamHandler()

@routes_bp.route('/api/get_fps_info')
def get_fps_info():
    """获取各种帧率信息"""
    try:
        # 获取姿势监测模块的帧率信息
        posture_fps_info = posture_monitor.get_fps_info()
        
        # 获取视频流模块的帧率信息
        stream_fps_info = video_stream_handler.get_fps_info()
        
        # 合并所有帧率信息
        fps_info = {
            **posture_fps_info,
            **stream_fps_info
        }
        
        return jsonify({
            'status': 'success',
            'fps_info': fps_info
        })
    except Exception as e:
        print(f"获取帧率信息出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取帧率信息失败: {str(e)}"
        })

@routes_bp.route('/api/set_resolution_mode', methods=['POST'])
def set_resolution_mode():
    """设置分辨率调整模式"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的请求数据'
            })
            
        # 解析参数
        adaptive = data.get('adaptive', True)
        resolution_index = data.get('resolution_index')
        target = data.get('target', 'both')  # 'processing', 'streaming', 'both'
        
        if target in ['processing', 'both']:
            # 设置处理分辨率模式
            posture_monitor.set_resolution_mode(adaptive, resolution_index)
            
        if target in ['streaming', 'both']:
            # 设置流分辨率模式
            video_stream_handler.set_resolution_mode(adaptive, resolution_index)
            
        return jsonify({
            'status': 'success',
            'message': '分辨率模式已更新',
            'adaptive': adaptive,
            'resolution_index': resolution_index if resolution_index is not None else 'auto',
            'target': target
        })
    except Exception as e:
        print(f"设置分辨率模式出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"设置分辨率模式失败: {str(e)}"
        })

@routes_bp.route('/api/set_quality_mode', methods=['POST'])
def set_quality_mode():
    """设置质量调整模式"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的请求数据'
            })
            
        # 解析参数
        adaptive = data.get('adaptive', True)
        quality = data.get('quality')
        
        # 设置质量模式
        video_stream_handler.set_quality_mode(adaptive)
        
        # 如果指定了固定质量
        if quality is not None:
            quality = int(quality)
            video_stream_handler.set_streaming_quality(quality)
            
        return jsonify({
            'status': 'success',
            'message': '质量模式已更新',
            'adaptive': adaptive,
            'quality': quality
        })
    except Exception as e:
        print(f"设置质量模式出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"设置质量模式失败: {str(e)}"
        })

@routes_bp.route('/api/set_performance_mode', methods=['POST'])
def set_performance_mode():
    """设置性能优化模式"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的请求数据'
            })
            
        # 解析参数
        skip_frames = data.get('skip_frames')
        use_separate_grab = data.get('use_separate_grab')
        
        # 设置性能模式
        posture_monitor.set_performance_mode(skip_frames, use_separate_grab)
            
        return jsonify({
            'status': 'success',
            'message': '性能模式已更新',
            'skip_frames': skip_frames,
            'use_separate_grab': use_separate_grab
        })
    except Exception as e:
        print(f"设置性能模式出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"设置性能模式失败: {str(e)}"
        })

@routes_bp.route('/api/get_performance_stats')
def get_performance_stats():
    """获取性能统计信息"""
    try:
        # 获取姿势监测模块的性能统计
        posture_stats = posture_monitor.get_performance_stats()
        
        # 获取视频流模块的性能统计
        stream_stats = video_stream_handler.get_performance_stats()
        
        # 合并所有统计信息
        stats = {
            'posture': posture_stats,
            'stream': stream_stats
        }
        
        return jsonify({
            'status': 'success',
            'performance_stats': stats
        })
    except Exception as e:
        print(f"获取性能统计出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取性能统计失败: {str(e)}"
        })

# 帧事件流端点
@routes_bp.route('/api/frame_events')
def frame_events():
    """获取帧事件流"""
    try:
        # 返回帧事件流
        return Response(
            video_stream_handler.generate_frame_events(),
            mimetype='text/event-stream'
        )
    except Exception as e:
        print(f"生成帧事件流出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"生成帧事件流失败: {str(e)}"
        })