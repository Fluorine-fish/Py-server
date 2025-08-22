import os,sys,time
import threading

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'Audio'))

# 导入必要的模块
from datetime import datetime

# 在文件开头添加串口模块导入
from serial_handler import SerialHandler
from config import (SERIAL_BAUDRATE)

_lampbot_instance = None

def get_lampbot_instance():
    global _lampbot_instance
    if _lampbot_instance is None:
        _lampbot_instance = LampbotService()
    return _lampbot_instance

class LampbotService:
    def __init__(self, *args, **kwargs):
        # 初始化路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        audio_dir = os.path.join(parent_dir, 'Audio')
        if audio_dir not in sys.path:
            sys.path.append(audio_dir)

        # 初始化串口处理器
        try:
            self.serial_handler = SerialHandler(baudrate=SERIAL_BAUDRATE)
            self.serial_available = (self.serial_handler is not None and 
                                     hasattr(self.serial_handler, 'initialized'))
            print(f"串口通信初始化: {'成功' if self.serial_available else '失败'}")
        except Exception as e:
            print(f"串口通信初始化失败: {str(e)}")
            self.serial_handler = None
            self.serial_available = False

        # 台灯状态
        self.lamp_status = {
            'power': True,
            'brightness': 500,
            'color_temp': 5300,
            'last_update': datetime.now().isoformat()
        }

        self.avilable = True # 用于标记全局实例当前是否没有执行任务，避免多线程出现冲突
        self._serial_lock = threading.RLock()  # 确保始终存在
        # 如果有 available/avilable 命名不一致，也做个兼容
        if not hasattr(self, 'available') and hasattr(self, 'avilable'):
            self.available = self.avilable
        if not hasattr(self, 'avilable') and hasattr(self, 'available'):
            self.avilable = self.available

    def _safe_send_command(self, command, data_array=None):
        """带串口锁的安全发送命令，返回布尔表示是否发送成功"""
        if data_array is None:
            data_array = [0] * 7  # pack_frame 最多7个uint32

        if not getattr(self, 'serial_handler', None) or not getattr(self, 'serial_available', False):
            print("串口不可用，无法发送命令")
            return False

        try:
            with self._serial_lock:
                return bool(self.serial_handler.send_command(command, data_array))
        except Exception as e:
            print(f"发送命令 0x{command:02X} 出错: {e}")
            return False

    def update_status(self):
        self.avilable = False

        result = None
        if self.serial_handler:
            with self._serial_lock:
                data = self.serial_handler.request_data(0x40, [1] * 8)
            if data is None:
                print("无法从台灯获取状态数据")
                self.lamp_status['last_update'] = datetime.now().isoformat()
                return None
            else:
                if data.get('command') == 0xBF:
                    print("台灯未开机，不响应命令")
                    self.lamp_status['last_update'] = datetime.now().isoformat()
                    return None
                if data.get('datatype') != 0xB0:
                    print(f"未知数据类型: {data.get('datatype')}")
                    self.lamp_status['last_update'] = datetime.now().isoformat()
                    return None
                if data.get('command') != 0x41:
                    print(f"未知命令: {data.get('command')}")
                    self.lamp_status['last_update'] = datetime.now().isoformat()
                    return None

                if 'is_light' in data:
                    self.lamp_status['power'] = data['is_light']
                if 'brightness' in data:
                    self.lamp_status['brightness'] = data['brightness']
                if 'color_temp' in data:
                    self.lamp_status['color_temp'] = data['color_temp']

                result = f"成功获取台灯状态: 电源={self.lamp_status['power']}, 亮度={self.lamp_status['brightness']}, 色温={self.lamp_status['color_temp']}"
                print(result)

        self.lamp_status['last_update'] = datetime.now().isoformat()

        self.avilable = True
        return result

    def light_on(self):
        self.avilable = False

        res = self._safe_send_command(0x14, [0] * 8)
        if res:
            print("串口命令发送成功: 开灯")
            self.lamp_status['power'] = True

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 开灯")

            self.avilable = True
            return "串口命令发送失败，未执行开灯操作"
        

    def light_off(self):
        self.avilable = False

        res = self._safe_send_command(0x15, [1] * 8)
        if res:
            print("串口命令发送成功: 关灯")
            self.lamp_status['power'] = False

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 关灯")

            self.avilable = True
            return "串口命令发送失败，未执行开灯操作"

    def light_brighter(self):
        self.avilable = False

        success = self._safe_send_command(0x10, [0] * 8)
        if success:
            print("串口命令发送成功: 调高灯光亮度")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 调高灯光亮度")

            self.avilable = True
            return "串口命令发送失败，未执行调高灯光亮度操作"
        
    def light_dimmer(self):
        self.avilable = False

        success = self._safe_send_command(0x11, [0] * 8)
        if success:
            print("串口命令发送成功: 调低灯光亮度")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 调低灯光亮度")

            self.avilable = True
            return "串口命令发送失败，未执行调低灯光亮度操作"     

    def color_temperature_up(self):
        self.avilable = False

        success = self._safe_send_command(0x12, [0] * 8)
        if success:
            print("串口命令发送成功: 提升光照色温")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 提升光照色温")

            self.avilable = True
            return "串口命令发送失败，未执行提升光照色温操作"
        
    def color_temperature_down(self):
        self.avilable = False

        success = self._safe_send_command(0x13, [0] * 8)
        if success:
            print("串口命令发送成功: 降低光照色温")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 降低光照色温")

            self.avilable = True
            return "串口命令发送失败，未执行降低光照色温操作"  
            
    def posture_reminder(self):
        self.avilable = False

        success = self._safe_send_command(0x20, [0] * 8)
        if success:
            print("串口命令发送成功: 坐姿提醒")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 坐姿提醒")

            self.avilable = True
            return "串口命令发送失败，未执行坐姿提醒操作"      

    def reading_mode(self):
        self.avilable = False

        success = self._safe_send_command(0x50, [0] * 8)
        if success:
            print("串口命令发送成功: 阅读模式")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 阅读模式")

            self.avilable = True
            return "串口命令发送失败，未执行阅读模式操作"

    def learning_mode(self):
        self.avilable = False

        success = self._safe_send_command(0x51, [0] * 8)
        if success:
            print("串口命令发送成功: 进行学习模式")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 进行学习模式")

            self.avilable = True
            return "串口命令发送失败，未执行进行学习模式操作"

    def vision_reminder(self):
        self.avilable = False

        success = self._safe_send_command(0x21, [0] * 8)
        if success:
            print("串口命令发送成功: 远眺提醒")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 远眺提醒")

            self.avilable = True
            return "串口命令发送失败，未执行远眺提醒操作"
        
    def arm_forward(self):
        self.avilable = False

        success = self._safe_send_command(0x30, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂向前移动")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 机械臂向前移动")

            self.avilable = True
            return "串口命令发送失败，未执行机械臂向前移动操作"
    
    def arm_backward(self):
        self.avilable = False

        success = self._safe_send_command(0x31, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂向后移动")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 机械臂向后移动")

            self.avilable = True
            return "串口命令发送失败，未执行机械臂向后移动操作"

    def arm_right(self):
        self.avilable = False

        success = self._safe_send_command(0x33, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂右转")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 机械臂右转")

            self.avilable = True
            return "串口命令发送失败，未执行机械臂右转操作"        
        
    def arm_left(self):
        self.avilable = False

        success = self._safe_send_command(0x32, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂左转")

            self.avilable = True
            return "success"
        else:
            print("串口命令发送失败: 机械臂左转")

            self.avilable = True
            return "串口命令发送失败，未执行机械臂左转操作"

# ---- 全局单例访问器 ----
_lampbot_singleton = None

def get_lampbot_instance():
    """获取 Lampbot 全局单例实例。
    若不存在则创建，供 Web 接口与其他模块复用。
    """
    global _lampbot_singleton
    if _lampbot_singleton is None:
        _lampbot_singleton = Lampbot_Instance()
    return _lampbot_singleton