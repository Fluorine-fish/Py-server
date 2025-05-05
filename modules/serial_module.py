"""
串口通信模块 - 负责与机械臂控制器的通信
"""
import serial
import struct
import time
from threading import Lock
from .logging_module import log_manager

class SerialCommunicationHandler:
    """串口通信处理器"""
    
    # 通信协议常量
    FRAME_HEADER = b's'
    FRAME_TAIL = b'e'
    FRAME_LENGTH = 32
    
    # 指令类型
    CMD_TYPE_CONTROL = 0xA0  # 控制指令
    CMD_TYPE_STATUS = 0xB0   # 状态反馈
    CMD_TYPE_POSTURE = 0xA1  # 姿势矫正
    CMD_TYPE_SITTING = 0xA2  # 久坐提醒
    
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.lock = Lock()
        self.is_connected = False
        self.last_error = None
        
    def connect(self):
        """连接到串口设备"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.is_connected = True
            log_manager.info(f"成功连接到串口设备 {self.port}")
            return True
        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"连接串口设备失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开串口连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        log_manager.info("已断开串口连接")
    
    def send_command(self, command_data):
        """发送命令到机械臂控制器
        
        Args:
            command_data: 包含命令信息的字典
        """
        if not self.is_connected:
            log_manager.error("串口未连接")
            return False
            
        try:
            with self.lock:
                if command_data['command'] == 'posture_correction':
                    frame = self._build_posture_frame(command_data['angle'])
                elif command_data['command'] == 'sitting_reminder':
                    frame = self._build_sitting_frame(command_data['duration'])
                else:
                    frame = self._build_control_frame(command_data)
                
                self.serial_port.write(frame)
                log_manager.debug(f"发送命令: {command_data}")
                return True
        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"发送命令失败: {e}")
            return False
    
    def _build_control_frame(self, command_data):
        """构建标准控制帧"""
        frame = bytearray(self.FRAME_LENGTH)
        frame[0] = ord(self.FRAME_HEADER)  # 帧头
        frame[1] = self.CMD_TYPE_CONTROL   # 控制指令类型
        
        # 填充控制数据
        struct.pack_into('?', frame, 2, command_data.get('find_bool', False))
        struct.pack_into('f', frame, 3, command_data.get('yaw', 0.0))
        struct.pack_into('f', frame, 7, command_data.get('pitch', 0.0))
        
        frame[-1] = ord(self.FRAME_TAIL)   # 帧尾
        return frame
    
    def _build_posture_frame(self, angle):
        """构建姿势矫正帧
        
        Args:
            angle: 检测到的头部角度
        """
        frame = bytearray(self.FRAME_LENGTH)
        frame[0] = ord(self.FRAME_HEADER)  # 帧头
        frame[1] = self.CMD_TYPE_POSTURE   # 姿势矫正指令类型
        
        # 计算矫正角度
        correction_angle = min(max(-45, angle), 45)  # 限制矫正角度范围
        struct.pack_into('f', frame, 2, correction_angle)
        
        # 添加矫正力度参数（0-1范围）
        force = min(abs(angle) / 45.0, 1.0)  # 角度越大，力度越大
        struct.pack_into('f', frame, 6, force)
        
        frame[-1] = ord(self.FRAME_TAIL)   # 帧尾
        return frame
    
    def _build_sitting_frame(self, duration):
        """构建久坐提醒帧
        
        Args:
            duration: 久坐时长（分钟）
        """
        frame = bytearray(self.FRAME_LENGTH)
        frame[0] = ord(self.FRAME_HEADER)  # 帧头
        frame[1] = self.CMD_TYPE_SITTING   # 久坐提醒指令类型
        
        # 填充久坐时长
        struct.pack_into('I', frame, 2, duration)
        
        # 计算提醒强度（基于久坐时长）
        intensity = min(duration / 60.0, 1.0)  # 超过1小时达到最大强度
        struct.pack_into('f', frame, 6, intensity)
        
        frame[-1] = ord(self.FRAME_TAIL)   # 帧尾
        return frame
    
    def receive_status(self):
        """接收机械臂状态反馈
        
        Returns:
            状态数据字典或None（如果接收失败）
        """
        if not self.is_connected:
            return None
            
        try:
            with self.lock:
                # 等待帧头
                while self.serial_port.read() != self.FRAME_HEADER:
                    continue
                
                # 读取剩余数据
                data = self.serial_port.read(self.FRAME_LENGTH - 1)
                if len(data) != self.FRAME_LENGTH - 1:
                    return None
                
                if data[-1] != ord(self.FRAME_TAIL):
                    return None
                
                # 解析数据
                cmd_type = data[0]
                if cmd_type == self.CMD_TYPE_STATUS:
                    yaw = struct.unpack('f', data[1:5])[0]
                    pitch = struct.unpack('f', data[5:9])[0]
                    
                    return {
                        'yaw': yaw,
                        'pitch': pitch
                    }
                    
                return None
        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"接收状态数据失败: {e}")
            return None
    
    def get_last_error(self):
        """获取最后一次错误信息"""
        return self.last_error
    
    def is_port_available(self):
        """检查串口是否可用"""
        try:
            temp_port = serial.Serial(self.port)
            temp_port.close()
            return True
        except:
            return False
    
    def flush_buffers(self):
        """清空串口缓冲区"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
