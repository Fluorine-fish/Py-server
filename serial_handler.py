"""串口通信处理模块 - 处理与硬件设备的通信"""
import serial
import time
import threading
import queue
import json
from datetime import datetime
from modules.database_module import save_record_to_db, save_frame_to_db

# 串口配置常量
BAUDRATE = 115200
TIMEOUT = 1
MAX_RETRY = 3

# 帧格式定义
FRAME_HEADER = 0xAA
FRAME_TAIL = 0x55
FRAME_VERSION = 0x01

# 命令类型
CMD_HEARTBEAT = 0x01     # 心跳包
CMD_POSTURE = 0x02       # 姿势数据
CMD_EMOTION = 0x03       # 情绪数据
CMD_WARNING = 0x04       # 警告信息
CMD_CONFIG = 0x05        # 配置信息

# 姿势警告类型
WARN_HEAD_TILT = 0x01    # 头部倾斜
WARN_NECK_BEND = 0x02    # 颈部弯曲
WARN_SHOULDER_TILT = 0x03 # 肩部倾斜
WARN_SPINE_BEND = 0x04   # 脊柱弯曲
WARN_DISTANCE = 0x05     # 距离不当
WARN_LIGHT = 0x06        # 光线不足

class SerialHandler:
    """串口通信处理类"""
    def __init__(self, port=None):
        self.port = port
        self.serial = None
        self.is_running = False
        self.read_thread = None
        self.write_thread = None
        self.send_queue = queue.Queue()
        self.last_heartbeat = time.time()
        self.device_status = {
            'connected': False,
            'last_error': None,
            'retry_count': 0
        }
    
    def start(self, port=None):
        """启动串口通信"""
        if port:
            self.port = port
            
        if not self.port:
            self.device_status['last_error'] = "未指定串口"
            return False
            
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=BAUDRATE,
                timeout=TIMEOUT
            )
            
            if not self.serial.is_open:
                self.serial.open()
            
            self.is_running = True
            self.device_status['connected'] = True
            self.device_status['last_error'] = None
            self.device_status['retry_count'] = 0
            
            # 启动读写线程
            self.read_thread = threading.Thread(target=self._read_loop)
            self.write_thread = threading.Thread(target=self._write_loop)
            self.read_thread.daemon = True
            self.write_thread.daemon = True
            self.read_thread.start()
            self.write_thread.start()
            
            return True
        except Exception as e:
            self.device_status['last_error'] = str(e)
            print(f"启动串口通信失败: {e}")
            return False
    
    def stop(self):
        """停止串口通信"""
        self.is_running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.device_status['connected'] = False
    
    def send_posture_warning(self, warning_data):
        """发送姿势警告
        
        Args:
            warning_data: dict, 包含以下字段：
                warning_type: 警告类型
                angle: 角度值
                threshold: 阈值
                duration: 持续时间
        """
        try:
            frame = self._build_frame(CMD_WARNING, warning_data)
            self.send_queue.put(frame)
            return True
        except Exception as e:
            print(f"构建警告帧失败: {e}")
            return False
    
    def send_posture_data(self, posture_data):
        """发送姿势数据
        
        Args:
            posture_data: dict, 包含以下字段：
                head_angle: 头部角度
                neck_angle: 颈部角度
                shoulder_tilt: 肩部倾斜
                spine_angle: 脊柱角度
                quality: 姿势质量
                score: 综合评分
        """
        try:
            frame = self._build_frame(CMD_POSTURE, posture_data)
            self.send_queue.put(frame)
            return True
        except Exception as e:
            print(f"构建姿势数据帧失败: {e}")
            return False
    
    def send_emotion_data(self, emotion_data):
        """发送情绪数据"""
        try:
            frame = self._build_frame(CMD_EMOTION, emotion_data)
            self.send_queue.put(frame)
            return True
        except Exception as e:
            print(f"构建情绪数据帧失败: {e}")
            return False
    
    def _build_frame(self, cmd_type, data):
        """构建数据帧"""
        try:
            # 将数据转换为JSON字符串
            data_str = json.dumps(data)
            data_bytes = data_str.encode('utf-8')
            
            # 计算数据长度
            length = len(data_bytes) + 6  # 帧头(1) + 版本(1) + 命令(1) + 长度(2) + 校验(1)
            
            # 构建帧
            frame = bytearray()
            frame.append(FRAME_HEADER)  # 帧头
            frame.append(FRAME_VERSION) # 版本号
            frame.append(cmd_type)      # 命令类型
            frame.append((length >> 8) & 0xFF)  # 长度高字节
            frame.append(length & 0xFF)         # 长度低字节
            frame.extend(data_bytes)    # 数据
            
            # 计算校验和
            checksum = 0
            for b in frame[1:]:  # 从版本号开始计算
                checksum ^= b
            frame.append(checksum)  # 校验和
            frame.append(FRAME_TAIL)  # 帧尾
            
            return frame
        except Exception as e:
            print(f"构建数据帧失败: {e}")
            raise
    
    def _read_loop(self):
        """串口读取循环"""
        buffer = bytearray()
        while self.is_running:
            try:
                if self.serial and self.serial.is_open:
                    if self.serial.in_waiting:
                        data = self.serial.read(self.serial.in_waiting)
                        buffer.extend(data)
                        
                        # 处理完整的帧
                        while len(buffer) > 0:
                            # 查找帧头
                            start = buffer.find(bytes([FRAME_HEADER]))
                            if start == -1:
                                buffer.clear()
                                break
                                
                            if start > 0:
                                buffer = buffer[start:]
                                
                            # 检查帧长度
                            if len(buffer) < 6:  # 最小帧长度
                                break
                                
                            # 获取帧长度
                            length = (buffer[3] << 8) | buffer[4]
                            if len(buffer) < length + 1:  # +1 for frame tail
                                break
                                
                            # 提取完整帧
                            frame = buffer[:length+1]
                            buffer = buffer[length+1:]
                            
                            # 处理帧
                            self._process_frame(frame)
                    else:
                        time.sleep(0.01)
            except Exception as e:
                print(f"串口读取错误: {e}")
                self.device_status['last_error'] = str(e)
                time.sleep(1)
    
    def _write_loop(self):
        """串口写入循环"""
        while self.is_running:
            try:
                if not self.send_queue.empty() and self.serial and self.serial.is_open:
                    data = self.send_queue.get()
                    self.serial.write(data)
                    self.serial.flush()
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"串口写入错误: {e}")
                self.device_status['last_error'] = str(e)
                time.sleep(1)
    
    def _process_frame(self, frame):
        """处理接收到的数据帧"""
        try:
            # 验证帧格式
            if len(frame) < 6 or frame[0] != FRAME_HEADER or frame[-1] != FRAME_TAIL:
                print("无效的帧格式")
                return
                
            # 提取帧信息
            version = frame[1]
            cmd_type = frame[2]
            length = (frame[3] << 8) | frame[4]
            data = frame[5:-2]  # 去除头部信息和校验和
            checksum = frame[-2]
            
            # 验证校验和
            calc_checksum = 0
            for b in frame[1:-2]:
                calc_checksum ^= b
            if calc_checksum != checksum:
                print("校验和错误")
                return
                
            # 处理不同类型的命令
            if cmd_type == CMD_HEARTBEAT:
                self._handle_heartbeat(data)
            elif cmd_type == CMD_POSTURE:
                self._handle_posture_data(data)
            elif cmd_type == CMD_EMOTION:
                self._handle_emotion_data(data)
            elif cmd_type == CMD_WARNING:
                self._handle_warning(data)
            elif cmd_type == CMD_CONFIG:
                self._handle_config(data)
            else:
                print(f"未知的命令类型: {cmd_type}")
            
            # 保存记录到数据库
            save_frame_to_db({
                'timestamp': datetime.now().isoformat(),
                'version': version,
                'cmd_type': cmd_type,
                'data': data.decode('utf-8', errors='ignore')
            })
        except Exception as e:
            print(f"处理帧数据失败: {e}")
    
    def _handle_heartbeat(self, data):
        """处理心跳包"""
        self.last_heartbeat = time.time()
        self.device_status['connected'] = True
    
    def _handle_posture_data(self, data):
        """处理姿势数据"""
        try:
            posture_info = json.loads(data.decode('utf-8'))
            print(f"收到姿势数据: {posture_info}")
            # 可以在这里添加其他处理逻辑
        except Exception as e:
            print(f"解析姿势数据失败: {e}")
    
    def _handle_emotion_data(self, data):
        """处理情绪数据"""
        try:
            emotion_info = json.loads(data.decode('utf-8'))
            print(f"收到情绪数据: {emotion_info}")
            # 可以在这里添加其他处理逻辑
        except Exception as e:
            print(f"解析情绪数据失败: {e}")
    
    def _handle_warning(self, data):
        """处理警告信息"""
        try:
            warning_info = json.loads(data.decode('utf-8'))
            print(f"收到警告信息: {warning_info}")
            # 可以在这里添加其他处理逻辑
        except Exception as e:
            print(f"解析警告信息失败: {e}")
    
    def _handle_config(self, data):
        """处理配置信息"""
        try:
            config_info = json.loads(data.decode('utf-8'))
            print(f"收到配置信息: {config_info}")
            # 可以在这里添加其他处理逻辑
        except Exception as e:
            print(f"解析配置信息失败: {e}")
    
    def get_status(self):
        """获取设备状态"""
        return {
            'connected': self.device_status['connected'],
            'last_error': self.device_status['last_error'],
            'last_heartbeat': self.last_heartbeat
        }