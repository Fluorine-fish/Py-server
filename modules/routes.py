"""
路由模块 - 处理所有API路由请求
"""
from flask import Blueprint, render_template, jsonify, request, Response, stream_with_context
import json
import queue
import time
import traceback
import importlib.util
import numpy as np
import cv2
from modules.database_module import save_record_to_db, get_history_records, clear_history, clear_all_posture_records
from modules.posture_module import WebPostureMonitor, posture_params
from config import DEBUG_BUTTON_VISIBLE  # 从config导入调试按钮显示配置

# 尝试导入虚拟检测服务模块
try:
    from modules.mock_detection import MockDetectionService
    MOCK_DETECTION_AVAILABLE = True
except ImportError:
    print("警告：虚拟检测服务模块不可用")
    MOCK_DETECTION_AVAILABLE = False

# 创建蓝图
routes_bp = Blueprint('routes', __name__)

# 全局变量
posture_monitor = None
video_stream_handler = None
serial_handler = None
detection_service = None
chatbot_service = None

# 设置依赖服务
def setup_services(posture_monitor_instance=None, video_stream_instance=None, 
                  serial_handler_instance=None, detection_service_instance=None,
                  chatbot_service_instance=None):
    """设置各个服务模块实例"""
    global posture_monitor, video_stream_handler, serial_handler, detection_service, chatbot_service
    posture_monitor = posture_monitor_instance
    video_stream_handler = video_stream_instance
    serial_handler = serial_handler_instance
    detection_service = detection_service_instance
    chatbot_service = chatbot_service_instance

# 页面路由
@routes_bp.route('/')
def index():
    return render_template('main.html', debug_button_visible=DEBUG_BUTTON_VISIBLE)

# 目标检测页面路由
@routes_bp.route('/detection')
def detection_page():
    """渲染目标检测控制页面"""
    print("\n==== 访问目标检测页面 ====")
    # 打印检测服务状态
    if detection_service:
        print(f"检测服务状态: {'运行中' if detection_service.is_running() else '未运行'}")
        if detection_service.is_running():
            pos = detection_service.get_position()
            if pos['detected']:
                print(f"当前检测位置: ({pos['x']:.3f}, {pos['y']:.3f}), 置信度: {pos['confidence']:.2f}")
            else:
                print("当前未检测到目标")
    else:
        print("检测服务未初始化")
    return render_template('detection.html')

# 目标检测相关API

@routes_bp.route('/api/detection/status', methods=['GET'])
def get_detection_status():
    """获取目标检测服务状态"""
    if not detection_service:
        return jsonify({
            'status': 'error',
            'message': '目标检测服务未初始化',
            'running': False
        })
    
    return jsonify({
        'status': 'success',
        'running': detection_service.is_running()
    })

@routes_bp.route('/api/detection/position', methods=['GET'])
def get_detection_position():
    """获取当前检测到的目标位置"""
    global detection_service
    
    # 如果检测服务不存在或未运行，返回默认的空结果
    if not detection_service:
        # 如果检测服务不存在，尝试导入并创建虚拟检测服务
        try:
            from modules.mock_detection import MockDetectionService
            detection_service = MockDetectionService()
            detection_service.initialize()
            detection_service.start()
            print("已自动启动虚拟检测服务")
        except Exception as e:
            print(f"无法创建虚拟检测服务: {e}")
            return jsonify({
                'status': 'error',
                'message': '目标检测服务未初始化且无法创建虚拟服务'
            })
    
    if not detection_service.is_running():
        try:
            detection_service.start()
            print("检测服务已自动启动")
        except Exception as e:
            print(f"启动检测服务失败: {e}")
            return jsonify({
                'status': 'error',
                'message': '目标检测服务未启动且无法自动启动'
            })
    
    position_data = detection_service.get_position()
    
    # 每次获取位置时打印检测状态
    if position_data['detected']:
        print(f"API请求位置: 检测到目标 - ({position_data['x']:.3f}, {position_data['y']:.3f}), 置信度: {position_data['confidence']:.2f}, FPS: {position_data['fps']:.1f}")
    else:
        print(f"API请求位置: 未检测到目标, FPS: {position_data['fps']:.1f}")
        
    return jsonify({
        'status': 'success',
        'position': position_data
    })

@routes_bp.route('/api/detection/auto_send/start', methods=['POST'])
def start_detection_auto_send():
    """启动检测坐标自动发送"""
    if not detection_service:
        return jsonify({
            'status': 'error',
            'message': '检测服务未初始化'
        })
    
    if not serial_handler or not serial_handler.is_connected():
        return jsonify({
            'status': 'error',
            'message': '串口未连接'
        })
    
    if not detection_service.is_running():
        return jsonify({
            'status': 'error',
            'message': '检测服务未运行'
        })
    
    # 获取传入的间隔参数
    data = request.json or {}
    interval = data.get('interval', 0.05)  # 默认50ms
    
    # 启动自动发送
    success = detection_service.start_auto_send(interval=interval)
    if success:
        return jsonify({
            'status': 'success',
            'message': f'已启动坐标自动发送 (间隔: {interval*1000:.0f}ms)',
            'interval': interval
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '启动坐标自动发送失败'
        })

@routes_bp.route('/api/detection/auto_send/stop', methods=['POST'])
def stop_detection_auto_send():
    """停止检测坐标自动发送"""
    if not detection_service:
        return jsonify({
            'status': 'error',
            'message': '检测服务未初始化'
        })
    
    # 停止自动发送
    success = detection_service.stop_auto_send()
    if success:
        return jsonify({
            'status': 'success',
            'message': '已停止坐标自动发送'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '停止坐标自动发送失败'
        })

@routes_bp.route('/api/detection/auto_send/status', methods=['GET'])
def get_detection_auto_send_status():
    """获取检测坐标自动发送状态"""
    if not detection_service:
        return jsonify({
            'status': 'error',
            'message': '检测服务未初始化',
            'auto_send': False
        })
    
    is_auto_sending = detection_service.is_auto_sending()
    
    return jsonify({
        'status': 'success',
        'auto_send': is_auto_sending,
    })

# 路由：调试页面

# 路由：调试页面
@routes_bp.route('/debug')
def debug():
    return render_template('debug.html')

# 路由：发送文本数据
@routes_bp.route('/api/send_data', methods=['POST'])
def send_data():
    data = request.json.get('data')
    response = "未连接"
    status = "error"
    message = "串口未连接"
    
    if not serial_handler or not serial_handler.is_connected():
        message = "串口未连接"
    else:
        # 尝试发送数据到串口
        response, message = serial_handler.send_data(data)
        if response:
            status = "success"
    
    # 无论成功失败都保存到数据库
    save_record_to_db(data, response, status, message)
    
    return jsonify({
        'status': status,
        'message': message,
        'response': response
    })

