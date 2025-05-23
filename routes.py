"""
路由模块 - 处理所有Web路由和API请求
"""
from flask import Blueprint, render_template, Response, request, jsonify
import cv2
import json
import time
import os
import re
from datetime import datetime
import numpy as np
from config import DEBUG, DB_CONFIG
from db_handler import DBHandler
from modules.video_stream_module import VideoStreamHandler
from modules.posture_module import WebPostureMonitor, POSTURE_MODULE_AVAILABLE
from serial_handler import SerialHandler

# 创建数据库处理器
db = DBHandler(DB_CONFIG)

# 创建Flask蓝图
routes = Blueprint('routes', __name__)

# 创建视频流处理器
video_stream_handler = VideoStreamHandler()

# 创建姿势监测器
posture_monitor = WebPostureMonitor(video_stream_handler=video_stream_handler)

# 创建串口通信处理器
serial_handler = SerialHandler(monitoring_interval=5)
print("串口通信处理器初始化完成")

# API版本
API_VERSION = "1.1.0"

# 应用状态
app_status = {
    'emotion_analysis_running': False,
    'last_error': '',
    'api_version': API_VERSION
}

# 最后事件时间戳
last_event_time = time.time()

@routes.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@routes.route('/api/status')
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

@routes.route('/api/start_monitoring', methods=['POST'])
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

@routes.route('/api/stop_monitoring', methods=['POST'])
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

@routes.route('/pose_video_feed')
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

@routes.route('/emotion_video_feed')
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

@routes.route('/api/get_pose_result')
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

@routes.route('/api/get_emotion_result')
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

@routes.route('/api/get_emotion_params')
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

@routes.route('/api/update_emotion_params', methods=['POST'])
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

# 帧率优化API

@routes.route('/api/get_fps_info')
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

@routes.route('/api/set_resolution_mode', methods=['POST'])
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

@routes.route('/api/set_quality_mode', methods=['POST'])
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

@routes.route('/api/set_performance_mode', methods=['POST'])
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

@routes.route('/api/get_performance_stats')
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

# Serial API路由

@routes.route('/api/get_serial_status')
def get_serial_status():
    """获取串口连接状态"""
    try:
        connected = serial_handler.is_connected()
        port = serial_handler.port if connected else None
        baudrate = serial_handler.baudrate if connected else None
        
        return jsonify({
            'status': 'success',
            'connected': connected,
            'port': port,
            'baudrate': baudrate
        })
    except Exception as e:
        print(f"获取串口状态出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取串口状态失败: {str(e)}",
            'connected': False
        })

@routes.route('/api/connect_serial', methods=['POST'])
def connect_serial():
    """连接指定的串口"""
    try:
        data = request.get_json()
        port = data.get('port')
        baudrate = data.get('baudrate', 115200)
        
        if not port:
            return jsonify({
                'status': 'error',
                'message': '必须指定串口设备'
            })
        
        # 先断开现有连接
        serial_handler.close()
        
        # 设置新的串口参数
        serial_handler.port = port
        serial_handler.baudrate = baudrate
        
        # 尝试连接
        connection_success = serial_handler.connect()
        
        if connection_success:
            return jsonify({
                'status': 'success',
                'message': f'成功连接到串口: {port}, 波特率: {baudrate}',
                'port': port,
                'baudrate': baudrate
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'无法连接到串口: {port}'
            })
    except Exception as e:
        print(f"连接串口出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"连接串口失败: {str(e)}"
        })

@routes.route('/api/disconnect_serial', methods=['POST'])
def disconnect_serial():
    """断开串口连接"""
    try:
        was_connected = serial_handler.is_connected()
        serial_handler.close()
        
        return jsonify({
            'status': 'success',
            'message': '已断开串口连接' if was_connected else '串口已处于断开状态'
        })
    except Exception as e:
        print(f"断开串口出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"断开串口失败: {str(e)}"
        })

