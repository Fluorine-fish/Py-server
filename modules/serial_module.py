"""
串口通信模块 - 处理与下位机的通信
"""
import serial
import struct
import time
import queue
import math
from threading import Lock
from .logging_module import log_manager
from serial_handler import SerialHandler

class SerialCommunicationHandler:
    """
    串口通信处理器 - 包装SerialHandler类，添加特定于应用的功能
    """
    # 提醒类型定义
    REMINDER_NONE = 0      # 无提醒
    REMINDER_SITTING = 1   # 久坐提醒
    REMINDER_POSTURE = 2   # 坐姿提醒
    REMINDER_VOICE = 3     # 语音交互

    # 坐姿提醒子类型（使用帧字节11之后的字节）
    POSTURE_WARN_NONE = 0x00      # 无警告
    POSTURE_WARN_NECK = 0x01      # 颈部前倾
    POSTURE_WARN_SHOULDER = 0x02   # 肩部倾斜
    POSTURE_WARN_SPINE = 0x03      # 脊柱弯曲
    POSTURE_WARN_HEAD = 0x04       # 头部侧倾
    POSTURE_WARN_MULTIPLE = 0x0F   # 多个问题

    # 通信协议常量
    FRAME_HEADER = b's'
    FRAME_TAIL = b'e'
    FRAME_LENGTH = 32
    
    # 指令类型
    CMD_TYPE_CONTROL = 0xA0    # 控制指令
    CMD_TYPE_STATUS = 0xB0     # 状态反馈
    CMD_TYPE_POSTURE = 0xA1    # 姿势矫正
    CMD_TYPE_SITTING = 0xA2    # 久坐提醒
    CMD_TYPE_ALERT = 0xA3      # 警报指令
    CMD_TYPE_LIGHT = 0xA4      # 照明控制
    CMD_TYPE_VOICE = 0xA5      # 语音控制指令（新增）

    # 照明控制字段偏移量（使用保留字节区域）
    LIGHT_BRIGHTNESS_OFFSET = 12  # 亮度值偏移量（4字节浮点数）
    LIGHT_COLOR_TEMP_OFFSET = 16  # 色温值偏移量（4字节浮点数）
    LIGHT_MODE_OFFSET = 20       # 照明模式偏移量（1字节）

    # 照明模式定义
    LIGHT_MODE_MANUAL = 0x00     # 手动模式
    LIGHT_MODE_AUTO = 0x01       # 自动模式
    LIGHT_MODE_READING = 0x02    # 阅读模式
    LIGHT_MODE_REST = 0x03       # 休息模式

    # 照明控制常量
    MIN_COLOR_TEMP = 3000.0  # 最小色温值 (K)
    MAX_COLOR_TEMP = 6500.0  # 最大色温值 (K)
    MIN_BRIGHTNESS = 0.0     # 最小亮度值 (%)
    MAX_BRIGHTNESS = 100.0   # 最大亮度值 (%)

    # 语音交互相关常量
    VOICE_CMD_START = 0x01    # 开始语音交互
    VOICE_CMD_STOP = 0x02     # 停止语音交互
    VOICE_CMD_PAUSE = 0x03    # 暂停语音交互
    VOICE_CMD_RESUME = 0x04   # 恢复语音交互
    VOICE_CMD_VOLUME = 0x05   # 调节音量

    def __init__(self, port=None, baudrate=115200):
        self.handler = SerialHandler(port=port, baudrate=baudrate)
        self.initialized = True
        self.port = port
        self.baudrate = baudrate
        self._frame_queue = queue.Queue(maxsize=100)
        self._start_frame_monitor()
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
    
    def _build_sitting_reminder_frame(self, duration, intensity=1.0):
        """构建久坐提醒帧
        
        Args:
            duration: 久坐持续时间（分钟）
            intensity: 提醒强度 (0.0-1.0)
        """
        frame = bytearray(self.FRAME_LENGTH)
        frame[0] = ord(self.FRAME_HEADER)  # 帧头
        frame[1] = self.CMD_TYPE_SITTING   # 久坐提醒指令类型
        
        # 填充久坐时长（4字节）
        struct.pack_into('I', frame, 2, int(duration))
        
        # 填充提醒强度（4字节浮点数）
        struct.pack_into('f', frame, 6, float(intensity))
        
        # 填充提醒类型（1字节）
        frame[10] = self.REMINDER_SITTING
        
        # 保留字节，用于未来扩展
        for i in range(11, self.FRAME_LENGTH-1):
            frame[i] = 0x00
            
        frame[-1] = ord(self.FRAME_TAIL)  # 帧尾
        return frame
        
    def send_sitting_reminder(self, duration):
        """发送久坐提醒
        
        Args:
            duration: 久坐持续时间（分钟）
        
        Returns:
            bool: 发送是否成功
        """
        try:
            # 根据久坐时间计算提醒强度
            base_intensity = 0.6  # 基础强度
            time_factor = min(duration / 60.0, 1.0)  # 时间因子，最大1.0
            intensity = base_intensity + (1.0 - base_intensity) * time_factor
            
            frame = self._build_sitting_reminder_frame(duration, intensity)
            with self.lock:
                self.serial_port.write(frame)
                log_manager.info(f"发送久坐提醒: 持续时间={duration}分钟, 强度={intensity:.2f}")
                return True
        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"发送久坐提醒失败: {e}")
            return False
    
    def send_posture_warning(self, warning_types):
        """发送坐姿警告
        
        Args:
            warning_types: 警告类型列表，可以包含多个警告
            
        Returns:
            bool: 发送是否成功
        """
        try:
            frame = bytearray(self.FRAME_LENGTH)
            frame[0] = ord(self.FRAME_HEADER)
            frame[1] = self.CMD_TYPE_POSTURE
            
            # 设置提醒类型为坐姿提醒
            frame[11] = self.REMINDER_POSTURE
            
            # 根据警告类型设置具体的提醒子类型
            if not warning_types:
                frame[12] = self.POSTURE_WARN_NONE
            elif len(warning_types) == 1:
                warning_map = {
                    'WARN_NECK_BEND': self.POSTURE_WARN_NECK,
                    'WARN_SHOULDER_TILT': self.POSTURE_WARN_SHOULDER,
                    'WARN_SPINE_BEND': self.POSTURE_WARN_SPINE,
                    'WARN_HEAD_TILT': self.POSTURE_WARN_HEAD
                }
                frame[12] = warning_map.get(warning_types[0], self.POSTURE_WARN_NONE)
            else:
                frame[12] = self.POSTURE_WARN_MULTIPLE
                
            # 当存在多个警告时，在后续字节中记录具体警告类型
            if len(warning_types) > 1:
                warning_bits = 0
                for warning in warning_types:
                    if 'NECK' in warning:
                        warning_bits |= (1 << 0)
                    if 'SHOULDER' in warning:
                        warning_bits |= (1 << 1)
                    if 'SPINE' in warning:
                        warning_bits |= (1 << 2)
                    if 'HEAD' in warning:
                        warning_bits |= (1 << 3)
                frame[13] = warning_bits
            
            frame[-1] = ord(self.FRAME_TAIL)
            
            with self.lock:
                self.serial_port.write(frame)
                log_manager.info(f"发送坐姿提醒: {warning_types}")
                return True
                
        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"发送坐姿提醒失败: {e}")
            return False

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

    def send_sitting_reminder(self):
        """发送久坐提醒"""
        return self.handler.send_reminder(self.REMINDER_SITTING)

    def send_posture_reminder(self, yaw=0.0, pitch=0.0):
        """发送坐姿提醒，可以指定机械臂角度"""
        return self.handler.send_reminder(self.REMINDER_POSTURE, yaw, pitch)

    def send_voice_interaction(self):
        """发送语音交互信号"""
        return self.handler.send_reminder(self.REMINDER_VOICE)

    def send_light_control(self, brightness: float, color_temp: float, mode: int = 0) -> bool:
        """发送照明控制命令
        
        Args:
            brightness: 亮度值 (0.0-100.0)，表示灯光亮度的百分比
            color_temp: 色温值 (3000-6500K)，较低的值产生暖光，较高的值产生冷光
            mode: 照明模式，可选值：
                  LIGHT_MODE_MANUAL(0): 手动模式
                  LIGHT_MODE_AUTO(1): 自动模式
                  LIGHT_MODE_READING(2): 阅读模式
                  LIGHT_MODE_REST(3): 休息模式
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 参数验证
            brightness = max(0.0, min(100.0, brightness))
            color_temp = max(3000.0, min(6500.0, color_temp))
            mode = max(0, min(3, mode))

            frame = bytearray(self.FRAME_LENGTH)
            frame[0] = ord(self.FRAME_HEADER)         # 帧头
            frame[1] = self.CMD_TYPE_LIGHT            # 照明控制指令

            # 填充亮度值
            struct.pack_into('f', frame, self.LIGHT_BRIGHTNESS_OFFSET, float(brightness))
            
            # 填充色温值
            struct.pack_into('f', frame, self.LIGHT_COLOR_TEMP_OFFSET, float(color_temp))
            
            # 填充照明模式
            frame[self.LIGHT_MODE_OFFSET] = mode
            
            # 填充帧尾
            frame[-1] = ord(self.FRAME_TAIL)

            with self.lock:
                self.serial_port.write(frame)
                log_manager.info(f"发送照明控制命令: 亮度={brightness:.1f}%, 色温={color_temp:.0f}K, 模式={mode}")
                return True

        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"发送照明控制命令失败: {e}")
            return False

    def _handle_light_status(self, frame_data):
        """处理照明状态反馈"""
        try:
            if 'light_status' in frame_data:
                brightness = frame_data.get('brightness', 0.0)
                color_temp = frame_data.get('color_temp', 4000.0)
                mode = frame_data.get('mode', 0)
                log_manager.debug(f"收到照明状态: 亮度={brightness:.1f}%, 色温={color_temp:.0f}K, 模式={mode}")
                # 这里可以添加更多处理逻辑
        except Exception as e:
            log_manager.error(f"处理照明状态数据失败: {e}")

    def _handle_alert_status(self, frame_data):
        """处理提醒状态反馈
        如果下位机返回了提醒状态，这里可以进行相应处理
        """
        if 'alert_status' in frame_data:
            alert_status = frame_data['alert_status']
            if alert_status > 0:
                print(f"收到提醒状态反馈: {alert_status}")
                # 这里可以添加更多的状态处理逻辑

    def _start_frame_monitor(self):
        """启动帧监控，将收到的帧数据放入队列"""
        def frame_callback(frame_data):
            try:
                # 处理提醒状态
                self._handle_alert_status(frame_data)
                
                # 转换弧度为角度以便前端显示
                frame_data_with_degrees = frame_data.copy()
                frame_data_with_degrees['yaw_degrees'] = math.degrees(frame_data['yaw'])
                frame_data_with_degrees['pitch_degrees'] = math.degrees(frame_data['pitch'])
                frame_data_with_degrees['timestamp'] = time.time()
                
                try:
                    self._frame_queue.put_nowait(frame_data_with_degrees)
                    print(f"收到新帧数据: type={frame_data['type']}, " 
                          f"yaw={frame_data_with_degrees['yaw_degrees']:.2f}°, "
                          f"pitch={frame_data_with_degrees['pitch_degrees']:.2f}°, "
                          f"alert_status={frame_data.get('alert_status', 0)}")
                except queue.Full:
                    try:
                        self._frame_queue.get_nowait()
                        self._frame_queue.put_nowait(frame_data_with_degrees)
                    except:
                        pass
            except Exception as e:
                print(f"处理帧数据时出错: {str(e)}")
        
        if hasattr(self.handler, 'start_frame_monitor'):
            self.handler.start_frame_monitor(callback=frame_callback)
            print("已启动帧数据监控")

    def _build_voice_frame(self, command, params=None):
        """构建语音交互帧
        
        Args:
            command: 语音命令类型
            params: 可选的参数字典
        """
        frame = bytearray(self.FRAME_LENGTH)
        frame[0] = ord(self.FRAME_HEADER)  # 帧头
        frame[1] = self.CMD_TYPE_VOICE     # 语音指令类型
        
        # 设置提醒类型为语音交互
        frame[11] = self.REMINDER_VOICE
        
        # 设置具体命令类型
        frame[12] = command
        
        # 处理参数
        if params:
            # 音量参数（0-100）
            if 'volume' in params:
                frame[13] = min(100, max(0, params['volume']))
            
            # 语音持续时间（秒）
            if 'duration' in params:
                struct.pack_into('H', frame, 14, params['duration'])
                
            # 其他参数可以放在保留字节中
            if 'data' in params:
                data_bytes = params['data'].encode('utf-8')[:16]  # 最多16字节
                frame[16:16+len(data_bytes)] = data_bytes
        
        frame[-1] = ord(self.FRAME_TAIL)   # 帧尾
        return frame
        
    def send_voice_command(self, command_type, **params):
        """发送语音控制命令
        
        Args:
            command_type: 命令类型（START/STOP/PAUSE/RESUME/VOLUME）
            **params: 可选参数，如音量、持续时间等
        
        Returns:
            bool: 发送是否成功
        """
        try:
            if not self.is_connected:
                log_manager.error("串口未连接")
                return False
                
            # 构建命令帧
            frame = self._build_voice_frame(command_type, params)
            
            with self.lock:
                self.serial_port.write(frame)
                log_manager.info(f"发送语音命令：类型={command_type}, 参数={params}")
                return True
                
        except Exception as e:
            self.last_error = str(e)
            log_manager.error(f"发送语音命令失败: {e}")
            return False
    
    def start_voice_interaction(self, volume=80):
        """开始语音交互"""
        return self.send_voice_command(VOICE_CMD_START, volume=volume)
    
    def stop_voice_interaction(self):
        """停止语音交互"""
        return self.send_voice_command(VOICE_CMD_STOP)
    
    def pause_voice_interaction(self):
        """暂停语音交互"""
        return self.send_voice_command(VOICE_CMD_PAUSE)
    
    def resume_voice_interaction(self):
        """恢复语音交互"""
        return self.send_voice_command(VOICE_CMD_RESUME)
    
    def set_voice_volume(self, volume):
        """设置语音音量
        
        Args:
            volume: 音量值（0-100）
        """
        return self.send_voice_command(VOICE_CMD_VOLUME, volume=volume)
    
    def _handle_voice_status(self, frame_data):
        """处理语音状态反馈"""
        try:
            if 'voice_status' in frame_data:
                status = frame_data['voice_status']
                volume = frame_data.get('volume', 80)
                log_manager.debug(f"收到语音状态：status={status}, volume={volume}")
                # 这里可以添加更多处理逻辑
        except Exception as e:
            log_manager.error(f"处理语音状态数据失败: {e}")