# 路由：获取历史记录
@routes_bp.route('/api/get_history')
def get_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = get_history_records(page, per_page)
    return jsonify(result)

# 路由：清空历史记录
@routes_bp.route('/api/clear_history', methods=['POST'])
def clear_history_route():
    if clear_history():
        return jsonify({'status': 'success', 'message': '历史记录已清空'})
    else:
        return jsonify({'status': 'error', 'message': '清空历史记录失败'})

# 路由：发送帧数据
@routes_bp.route('/api/send_frame', methods=['POST'])
def send_frame():
    """发送按照帧格式打包的yaw和pitch数据"""
    try:
        # 获取请求参数
        data = request.json
        find_bool = data.get('find_bool', False)
        yaw = data.get('yaw', 0.0)
        pitch = data.get('pitch', 0.0)
        
        response_data = "未连接"
        status = "error"
        message = "串口未连接"
        
        if not serial_handler or not serial_handler.is_connected():
            message = "串口未连接"
        else:
            # 发送帧格式数据
            response_frame, message = serial_handler.send_frame(find_bool, yaw, pitch)
            if response_frame:
                response_data = str(response_frame)
                status = "success"
            elif "成功" in message:
                response_data = "无响应"
                status = "success"
        
        # 保存到数据库
        sent_info = f"yaw:{yaw}, pitch:{pitch}, find_bool:{find_bool}"
        save_record_to_db(sent_info, response_data, status, message)
        
        return jsonify({
            'status': status,
            'message': message,
            'response': response_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"处理请求时出错: {str(e)}",
            'response': '发送失败'
        })

# 路由：读取帧数据
@routes_bp.route('/api/read_frame', methods=['GET'])
def read_frame_api():
    """读取一帧数据并解析"""
    try:
        status = "error"
        message = "串口未连接"
        frame_data = None
        
        if not serial_handler or not serial_handler.is_connected():
            message = "串口未连接"
        else:
            # 读取帧数据
            frame_data, message = serial_handler.read_frame()
            if frame_data:
                status = "success"
        
        return jsonify({
            'status': status,
            'message': message,
            'frame_data': frame_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"读取帧数据时出错: {str(e)}",
            'frame_data': None
        })

# 路由：SSE帧数据事件流
@routes_bp.route('/api/frame_events')
def frame_events():
    """SSE端点，向前端推送接收到的帧数据"""
    def event_stream():
        if not serial_handler:
            # 如果串口未初始化，发送空闲状态信息而不是立即退出
            yield f"data: {json.dumps({'status': 'idle', 'message': '串口未初始化', 'type': 'status'})}\n\n"
            # 每30秒发送一次心跳保持连接
            while True:
                try:
                    time.sleep(30)
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                except Exception:
                    break
            return
            
        frame_queue = serial_handler.get_frame_queue()
        
        while True:
            try:
                # 从队列获取最新数据，最多等待30秒
                frame_data = frame_queue.get(timeout=30)
                # 发送事件
                yield f"data: {json.dumps(frame_data)}\n\n"
            except queue.Empty:
                # 超时时发送心跳保持连接
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            except Exception as e:
                print(f"发送事件流时出错: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

# 路由：启动姿势分析
@routes_bp.route('/api/start_posture_analysis', methods=['POST'])
def start_posture_analysis():
    """启动姿势分析系统"""
    global posture_monitor
    
    try:
        if not posture_monitor:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未初始化'
            })
            
        if posture_monitor.is_running:
            return jsonify({
                'status': 'success',
                'message': '姿势分析系统已经在运行中'
            })
        
        success = posture_monitor.start()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '姿势分析系统启动成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '启动姿势分析系统失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
                'message': f'启动姿势分析系统出错: {str(e)}'
        })

# 路由：停止姿势分析
@routes_bp.route('/api/stop_posture_analysis', methods=['POST'])
def stop_posture_analysis():
    """停止姿势分析系统"""
    global posture_monitor
    
    try:
        if not posture_monitor or not posture_monitor.is_running:
            return jsonify({
                'status': 'success',
                'message': '姿势分析系统未运行'
            })
        
        success = posture_monitor.stop()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '姿势分析系统已停止'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '停止姿势分析系统失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'停止姿势分析系统出错: {str(e)}'
        })

# 路由：获取姿势状态
@routes_bp.route('/api/get_pose_status')
def get_pose_status():
    """获取当前姿势分析状态"""
    global posture_monitor, video_stream_handler
    
    try:
        print("DEBUG: 请求获取姿势分析状态")
        
        # 检查是否有视频流但姿势分析未初始化的情况
        if not posture_monitor:
            print("WARNING: 姿势分析系统对象未初始化，但前端请求了状态")
            # 检查视频流处理器是否在工作
            if video_stream_handler:
                # 视频流正常但姿势分析未初始化，尝试修正状态
                print("INFO: 视频流处理器存在但姿势分析未初始化")
                return jsonify({
                    'status': 'partial',  # 新状态：部分可用
                    'message': '视频流可用但姿势分析未正确初始化',
                    'is_running': False,
                    'pose_data': {'status': 'Video Only', 'angle': 0, 'is_bad_posture': False, 'is_occluded': True},
                    'emotion_data': {'emotion': 'UNKNOWN', 'emotion_code': -1}
                })
            else:
                print("ERROR: 姿势分析系统和视频流均未初始化")
                return jsonify({
                    'status': 'error',
                    'message': '姿势分析系统未初始化',
                    'is_running': False,
                    'pose_data': None,
                    'emotion_data': None
                })
        
        # 正常情况下返回完整状态信息
        print(f"DEBUG: 姿势分析系统状态 - 运行中: {posture_monitor.is_running}")
        return jsonify({
            'status': 'success',
            'message': '获取姿势分析状态成功',
            'is_running': posture_monitor.is_running,
            'pose_data': posture_monitor.pose_result,
            'emotion_data': posture_monitor.emotion_result
        })
    except Exception as e:
        print(f"ERROR: 获取姿势分析状态出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'获取姿势分析状态出错: {str(e)}',
            'is_running': False,
            'pose_data': None,
            'emotion_data': None
        })