@routes.route('/api/send_serial_command', methods=['POST'])
def send_serial_command():
    """向串口发送命令"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            return jsonify({
                'status': 'error',
                'message': '命令不能为空'
            })
        
        if not serial_handler.is_connected():
            return jsonify({
                'status': 'error',
                'message': '串口未连接，请先连接串口'
            })
        
        # 发送命令
        success = serial_handler.send_data(command + '\r\n')
        
        # 给点时间让设备处理并响应
        time.sleep(0.1)
        
        # 尝试读取响应
        response = serial_handler.read_data()
        
        # 记录命令和响应到数据库
        try:
            db.record_serial_data(
                sent_data=command,
                received_data=response,
                status="success" if success else "error",
                message="" if success else "发送失败"
            )
        except Exception as db_error:
            print(f"记录串口数据到数据库失败: {str(db_error)}")
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '命令已发送',
                'command': command,
                'response': response
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '发送命令失败',
                'command': command
            })
    except Exception as e:
        print(f"发送串口命令出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"发送串口命令失败: {str(e)}"
        })

@routes.route('/api/send_frame', methods=['POST'])
def send_frame():
    """向串口发送帧数据"""
    try:
        data = request.get_json()
        yaw = data.get('yaw', 0.0)
        pitch = data.get('pitch', 0.0)
        find_bool = data.get('find_bool', False)
        
        if not serial_handler.is_connected():
            return jsonify({
                'status': 'error',
                'message': '串口未连接，请先连接串口'
            })
        
        # 发送帧数据
        success = serial_handler.send_yaw_pitch(find_bool, yaw, pitch)
        
        # 给点时间让设备处理并响应
        time.sleep(0.1)
        
        # 记录到数据库
        try:
            sent_data = f"yaw={yaw}, pitch={pitch}, find={find_bool}"
            db.record_serial_data(
                sent_data=sent_data,
                received_data="",
                status="success" if success else "error",
                message="" if success else "发送失败"
            )
        except Exception as db_error:
            print(f"记录帧数据到数据库失败: {str(db_error)}")
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '帧数据已发送',
                'response': f"发送了帧数据: yaw={yaw}, pitch={pitch}, find={find_bool}"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '发送帧数据失败'
            })
    except Exception as e:
        print(f"发送帧数据出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"发送帧数据失败: {str(e)}"
        })

@routes.route('/api/read_frame')
def read_frame():
    """读取一帧数据"""
    try:
        if not serial_handler.is_connected():
            return jsonify({
                'status': 'error',
                'message': '串口未连接，请先连接串口'
            })
        
        # 读取帧数据
        frame_data = serial_handler.read_frame()
        
        if frame_data:
            return jsonify({
                'status': 'success',
                'frame_data': frame_data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '没有接收到有效帧数据'
            })
    except Exception as e:
        print(f"读取帧数据出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"读取帧数据失败: {str(e)}"
        })

@routes.route('/api/get_history')
def get_history():
    """获取串口通信历史记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 从数据库获取历史记录
        total_records, records = db.get_serial_history(page, per_page)
        
        # 计算总页数
        total_pages = (total_records + per_page - 1) // per_page
        
        return jsonify({
            'status': 'success',
            'current_page': page,
            'per_page': per_page,
            'total_records': total_records,
            'total_pages': total_pages,
            'records': records
        })
    except Exception as e:
        print(f"获取历史记录出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取历史记录失败: {str(e)}"
        })

@routes.route('/api/clear_history', methods=['POST'])
def clear_history():
    """清空串口通信历史记录"""
    try:
        # 调用数据库清空历史记录
        db.clear_serial_history()
        
        return jsonify({
            'status': 'success',
            'message': '历史记录已清空'
        })
    except Exception as e:
        print(f"清空历史记录出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"清空历史记录失败: {str(e)}"
        })

# 帧事件流端点
@routes.route('/api/frame_events')
def frame_events():
    def generate():
        """生成事件流"""
        # 初始化事件ID
        event_id = 0
        
        # 启动帧监控
        frame_queue = []
        
        # 初始化最后一次发送心跳包的时间
        last_heartbeat_time = time.time()
        
        # 开始事件循环
        while True:
            # 每15秒发送一次心跳包，保持连接活跃
            current_time = time.time()
            if current_time - last_heartbeat_time > 15:
                heartbeat_data = json.dumps({
                    'type': 'heartbeat',
                    'timestamp': current_time
                })
                yield f"id: {event_id}\ndata: {heartbeat_data}\n\n"
                event_id += 1
                last_heartbeat_time = current_time
            
            # 如果串口已连接，尝试读取一帧数据
            if serial_handler.is_connected():
                frame_data = serial_handler.read_frame()
                if frame_data:
                    # 构造事件数据
                    data = json.dumps(frame_data)
                    yield f"id: {event_id}\ndata: {data}\n\n"
                    event_id += 1
            
            # 短暂休眠，避免过度占用CPU
            time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')

@routes.route('/api/send_data', methods=['POST'])
def send_data():
    """处理通用数据发送请求"""
    try:
        data = request.get_json()
        send_text = data.get('data', '')
        
        if not send_text:
            return jsonify({
                'status': 'error',
                'message': '发送的数据不能为空'
            })
        
        if not serial_handler.is_connected():
            return jsonify({
                'status': 'error',
                'message': '串口未连接，请先连接串口'
            })
        
        # 发送数据
        success = serial_handler.send_data(send_text)
        
        # 给设备一点时间处理
        time.sleep(0.1)
        
        # 尝试读取响应
        response = serial_handler.read_data()
        
        # 记录到数据库
        try:
            db.record_serial_data(
                sent_data=send_text,
                received_data=response,
                status="success" if success else "error",
                message="" if success else "发送失败"
            )
        except Exception as db_error:
            print(f"记录数据到数据库失败: {str(db_error)}")
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '数据已发送',
                'response': response or "无响应"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '发送数据失败'
            })
    except Exception as e:
        print(f"发送数据出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"发送数据失败: {str(e)}"
        })