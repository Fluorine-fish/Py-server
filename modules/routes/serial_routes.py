"""
串口通信相关路由模块
包含所有与串口通信相关的API端点
"""

from flask import jsonify, request
from . import routes_bp
import json
import time
from modules.serial_module import SerialHandler

# 获取串口设备列表
@routes_bp.route('/api/serial/ports')
def get_serial_ports():
    """获取可用的串口设备列表"""
    try:
        ports = SerialHandler.get_available_ports()
        return jsonify({"ports": ports})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 连接到串口
@routes_bp.route('/api/serial/connect', methods=['POST'])
def connect_serial():
    """连接到指定的串口设备"""
    try:
        data = request.json
        port = data.get('port')
        baud_rate = data.get('baud_rate', 9600)
        
        if not port:
            return jsonify({"error": "未指定串口"}), 400
            
        success = SerialHandler.connect(port, baud_rate)
        
        if success:
            return jsonify({"status": "connected", "port": port, "baud_rate": baud_rate})
        else:
            return jsonify({"error": "连接失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 断开串口连接
@routes_bp.route('/api/serial/disconnect')
def disconnect_serial():
    """断开当前串口连接"""
    try:
        SerialHandler.disconnect()
        return jsonify({"status": "disconnected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取串口状态
@routes_bp.route('/api/serial/status')
def get_serial_status():
    """获取当前串口连接状态"""
    status = {
        "connected": SerialHandler.is_connected(),
        "port": SerialHandler.current_port,
        "baud_rate": SerialHandler.baud_rate,
        "bytes_sent": SerialHandler.bytes_sent,
        "bytes_received": SerialHandler.bytes_received,
        "last_activity": SerialHandler.last_activity_time
    }
    return jsonify(status)

# 发送串口数据
@routes_bp.route('/api/serial/send', methods=['POST'])
def send_serial_data():
    """向串口发送数据"""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "未提供消息内容"}), 400
            
        if not SerialHandler.is_connected():
            return jsonify({"error": "串口未连接"}), 400
            
        success = SerialHandler.send_data(message)
        
        if success:
            return jsonify({
                "status": "sent", 
                "message": message,
                "bytes_sent": len(message),
                "timestamp": time.time()
            })
        else:
            return jsonify({"error": "发送失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 接收串口数据
@routes_bp.route('/api/serial/receive')
def receive_serial_data():
    """从串口接收数据"""
    try:
        if not SerialHandler.is_connected():
            return jsonify({"error": "串口未连接"}), 400
            
        data = SerialHandler.read_data()
        
        return jsonify({
            "status": "received",
            "data": data,
            "bytes_received": len(data) if data else 0,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 发送自定义命令
@routes_bp.route('/api/serial/command', methods=['POST'])
def send_command():
    """发送预定义命令到串口"""
    try:
        data = request.json
        command_type = data.get('type')
        params = data.get('params', {})
        
        if not command_type:
            return jsonify({"error": "未指定命令类型"}), 400
            
        if not SerialHandler.is_connected():
            return jsonify({"error": "串口未连接"}), 400
        
        # 根据命令类型构建命令
        command = ""
        if command_type == "position":
            # 格式: "P:X,Y,Z"
            x = params.get('x', 0)
            y = params.get('y', 0)
            z = params.get('z', 0)
            command = f"P:{x},{y},{z}"
        elif command_type == "led":
            # 格式: "L:R,G,B"
            r = params.get('r', 0)
            g = params.get('g', 0)
            b = params.get('b', 0)
            command = f"L:{r},{g},{b}"
        elif command_type == "motor":
            # 格式: "M:SPEED,DIR"
            speed = params.get('speed', 0)
            direction = params.get('direction', 0)
            command = f"M:{speed},{direction}"
        elif command_type == "custom":
            # 自定义命令直接发送
            command = params.get('command', '')
        else:
            return jsonify({"error": "不支持的命令类型"}), 400
            
        # 发送命令
        success = SerialHandler.send_data(command)
        
        if success:
            return jsonify({
                "status": "command_sent", 
                "command_type": command_type,
                "command": command,
                "timestamp": time.time()
            })
        else:
            return jsonify({"error": "命令发送失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 清除串口缓冲区
@routes_bp.route('/api/serial/clear')
def clear_serial_buffer():
    """清除串口接收缓冲区"""
    try:
        if not SerialHandler.is_connected():
            return jsonify({"error": "串口未连接"}), 400
            
        SerialHandler.clear_buffer()
        return jsonify({"status": "buffer_cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取串口历史记录
@routes_bp.route('/api/serial/history')
def get_serial_history():
    """获取串口通信历史记录"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = SerialHandler.get_history(limit)
        
        return jsonify({
            "history": history,
            "count": len(history),
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500