# 路由：获取帧率信息
@routes_bp.route('/api/get_fps_info')
def get_fps_info():
    """获取所有帧率信息（包括捕获帧率、处理帧率和视频流帧率）"""
    global posture_monitor, video_stream_handler
    
    try:
        # 初始化返回数据
        fps_data = {
            'status': 'success',
            'capture_fps': 0,  # 图像接收帧率
            'pose_process_fps': 0,  # 姿势处理帧率
            'emotion_process_fps': 0,  # 情绪处理帧率
            'pose_stream_fps': 0,  # 姿势视频流帧率
            'emotion_stream_fps': 0  # 情绪视频流帧率
        }
        
        # 获取姿势分析模块的帧率数据
        if posture_monitor  and posture_monitor.is_running:
            posture_fps_info = posture_monitor.get_fps_info()
            fps_data.update({
                'capture_fps': posture_fps_info.get('capture_fps', 0),
                'pose_process_fps': posture_fps_info.get('pose_process_fps', 0),
                'emotion_process_fps': posture_fps_info.get('emotion_process_fps', 0)
            })
        
        # 获取视频流模块的帧率数据
        if video_stream_handler:
            stream_fps_info = video_stream_handler.get_fps_info()
            fps_data.update({
                'pose_stream_fps': stream_fps_info.get('pose_stream_fps', 0),
                'emotion_stream_fps': stream_fps_info.get('emotion_stream_fps', 0)
            })
        
        return jsonify(fps_data)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取帧率信息出错: {str(e)}',
            'capture_fps': 0,
            'pose_process_fps': 0,
            'emotion_process_fps': 0,
            'pose_stream_fps': 0,
            'emotion_stream_fps': 0
        })

# 路由：获取情绪参数
@routes_bp.route('/api/get_emotion_params')
def get_emotion_params():
    """获取情绪分析参数"""
    global posture_monitor, posture_params
    
    try:
        return jsonify({
            'status': 'success',
            'params': posture_params
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取情绪分析参数出错: {str(e)}'
        })

# 路由：更新情绪参数
@routes_bp.route('/api/update_emotion_params', methods=['POST'])
def update_emotion_params():
    """更新情绪分析参数"""
    global posture_monitor
    
    try:
        if not posture_monitor:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未初始化'
            })
            
        params = request.json
        
        # 验证并更新参数
        success = posture_monitor.update_emotion_params(params)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '情绪分析参数更新成功',
                'params': posture_monitor.get_emotion_params()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '更新情绪分析参数失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'更新情绪分析参数出错: {str(e)}'
        })

# 路由：姿势检测视频流
@routes_bp.route('/api/video_pose')
def video_pose():
    """姿势检测视频流端点"""
    print("DEBUG: 请求姿势检测视频流")
    
    if not video_stream_handler:
        print("ERROR: 视频流处理器未初始化")
        # 返回空的响应
        return Response("视频流处理器未初始化", status=500)
    
    print("DEBUG: 开始生成姿势视频流响应")
    return Response(
        video_stream_handler.generate_video_frames(video_stream_handler.get_pose_frame_queue(), is_pose_stream=True),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# 路由：情绪分析视频流
@routes_bp.route('/api/video_emotion')
def video_emotion():
    """情绪分析视频流端点"""
    print("DEBUG: 请求情绪分析视频流")
    
    if not video_stream_handler:
        print("ERROR: 视频流处理器未初始化")
        # 返回空的响应
        return Response("视频流处理器未初始化", status=500)
    
    print("DEBUG: 开始生成情绪视频流响应")
    return Response(
        video_stream_handler.generate_video_frames(video_stream_handler.get_emotion_frame_queue(), is_pose_stream=False),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# 路由：获取串口状态
@routes_bp.route('/api/get_serial_status')
def get_serial_status():
    """获取串口连接状态"""
    global serial_handler
    
    try:
        if not serial_handler:
            return jsonify({
                'status': 'error',
                'message': '串口处理器未初始化',
                'connected': False
            })
            
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
            'message': f'获取串口状态失败: {str(e)}',
            'connected': False
        })

# 路由：连接串口
@routes_bp.route('/api/connect_serial', methods=['POST'])
def connect_serial():
    """连接指定的串口"""
    global serial_handler
    
    try:
        if not serial_handler:
            return jsonify({
                'status': 'error',
                'message': '串口处理器未初始化',
                'connected': False
            })
            
        data = request.json
        port = data.get('port')
        baudrate = data.get('baudrate', 115200)
        
        if not port:
            return jsonify({
                'status': 'error',
                'message': '必须指定串口设备路径'
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
            'message': f'连接串口失败: {str(e)}'
        })

# 视频流路由别名 - 兼容前端
@routes_bp.route('/pose_video_feed')
def pose_video_feed_alias():
    """姿势分析视频流别名"""
    print("DEBUG: 通过别名请求姿势分析视频流")
    
    if not video_stream_handler:
        print("ERROR: 视频流处理器未初始化")
        return Response("视频流处理器未初始化", status=500)
    
    return Response(
        video_stream_handler.generate_video_frames(video_stream_handler.get_pose_frame_queue(), is_pose_stream=True),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@routes_bp.route('/emotion_video_feed')
def emotion_video_feed_alias():
    """情绪分析视频流别名"""
    print("DEBUG: 通过别名请求情绪分析视频流")
    
    if not video_stream_handler:
        print("ERROR: 视频流处理器未初始化")
        return Response("视频流处理器未初始化", status=500)
    
    return Response(
        video_stream_handler.generate_video_frames(video_stream_handler.get_emotion_frame_queue(), is_pose_stream=False),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# 添加串口指令发送路由
@routes_bp.route('/api/send_serial_command', methods=['POST'])
def send_serial_command():
    """向串口发送命令"""
    global serial_handler
    
    try:
        data = request.json
        command = data.get('command')
        
        if not command:
            return jsonify({
                'status': 'error',
                'message': '命令不能为空'
            })
        
        if not serial_handler or not serial_handler.is_connected():
            return jsonify({
                'status': 'error',
                'message': '串口未连接，请先连接串口'
            })
        
        # 发送命令
        response_data, message = serial_handler.send_data(command + '\r\n')
        
        # 记录命令和响应到数据库
        status = "success" if response_data else "error"
        save_record_to_db(command, response_data, status, message)
        
        return jsonify({
            'status': status,
            'message': message or '命令已发送',
            'command': command,
            'response': response_data or "无响应"
        })
    except Exception as e:
        print(f"发送串口命令出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'发送串口命令失败: {str(e)}'
        })

# 设置分辨率模式
@routes_bp.route('/api/set_resolution_mode', methods=['POST'])
def set_resolution_mode():
    """设置分辨率调整模式"""
    global posture_monitor, video_stream_handler
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的请求数据'
            })
            
        # 解析参数
        adaptive = data.get('adaptive', True)
        resolution_index = data.get('resolution_index')
        target = data.get('target', 'both')  # 'processing', 'streaming', 'both'
        quality = data.get('quality', 90)
        
        # 更新处理分辨率
        if posture_monitor and target in ['processing', 'both']:
            posture_monitor.set_resolution_mode(adaptive, resolution_index)
            
        # 更新流分辨率
        if video_stream_handler and target in ['streaming', 'both']:
            video_stream_handler.set_resolution_mode(adaptive, resolution_index)
            # 如果指定了质量参数，也设置流质量
            if quality is not None:
                video_stream_handler.set_streaming_quality(int(quality))
                
        return jsonify({
            'status': 'success',
            'message': '分辨率模式已更新',
            'adaptive': adaptive,
            'resolution_index': resolution_index if resolution_index is not None else 'auto',
            'target': target,
            'quality': quality
        })
    except Exception as e:
        print(f"设置分辨率模式出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'设置分辨率模式失败: {str(e)}'
        })

