import os,sys,time
import multiprocessing as mp
from multiprocessing.synchronize import Event as MpEvent
from multiprocessing.queues import Queue as MpQueue
import threading
from queue import Empty

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

# 在模块顶层新增：进程里的 tick 循环（只发信号，不直接操作串口）
def _tick_loop(stop_event: MpEvent, q: MpQueue, interval_sec: int = 10):
    import time as _t
    while not stop_event.is_set():
        try:
            # 非阻塞推送一个心跳，队列满就跳过，避免堆积
            q.put_nowait(_t.time())
        except Exception:
            pass
        stop_event.wait(interval_sec)

class Lampbot_Instance:
    def __init__(self):
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

        # 线程锁，确保串口访问互斥
        self._serial_lock = threading.Lock()

        # 台灯状态
        self.lamp_status = {
            'power': True,
            'brightness': 500,
            'color_temp': 5300,
            'last_update': datetime.now().isoformat()
        }

        # 启动“进程 + 监听线程”
        self._stop_event = mp.Event()
        self._tick_q = mp.Queue(maxsize=8)
        self._tick_proc = mp.Process(
            target=_tick_loop,
            args=(self._stop_event, self._tick_q, 10),  # 每10秒
            daemon=True
        )
        self._tick_proc.start()

        self._listener_thread = threading.Thread(
            target=self._listen_ticks, daemon=True
        )
        self._listener_thread.start()

    # 监听子进程心跳并触发更新（仍在主进程，安全访问串口）
    def _listen_ticks(self):
        while not self._stop_event.is_set():
            try:
                _ = self._tick_q.get(timeout=1.0)
            except Empty:
                continue
            try:
                self.update_status()
            except Exception as e:
                print(f"后台更新失败: {e}")

    # 安全发送串口命令
    def _safe_send_command(self, cmd: int, payload):
        if not self.serial_handler:
            print("串口未初始化")
            return False
        with self._serial_lock:
            return self.serial_handler.send_command(cmd, payload)

    def close(self, timeout: float = 2.0):
        # 优雅关闭进程与线程
        try:
            self._stop_event.set()
        except Exception:
            pass
        try:
            if hasattr(self, '_tick_proc') and self._tick_proc.is_alive():
                self._tick_proc.join(timeout)
                if self._tick_proc.is_alive():
                    self._tick_proc.kill()
        except Exception:
            pass
        try:
            if hasattr(self, '_listener_thread') and self._listener_thread.is_alive():
                self._listener_thread.join(timeout)
        except Exception:
            pass
        try:
            if hasattr(self, '_tick_q'):
                self._tick_q.close()
        except Exception:
            pass

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def update_status(self):
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
        return result

    def light_on(self):
        res = self._safe_send_command(0x14, [0] * 8)
        if res:
            print("串口命令发送成功: 开灯")
            self.lamp_status['power'] = True
            return "success"
        else:
            print("串口命令发送失败: 开灯")
            return "串口命令发送失败，未执行开灯操作"

    def light_off(self):
        res = self._safe_send_command(0x15, [1] * 8)
        if res:
            print("串口命令发送成功: 关灯")
            self.lamp_status['power'] = False
            return "success"
        else:
            print("串口命令发送失败: 关灯")
            return "串口命令发送失败，未执行开灯操作"

    def light_brighter(self):
        success = self._safe_send_command(0x10, [0] * 8)
        if success:
            print("串口命令发送成功: 调高灯光亮度")
            return "success"
        else:
            print("串口命令发送失败: 调高灯光亮度")
            return "串口命令发送失败，未执行调高灯光亮度操作"
        
    def light_dimmer(self):
        success = self._safe_send_command(0x11, [0] * 8)
        if success:
            print("串口命令发送成功: 调低灯光亮度")
            return "success"
        else:
            print("串口命令发送失败: 调低灯光亮度")
            return "串口命令发送失败，未执行调低灯光亮度操作"     

    def color_temperature_up(self):
        success = self._safe_send_command(0x12, [0] * 8)
        if success:
            print("串口命令发送成功: 提升光照色温")
            return "success"
        else:
            print("串口命令发送失败: 提升光照色温")
            return "串口命令发送失败，未执行提升光照色温操作"
        
    def color_temperature_down(self):
        success = self._safe_send_command(0x13, [0] * 8)
        if success:
            print("串口命令发送成功: 降低光照色温")
            return "success"
        else:
            print("串口命令发送失败: 降低光照色温")
            return "串口命令发送失败，未执行降低光照色温操作"  
            
    def posture_reminder(self):
        success = self._safe_send_command(0x20, [0] * 8)
        if success:
            print("串口命令发送成功: 坐姿提醒")
            return "success"
        else:
            print("串口命令发送失败: 坐姿提醒")
            return "串口命令发送失败，未执行坐姿提醒操作"      

    def reading_mode(self):
        success = self._safe_send_command(0x50, [0] * 8)
        if success:
            print("串口命令发送成功: 阅读模式")
            return "success"
        else:
            print("串口命令发送失败: 阅读模式")
            return "串口命令发送失败，未执行阅读模式操作"

    def learning_mode(self):
        success = self._safe_send_command(0x51, [0] * 8)
        if success:
            print("串口命令发送成功: 进行学习模式")
            return "success"
        else:
            print("串口命令发送失败: 进行学习模式")
            return "串口命令发送失败，未执行进行学习模式操作"

    def vision_reminder(self):
        success = self._safe_send_command(0x21, [0] * 8)
        if success:
            print("串口命令发送成功: 远眺提醒")
            return "success"
        else:
            print("串口命令发送失败: 远眺提醒")
            return "串口命令发送失败，未执行远眺提醒操作"
        
    def arm_forward(self):
        success = self._safe_send_command(0x30, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂向前移动")
            return "success"
        else:
            print("串口命令发送失败: 机械臂向前移动")
            return "串口命令发送失败，未执行机械臂向前移动操作"
    
    def arm_backward(self):
        success = self._safe_send_command(0x31, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂向后移动")
            return "success"
        else:
            print("串口命令发送失败: 机械臂向后移动")
            return "串口命令发送失败，未执行机械臂向后移动操作"

    def arm_right(self):
        success = self._safe_send_command(0x33, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂右转")
            return "success"
        else:
            print("串口命令发送失败: 机械臂右转")
            return "串口命令发送失败，未执行机械臂右转操作"        
        
    def arm_left(self):
        success = self._safe_send_command(0x32, [0] * 8)
        if success:
            print("串口命令发送成功: 机械臂左转")
            return "success"
        else:
            print("串口命令发送失败: 机械臂左转")
            return "串口命令发送失败，未执行机械臂左转操作"