# 兼容路由 - 支持旧版前端
@routes_bp.route('/get_pose_status')
def get_pose_status_compat():
    """获取姿势状态的兼容路由（无API前缀）"""
    return get_pose_status()

# 路由：获取坐姿图像记录设置
@routes_bp.route('/api/get_posture_recording_settings')
def get_posture_recording_settings():
    """获取坐姿图像记录设置"""
    global posture_monitor
    
    try:
        if not posture_monitor:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未初始化',
                'settings': None
            })
        
        settings = posture_monitor.get_posture_recording_settings()
        
        return jsonify({
            'status': 'success',
            'message': '获取坐姿图像记录设置成功',
            'settings': settings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取坐姿图像记录设置失败: {str(e)}',
            'settings': None
        })

@routes_bp.route('/api/check_posture_time_recording', methods=['GET'])
def check_posture_time_recording():
    """检查坐姿时间记录设置"""
    if posture_monitor:
        settings = posture_monitor.get_posture_time_recording_settings()
        return jsonify({
            'status': 'success',
            'settings': settings
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '姿势监测器未初始化'
        })

# 路由：更新坐姿图像记录设置
@routes_bp.route('/api/update_posture_recording_settings', methods=['POST'])
def update_posture_recording_settings():
    """更新坐姿图像记录设置"""
    global posture_monitor
    
    try:
        if not posture_monitor:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未初始化'
            })
        
        # 获取请求参数
        data = request.json
        enabled = data.get('enabled')
        duration_threshold = data.get('duration_threshold')
        interval = data.get('interval')
        
        # 新增良好坐姿记录参数
        good_posture_enabled = data.get('good_posture_enabled')
        good_posture_angle_threshold = data.get('good_posture_angle_threshold')
        good_posture_duration_threshold = data.get('good_posture_duration_threshold')
        good_posture_interval = data.get('good_posture_interval')
        
        if (enabled is None and duration_threshold is None and interval is None and
            good_posture_enabled is None and good_posture_angle_threshold is None and
            good_posture_duration_threshold is None and good_posture_interval is None):
            return jsonify({
                'status': 'error',
                'message': '未提供任何更新参数'
            })
        
        # 更新设置
        settings = posture_monitor.set_posture_recording(
            enabled=enabled,
            duration_threshold=duration_threshold,
            interval=interval,
            good_posture_enabled=good_posture_enabled,
            good_posture_angle_threshold=good_posture_angle_threshold,
            good_posture_duration_threshold=good_posture_duration_threshold,
            good_posture_interval=good_posture_interval
        )
        
        return jsonify({
            'status': 'success',
            'message': '坐姿图像记录设置已更新',
            'settings': settings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'更新坐姿图像记录设置失败: {str(e)}'
        })

# 路由：获取坐姿图像记录列表
@routes_bp.route('/api/get_posture_images')
def get_posture_images():
    """获取坐姿图像记录列表，支持分页和按日期及时间段筛选"""
    try:
        from modules.database_module import get_posture_images as db_get_posture_images
        
        # 获取请求参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        bad_posture_only = request.args.get('bad_posture_only', 'false').lower() == 'true'
        date = request.args.get('date', None)  # 日期格式：YYYY-MM-DD
        hour = request.args.get('hour', None, type=int)  # 小时：0-23
        
        # 查询数据库
        result = db_get_posture_images(page, per_page, bad_posture_only, date, hour)
        
        return jsonify({
            'status': 'success',
            'message': '获取坐姿图像记录成功',
            **result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取坐姿图像记录失败: {str(e)}',
            'records': [],
            'pagination': {
                'total': 0,
                'page': 1,
                'per_page': 10,
                'total_pages': 0
            }
        })

# 路由：删除坐姿图像记录
@routes_bp.route('/api/delete_posture_image', methods=['POST'])
def delete_posture_image():
    """删除指定的坐姿图像记录"""
    try:
        from modules.database_module import delete_posture_image as db_delete_posture_image
        
        # 获取请求参数
        data = request.json
        image_id = data.get('image_id')
        
        if not image_id:
            return jsonify({
                'status': 'error',
                'message': '未提供图像ID'
            })
        
        # 执行删除
        success = db_delete_posture_image(image_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'已删除坐姿图像记录 (ID: {image_id})'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'未找到ID为 {image_id} 的坐姿图像记录'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'删除坐姿图像记录失败: {str(e)}'
        })

# 路由：清空坐姿图像记录
@routes_bp.route('/api/clear_posture_images', methods=['POST'])
def clear_posture_images():
    """清空坐姿图像记录"""
    try:
        from modules.database_module import clear_posture_images as db_clear_posture_images
        
        # 获取请求参数
        data = request.json
        days_to_keep = data.get('days_to_keep')
        
        # 执行清空
        deleted_count = db_clear_posture_images(days_to_keep)
        
        message = f'已删除 {deleted_count} 条坐姿图像记录'
        if days_to_keep:
            message = f'已删除 {deleted_count} 条{days_to_keep}天前的坐姿图像记录'
            
        return jsonify({
            'status': 'success',
            'message': message,
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'清空坐姿图像记录失败: {str(e)}'
        })

# 路由：手动记录当前坐姿图像
@routes_bp.route('/api/capture_posture_image', methods=['POST'])
def capture_posture_image():
    """手动记录当前坐姿图像"""
    global posture_monitor
    
    try:
        if not posture_monitor or not posture_monitor.is_running:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未运行'
            })
        
        from modules.database_module import save_posture_image
        
        # 获取请求参数
        data = request.json
        notes = data.get('notes', '手动记录的坐姿图像')
        
        # 获取当前帧
        if not hasattr(posture_monitor, 'cap') or not posture_monitor.cap.isOpened():
            return jsonify({
                'status': 'error',
                'message': '摄像头未就绪'
            })
            
        # 读取当前帧
        ret, frame = posture_monitor.cap.read()
        if not ret:
            return jsonify({
                'status': 'error',
                'message': '无法获取当前摄像头帧'
            })
        
        # 获取当前姿势状态
        angle = posture_monitor.pose_result.get('angle', 0)
        is_bad_posture = posture_monitor.pose_result.get('is_bad_posture', False)
        posture_status = f"{'Bad' if is_bad_posture else 'Good'} Posture - Angle: {angle:.1f}°"
        emotion = posture_monitor.emotion_result.get('emotion', 'UNKNOWN')
        
        # 保存图像记录
        result = save_posture_image(
            image=frame,
            angle=angle,
            is_bad_posture=is_bad_posture,
            posture_status=posture_status,
            emotion=emotion,
            notes=notes
        )
        
        if result:
            return jsonify({
                'status': 'success',
                'message': '成功记录当前坐姿图像',
                'image': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '保存坐姿图像失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'记录坐姿图像失败: {str(e)}'
        })

# 路由：查看更多坐姿图像记录页面
@routes_bp.route('/posture-records')
def posture_records_page():
    """显示坐姿图像记录详情页面"""
    return render_template('posture_records.html')

# 路由：获取坐姿统计数据
@routes_bp.route('/api/get_posture_stats')
def get_posture_stats():
    """获取坐姿统计数据
    
    支持的参数:
    - time_range: 预设时间范围 'day', 'week', 'month', 'custom'
    - start_date: 自定义开始日期 (格式: YYYY-MM-DD，仅当time_range为'custom'时有效)
    - end_date: 自定义结束日期 (格式: YYYY-MM-DD，仅当time_range为'custom'时有效)
    - with_hourly_data: 是否返回每小时数据，'true'或'false'，默认为'false'
    """
    global posture_monitor
    
    try:
        # 获取时间范围参数
        time_range = request.args.get('time_range', 'day')
        if time_range not in ['day', 'week', 'month', 'custom']:
            time_range = 'day'
        
        # 处理自定义日期范围
        custom_start_date = None
        custom_end_date = None
        
        if time_range == 'custom':
            try:
                from datetime import datetime
                # 解析自定义日期参数
                start_date_str = request.args.get('start_date')
                end_date_str = request.args.get('end_date')
                
                if start_date_str and end_date_str:
                    custom_start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    custom_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    # 设置start_date的时间为00:00:00
                    custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    # 设置end_date的时间为23:59:59
                    custom_end_date = custom_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                else:
                    # 如果未提供有效的自定义日期，则使用"今天"作为默认值
                    time_range = 'day'
            except ValueError:
                # 日期格式无效，回退到"今天"
                time_range = 'day'
        
        # 是否需要返回每小时数据
        with_hourly_data = request.args.get('with_hourly_data', 'false').lower() == 'true'
        
        # 检查姿势监测器是否已初始化
        if not posture_monitor:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未初始化',
                'posture_stats': {
                    'good': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                    'mild': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                    'moderate': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                    'severe': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                    'total_time': {'seconds': 0, 'formatted_time': '0h 0m'},
                    'good_posture_percentage': 0,
                    'time_range': time_range
                }
            })
        
        # 直接从模块导入函数
        from modules.database_module import get_posture_stats as db_get_posture_stats
        
        # 获取姿势统计数据
        stats = db_get_posture_stats(
            time_range=time_range, 
            custom_start_date=custom_start_date, 
            custom_end_date=custom_end_date,
            with_hourly_data=with_hourly_data
        )
        
        # 添加查询区间的文字描述
        time_range_description = ""
        if time_range == 'day':
            time_range_description = "今日数据"
        elif time_range == 'week':
            time_range_description = "本周数据"
        elif time_range == 'month':
            time_range_description = "本月数据"
        elif time_range == 'custom':
            from datetime import datetime
            time_range_description = f"{custom_start_date.strftime('%Y-%m-%d')}至{custom_end_date.strftime('%Y-%m-%d')}数据"
        
        stats['time_range_description'] = time_range_description
        
        return jsonify({
            'status': 'success',
            'posture_stats': stats
        })
    except Exception as e:
        print(f"获取坐姿统计数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f"获取坐姿统计数据失败: {str(e)}",
            'posture_stats': {
                'good': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                'mild': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                'moderate': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                'severe': {'seconds': 0, 'percentage': 0, 'formatted_time': '0h 0m'},
                'total_time': {'seconds': 0, 'formatted_time': '0h 0m'},
                'good_posture_percentage': 0,
                'time_range': time_range
            }
        })

# 路由：设置坐姿类型阈值
@routes_bp.route('/api/set_posture_thresholds', methods=['POST'])
def set_posture_thresholds():
    """设置坐姿类型阈值"""
    global posture_monitor
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的请求数据'
            })
            
        # 解析参数
        enabled = data.get('enabled', True)
        thresholds = data.get('thresholds', {})
        
        if not posture_monitor:
            return jsonify({
                'status': 'error',
                'message': '姿势分析系统未初始化'
            })
        
        # 将前端传来的阈值键名转换为后端使用的键名
        backend_thresholds = {}
        if 'good' in thresholds:
            backend_thresholds['good'] = thresholds['good']
        if 'mild' in thresholds:
            backend_thresholds['mild'] = thresholds['mild']
        if 'moderate' in thresholds:
            backend_thresholds['moderate'] = thresholds['moderate']
        
        # 更新坐姿时间记录设置
        settings = posture_monitor.set_posture_time_recording(enabled, backend_thresholds)
        
        return jsonify({
            'status': 'success',
            'message': '坐姿阈值设置已更新',
            'settings': settings
        })
    except Exception as e:
        print(f"设置坐姿阈值出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"设置坐姿阈值失败: {str(e)}"
        })

# 路由：导出所有坐姿历史记录
@routes_bp.route('/api/export_all_posture_records')
def export_all_posture_records():
    """导出所有坐姿历史记录，包括统计数据、图像记录和时间记录"""
    try:
        from modules.database_module import export_all_posture_records as db_export_records
        
        # 获取时间范围参数
        time_range = request.args.get('time_range', 'all')
        if time_range not in ['all', 'day', 'week', 'month', 'custom']:
            time_range = 'all'
        
        # 处理自定义日期范围
        custom_start_date = None
        custom_end_date = None
        
        if time_range == 'custom':
            try:
                from datetime import datetime
                # 解析自定义日期参数
                start_date_str = request.args.get('start_date')
                end_date_str = request.args.get('end_date')
                
                if start_date_str  and end_date_str:
                    custom_start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    custom_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    # 设置start_date的时间为00:00:00
                    custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    # 设置end_date的时间为23:59:59
                    custom_end_date = custom_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                else:
                    # 如果未提供有效的自定义日期，则使用"全部"作为默认值
                    time_range = 'all'
            except ValueError:
                # 日期格式无效，回退到"全部"
                time_range = 'all'
        
        # 获取所有坐姿记录
        records = db_export_records(
            time_range=time_range,
            start_date=custom_start_date,
            end_date=custom_end_date
        )
        
        # 添加查询区间的文字描述
        time_range_description = ""
        if time_range == 'day':
            time_range_description = "今日数据"
        elif time_range == 'week':
            time_range_description = "本周数据"
        elif time_range == 'month':
            time_range_description = "本月数据"
        elif time_range == 'custom'  and custom_start_date  and custom_end_date:
            time_range_description = f"{custom_start_date.strftime('%Y-%m-%d')}至{custom_end_date.strftime('%Y-%m-%d')}数据"
        else:
            time_range_description = "所有历史数据"
        
        records['time_range_description'] = time_range_description
        
        return jsonify({
            'status': 'success',
            'message': f'成功导出{time_range_description}，共{records["image_records"]["count"]}条图像记录  and {records["time_records"]["count"]}条时间记录',
            'records': records
        })
    except Exception as e:
        print(f"导出所有坐姿历史记录出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'导出坐姿历史记录失败: {str(e)}'
        })

# 路由：清空所有坐姿记录
@routes_bp.route('/api/clear_all_posture_records', methods=['POST'])
def clear_all_posture_records_route():
    """清空所有坐姿记录，包括图像记录和时间记录"""
    try:
        print("正在执行清空所有坐姿记录...")
        result = clear_all_posture_records()
        print(f"清空结果: {result}")
        
        if result and result.get('status') == 'success':
            return jsonify({
                'status': 'success', 
                'message': result.get('message', '所有坐姿记录已清空')
            })
        else:
            error_msg = result.get('message', '清空坐姿记录失败') if result else '清空坐姿记录失败'
            print(f"清空失败: {error_msg}")
            return jsonify({
                'status': 'error', 
                'message': error_msg
            })
    except Exception as e:
        print(f"执行清空所有坐姿记录时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'清空坐姿记录时发生错误: {str(e)}'
        })

@routes_bp.route('/api/posture/history/all', methods=['GET'])
def get_all_posture_history():
    """获取所有坐姿历史记录，包括图像记录和时间记录"""
    try:
        # 从查询参数中获取时间范围
        time_range = request.args.get('range', 'all')
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # 获取所有历史记录
        result = get_all_posture_records(time_range, start_date, end_date)
        
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'获取坐姿历史记录失败: {str(e)}'
        }), 500

@routes_bp.route('/api/posture/history/clear', methods=['POST'])
def clear_posture_history():
    """清空坐姿历史记录"""
    try:
        # 获取请求参数
        data = request.get_json()
        days_to_keep = data.get('days_to_keep', None)
        
        if days_to_keep is not None:
            try:
                days_to_keep = int(days_to_keep)
            except ValueError:
                days_to_keep = None
        
        # 执行清空操作
        result = clear_all_posture_records(days_to_keep)
        
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'清空坐姿历史记录失败: {str(e)}'
        }), 500

@routes_bp.route('/posture/history', methods=['GET'])
def view_posture_history():
    """渲染坐姿历史记录页面"""
    return render_template('posture_history.html', title='坐姿历史记录')

@routes_bp.route('/api/debug/posture_records')
def debug_posture_records():
    """诊断接口：获取所有坐姿时间记录的原始数据（仅用于调试）"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取最近100条记录
        query = """
            SELECT 
                id, start_time, end_time, duration_seconds, 
                angle, posture_type, notes
            FROM posture_time_records
            ORDER BY start_time DESC
            LIMIT 100
        """
        
        cursor.execute(query)
        records = cursor.fetchall()
        
        # 处理时间戳格式
        for record in records:
            if 'start_time' in record and record['start_time']:
                record['start_time'] = record['start_time'].isoformat()
            if 'end_time' in record and record['end_time']:
                record['end_time'] = record['end_time'].isoformat()
        
        # 获取坐姿类型分布统计
        type_query = """
            SELECT 
                posture_type, 
                COUNT(*) as count, 
                SUM(duration_seconds) as total_seconds
            FROM posture_time_records
            GROUP BY posture_type
        """
        
        cursor.execute(type_query)
        type_stats = cursor.fetchall()
        
        # 获取总记录数
        cursor.execute("SELECT COUNT(*) as total FROM posture_time_records")
        total_count = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'total_records': total_count,
            'type_distribution': type_stats,
            'records': records
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'获取坐姿时间记录失败: {str(e)}'
        })

@routes_bp.route('/api/debug/add_test_posture_record', methods=['POST'])
def add_test_posture_record():
    """调试接口：添加测试坐姿时间记录"""
    try:
        from datetime import datetime, timedelta
        from modules.database_module import record_posture_time
        
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的数据格式'
            })
        
        # 获取参数
        posture_type = data.get('posture_type', 'mild')  # 默认为轻度不良
        duration_seconds = float(data.get('duration_seconds', 120))  # 默认2分钟
        angle = float(data.get('angle', 40))  # 默认角度40度
        
        # 验证坐姿类型
        valid_types = ['good', 'mild', 'moderate', 'severe']
        if posture_type not in valid_types:
            return jsonify({
                'status': 'error',
                'message': f'无效的坐姿类型，有效类型: {", ".join(valid_types)}'
            })
        
        # 计算开始和结束时间
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=duration_seconds)
        
        # 记录到数据库
        record_id = record_posture_time(
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            angle=angle,
            posture_type=posture_type,
            notes=f"测试添加的{posture_type}坐姿记录，角度：{angle}°"
        )
        
        if record_id:
            return jsonify({
                'status': 'success',
                'message': f'成功添加{posture_type}坐姿测试记录，ID: {record_id}',
                'record': {
                    'id': record_id,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration_seconds,
                    'angle': angle,
                    'posture_type': posture_type
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '添加测试记录失败'
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'添加测试记录出错: {str(e)}'
        })

@routes_bp.route('/api/get_posture_distribution')
def get_posture_distribution():
    """获取不良坐姿时段分布数据
    
    支持的参数:
    - time_range: 预设时间范围 'day', 'week', 'month', 'custom'
    - start_date: 自定义开始日期 (格式: YYYY-MM-DD，仅当time_range为'custom'时有效)
    - end_date: 自定义结束日期 (格式: YYYY-MM-DD，仅当time_range为'custom'时有效)
    """
    try:
        from datetime import datetime, timedelta
        import traceback
        from modules.database_module import get_hourly_posture_data
        
        # 获取时间范围参数
        time_range = request.args.get('time_range', 'day')
        if time_range not in ['day', 'week', 'month', 'custom']:
            time_range = 'day'
        
        # 处理自定义日期范围
        custom_start_date = None
        custom_end_date = None
        
        if time_range == 'custom':
            try:
                # 解析自定义日期参数
                start_date_str = request.args.get('start_date')
                end_date_str = request.args.get('end_date')
                
                if start_date_str and end_date_str:
                    custom_start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    custom_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    # 设置start_date的时间为00:00:00
                    custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    # 设置end_date的时间为23:59:59
                    custom_end_date = custom_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                else:
                    # 如果未提供有效的自定义日期，则使用"今天"作为默认值
                    time_range = 'day'
            except ValueError:
                # 日期格式无效，回退到"今天"
                time_range = 'day'
        
        # 确定查询的日期范围
        now = datetime.now()
        start_date = None
        end_date = None
        
        if time_range == 'day':
            # 今天的数据
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_date = now
        elif time_range == 'week':
            # 本周的数据（从周一开始）
            days_since_monday = now.weekday()
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0) - timedelta(days=days_since_monday)
            end_date = now
        elif time_range == 'month':
            # 本月的数据
            start_date = datetime(now.year, now.month, 1, 0, 0, 0)
            end_date = now
        elif time_range == 'custom' and custom_start_date and custom_end_date:
            # 自定义日期范围
            start_date = custom_start_date
            end_date = custom_end_date
        else:
            # 默认使用今天的数据
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_date = now
            
        # 定义时段范围
        time_periods = [
            {"start": 8, "end": 10, "label": "8-10"},
            {"start": 10, "end": 12, "label": "10-12"},
            {"start": 12, "end": 14, "label": "12-14"},
            {"start": 14, "end": 16, "label": "14-16"},
            {"start": 16, "end": 18, "label": "16-18"},
            {"start": 18, "end": 20, "label": "18-20"}
        ]
        
        # 初始化时段数据
        period_counts = {period["label"]: 0 for period in time_periods}
        
        # 获取全部坐姿时间记录
        import mysql.connector
        from config import DB_CONFIG
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查询不良坐姿记录
        query = """
            SELECT 
                start_time,
                HOUR(start_time) as hour,
                posture_type
            FROM posture_time_records
            WHERE start_time >= %s AND end_time <= %s
            AND (posture_type = 'fair' OR posture_type = 'poor')
        """
        
        cursor.execute(query, (start_date, end_date))
        records = cursor.fetchall()
        
        # 统计每个时段的不良坐姿次数
        for record in records:
            hour = record['hour']
            
            # 找到对应的时段
            for period in time_periods:
                if period["start"] <= hour < period["end"]:
                    period_counts[period["label"]] += 1
                    break
        
        cursor.close()
        conn.close()
        
        # 形成最终结果
        labels = [period["label"] for period in time_periods]
        data = [period_counts[period["label"]] for period in time_periods]
        
        distribution = {
            'labels': labels,
            'data': data,
            'time_range': time_range,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
        
        return jsonify({
            'status': 'success',
            'distribution': distribution
        })
    except Exception as e:
        print(f"获取不良坐姿时段分布数据出错: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f"获取不良坐姿时段分布数据失败: {str(e)}"
        })

# 添加视频流控制路由
@routes_bp.route('/api/toggle_video_stream', methods=['POST'])
def toggle_video_stream():
    """启用或禁用视频流传输"""
    global video_stream_handler
    
    if not video_stream_handler:
        return jsonify({
            'status': 'error',
            'message': '视频流处理器未初始化',
            'is_streaming': False
        })
    
    # 获取请求参数
    data = request.json
    enable = data.get('enable', None)
    
    if enable is None:
        return jsonify({
            'status': 'error',
            'message': '缺少必要参数: enable',
            'is_streaming': video_stream_handler.get_streaming_status()
        })
    
    # 根据参数启用或禁用视频流
    if enable:
        video_stream_handler.enable_streaming()
    else:
        video_stream_handler.disable_streaming()
    
    # 返回当前状态
    return jsonify({
        'status': 'success',
        'message': '视频流已' + ('启用' if enable else '禁用'),
        'is_streaming': video_stream_handler.get_streaming_status()
    })

@routes_bp.route('/api/get_video_stream_status', methods=['GET'])
def get_video_stream_status():
    """获取视频流传输状态"""
    global video_stream_handler
    
    if not video_stream_handler:
        return jsonify({
            'status': 'error',
            'message': '视频流处理器未初始化',
            'is_streaming': False
        })
    
    return jsonify({
        'status': 'success',
        'is_streaming': video_stream_handler.get_streaming_status()
    })

# 添加开启和停止检测服务的API
@routes_bp.route('/api/detection/start', methods=['POST'])
def start_detection():
    """启动目标检测服务"""
    if not detection_service:
        return jsonify({
            'status': 'error',
            'message': '检测服务未初始化'
        })
    
    if detection_service.is_running():
        return jsonify({
            'status': 'success',
            'message': '检测服务已在运行'
        })
    
    try:
        success = detection_service.start()
        if success:
            return jsonify({
                'status': 'success',
                'message': '检测服务启动成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '检测服务启动失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'启动检测服务出错: {str(e)}'
        })

@routes_bp.route('/api/detection/stop', methods=['POST'])
def stop_detection():
    """停止目标检测服务"""
    if not detection_service:
        return jsonify({
            'status': 'error',
            'message': '检测服务未初始化'
        })
    
    if not detection_service.is_running():
        return jsonify({
            'status': 'success',
            'message': '检测服务未运行'
        })
    
    try:
        success = detection_service.stop()
        if success:
            return jsonify({
                'status': 'success',
                'message': '检测服务已停止'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '停止检测服务失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'停止检测服务出错: {str(e)}'
        })

# 语音助手相关API
@routes_bp.route('/api/chatbot/status', methods=['GET'])
def get_chatbot_status():
    """获取语音助手状态"""
    if not chatbot_service:
        return jsonify({
            'status': 'error',
            'message': '语音助手服务未初始化',
            'initialized': False
        })
    
    return jsonify({
        'status': 'success',
        'initialized': True,
        'message': '语音助手服务已初始化'
    })

@routes_bp.route('/api/chatbot/send_message', methods=['POST'])
def send_chatbot_message():
    """向语音助手发送文本消息"""
    if not chatbot_service:
        return jsonify({
            'status': 'error',
            'message': '语音助手服务未初始化'
        })
    
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({
            'status': 'error',
            'message': '消息不能为空'
        })
    
    try:
        response = chatbot_service.send_message(message)
        return jsonify({
            'status': 'success',
            'message': '消息已发送',
            'response': response
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'发送消息失败: {str(e)}'
        })

@routes_bp.route('/api/chatbot/speak_text', methods=['POST'])
def speak_text():
    """使用语音助手朗读指定文本"""
    if not chatbot_service:
        return jsonify({
            'status': 'error',
            'message': '语音助手服务未初始化'
        })
    
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({
            'status': 'error',
            'message': '文本不能为空'
        })
    
    try:
        success = chatbot_service.speak_text(text)
        if success:
            return jsonify({
                'status': 'success',
                'message': '文本朗读成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '文本朗读失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'文本朗读出错: {str(e)}'
        })

@routes_bp.route('/api/chatbot/reset', methods=['POST'])
def reset_chatbot():
    """重置语音助手对话上下文"""
    if not chatbot_service:
        return jsonify({
            'status': 'error',
            'message': '语音助手服务未初始化'
        })
    
    try:
        success = chatbot_service.reset()
        if success:
            return jsonify({
                'status': 'success',
                'message': '语音助手对话上下文已重置'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '重置语音助手对话上下文失败'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'重置语音助手对话上下文出错: {str(e)}'
        })

# =============================================================================
# 家长监护 - 留言系统API
# =============================================================================

@routes_bp.route('/api/guardian/send_message', methods=['POST'])
def send_guardian_message():
    """发送家长留言"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '无效的请求数据'
            }), 400
        
        # 获取请求参数
        sender = data.get('sender', '').strip()
        content = data.get('content', '').strip()
        message_type = data.get('type', 'immediate')
        scheduled_time = data.get('scheduled_time')
        
        # 基本验证
        if not sender:
            return jsonify({
                'status': 'error',
                'message': '发送者身份不能为空'
            }), 400
        
        if not content:
            return jsonify({
                'status': 'error',
                'message': '留言内容不能为空'
            }), 400
        
        # 导入数据库处理器
        from modules.database_module import get_db_handler
        db = get_db_handler()
        
        # 发送留言
        result = db.send_guardian_message(sender, content, message_type, scheduled_time)
        print(f"DEBUG: 数据库方法返回结果: {result}")
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        print(f"ERROR: 发送家长留言API出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

@routes_bp.route('/api/guardian/get_messages', methods=['GET'])
def get_guardian_messages():
    """获取家长留言历史"""
    try:
        # 获取分页参数
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 限制参数范围
        limit = min(max(limit, 1), 100)  # 限制在1-100之间
        offset = max(offset, 0)
        
        # 导入数据库处理器
        from modules.database_module import get_db_handler
        db = get_db_handler()
        
        # 获取留言历史
        result = db.get_guardian_messages(limit, offset)
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'messages': result['messages'],
                'total': result['total'],
                'limit': result['limit'],
                'offset': result['offset']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
        
    except Exception as e:
        print(f"获取家长留言历史API出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@routes_bp.route('/api/guardian/message_status/<int:message_id>', methods=['PUT'])
def update_guardian_message_status(message_id):
    """更新留言状态"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少状态参数'
            }), 400
        
        status = data['status']
        
        # 导入数据库处理器
        from modules.database_module import get_db_handler
        db = get_db_handler()
        
        # 更新状态
        result = db.update_message_status(message_id, status)
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        print(f"更新留言状态API出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

# =============================================================================
# 家长监护 - 视频流API
# =============================================================================

@routes_bp.route('/video_feed')
def video_feed():
    """原始视频流接口，支持分辨率参数，仅返回纯原始视频不带任何文字标记"""
    try:
        # 获取分辨率参数
        resolution = request.args.get('resolution', '480p')
        
        if not video_stream_handler:
            # 如果视频流处理器未初始化，返回纯色图像（不添加任何文本）
            error_msg = "视频流处理器未初始化"
            print(f"ERROR: {error_msg}")
            
            # 创建一个纯色图像
            img = np.ones((480, 640, 3), dtype=np.uint8) * 200
            
            # 将图像编码为JPEG并返回
            success, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if success:
                return Response(
                    (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'),
                    mimetype='multipart/x-mixed-replace; boundary=frame'
                )
            return "视频流处理器未初始化", 503
        
        # 确保视频流已启用
        if not video_stream_handler.get_streaming_status():
            print("DEBUG: 视频流未启用，现在启用它")
            video_stream_handler.enable_streaming()
        
        # 生成纯原始视频流（不带任何标记和处理）
        def generate_pure_raw_video_stream():
            try:
                # 启用视频流
                if not video_stream_handler.get_streaming_status():
                    video_stream_handler.enable_streaming()
                
                # 获取原始视频流帧
                while True:
                    # 直接使用全局姿势监测器获取原始摄像头帧（不经过任何处理）
                    global posture_monitor
                    frame = None
                    
                    if posture_monitor and hasattr(posture_monitor, 'cap') and posture_monitor.cap.isOpened():
                        ret, raw_frame = posture_monitor.cap.read()
                        if ret and raw_frame is not None and raw_frame.size > 0:
                            frame = raw_frame.copy()  # 获取完全未处理的原始相机帧
                    
                    # 如果无法获取原始帧，使用备用空白帧
                    if frame is None:
                        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
                    
                    # 调整分辨率（如果需要）
                    if resolution != '480p':
                        resolution_map = {
                            'high': (720, 540),
                            'medium': (640, 480),
                            'low': (320, 240),
                            '720p': (720, 540),
                            '480p': (640, 480),
                            '360p': (480, 360),
                            '240p': (320, 240)
                        }
                        if resolution in resolution_map:
                            width, height = resolution_map[resolution]
                            frame = cv2.resize(frame, (width, height))
                    
                    # 编码并返回帧
                    success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                    if success:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
                    # 控制帧率
                    time.sleep(0.033)  # 约30fps
                    
            except Exception as e:
                print(f"生成纯原始视频流出错: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 创建一个纯色图像，不添加任何文本
                img = np.ones((480, 640, 3), dtype=np.uint8) * 200
                
                # 将图像编码为JPEG并返回
                success, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if success:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                # 防止循环过快
                time.sleep(2)
        
        # 返回视频流响应
        return Response(
            stream_with_context(generate_pure_raw_video_stream()),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
        
    except Exception as e:
        print(f"生成纯原始视频流出错: {str(e)}")
        return "视频流生成失败", 500

@routes_bp.route('/api/guardian/video_status', methods=['GET'])
def get_video_status():
    """获取视频流状态"""
    try:
        if not video_stream_handler:
            return jsonify({
                'status': 'error',
                'message': '视频流处理器未初始化',
                'video_active': False
            }), 503
        
        # 获取当前视频流状态
        is_streaming = video_stream_handler.get_streaming_status()
        
        # 如果请求中包含enable=true参数，启用视频流
        if request.args.get('enable') == 'true' and not is_streaming:
            video_stream_handler.enable_streaming()
            is_streaming = True
        
        # 如果请求中包含disable=true参数，禁用视频流
        if request.args.get('disable') == 'true' and is_streaming:
            video_stream_handler.disable_streaming()
            is_streaming = False
        
        # 获取当前分辨率
        width, height = video_stream_handler.stream_width, video_stream_handler.stream_height
        resolution = f"{width}x{height}"
        
        # 尝试获取FPS信息
        fps = 0
        try:
            fps = video_stream_handler.pose_stream_fps.get_fps()
        except:
            pass
        
        # 检查是否有有效的原始帧
        has_raw_frame = hasattr(video_stream_handler, 'last_raw_frame') and video_stream_handler.last_raw_frame is not None
        
        return jsonify({
            'status': 'success',
            'video_active': is_streaming,
            'has_frame': has_raw_frame,
            'resolution': resolution,
            'fps': round(fps, 1),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"获取视频流状态API出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}',
            'video_active': False
        }), 500
