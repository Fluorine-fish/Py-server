import sys
import os
import time

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'Audio'))

# 导入必要的模块
import pyaudio
import dashscope
from dashscope.audio.asr import *
from dashscope.audio.tts_v2 import *
from http import HTTPStatus
import json
from datetime import datetime
from Audio.Snowboy import snowboydecoder
from modules.Lampbot_manager import Lampbot_Instance

# 在文件开头添加串口模块导入
from serial_handler import SerialHandler
from config import (SERIAL_BAUDRATE, 
                    CHATBOT_MODULE,
                    TIME_OUT,
                    AUTO_RETURN,
                    MODULE_SENSITY,
                    ENABLE_WELCOME_MESSAGE)


# 修改后的Agent类定义 (直接将声明代码复制过来)
class Agent:
    asr_model = "gummy-chat-v1"  # asr模型名称
    tts_model = "cosyvoice-v1"  # tts模型名称
    tts_voice = "longxiaochun"  # tts语音名称
    assistant_model = CHATBOT_MODULE  # 大模型名称

    assistant = None  # 大模型助手
    thread = None  # 线程
    tools = None  # 工具列表

    class TTSCallback(ResultCallback):
        _player = None
        _stream = None

        def on_open(self):
            self._player = pyaudio.PyAudio()
            self._stream = self._player.open(
                format=pyaudio.paInt16, channels=1, rate=22050, output=True
            )

        def on_close(self):
            # stop player
            self._stream.stop_stream()
            self._stream.close()
            self._player.terminate()

        def on_data(self, data: bytes) -> None:
            self._stream.write(data)  # 往音频设备中写入数据,即播放音频

    class ASRCallback(TranslationRecognizerCallback):
        _mic = None
        _stream = None
        asr_result = None

        def on_open(self) -> None:
            self._mic = pyaudio.PyAudio()
            self._stream = self._mic.open(
                format=pyaudio.paInt16, channels=1, rate=16000, input=True
            )

        def on_close(self) -> None:
            self._stream.stop_stream()
            self._stream.close()
            self._mic.terminate()
            self._stream = None
            self._mic = None

        def on_event(
            self,
            request_id,
            transcription_result: TranscriptionResult,
            translation_result: TranslationResult,
            usage,
        ) -> None:
            if transcription_result is not None:
                if transcription_result.is_sentence_end:
                    self.asr_result = transcription_result.text

    def __init__(self, instructions: str, tools_json_path: str):
        # 从json中加载预设tools
        with open(tools_json_path, "r", encoding="utf-8") as tools_file:
            self.tools = json.load(tools_file)

        # 创建助手
        self.assistant = dashscope.Assistants.create(
            model=self.assistant_model,  # 大语言模型名，用于为智能体配置大模型
            name='"瞳灵"台灯智能体',  # 智能体名称，用于区别智能体的名称
            description='"瞳灵"台灯智能体,用于进行语音交互',  # 智能体的功能描述
            instructions=instructions,  # 由自然语言构成的指令，用于定义智能体的角色和任务
            tools=self.tools,  # 为智能体配置的工具列表
        )
        # 检测助手创建是否成功
        if not self.__check_status(self.assistant, "助手创建"):
            exit()
        # 创建助手的线程
        self.thread = dashscope.Threads.create()
        # 检测线程创建是否成功
        if not self.__check_status(self.thread, "线程创建"):
            exit()

    def __check_status(self, component, operation):
        if component.status_code == HTTPStatus.OK:
            print(f"{operation} 成功。")
            return True
        else:
            print(
                f"{operation} 失败。状态码：{component.status_code}，错误码：{component.code}，错误信息：{component.message}"
            )
            return False

    def get_message(self):
        # 创建语音识别回调函数
        asr_callback = self.ASRCallback()
        # 创建语音识别模型对象
        translator = TranslationRecognizerChat(
            model="gummy-chat-v1",
            format="pcm",
            sample_rate=16000,
            transcription_enabled=True,
            callback=asr_callback,
            max_end_silence=1000,  # 设置最大结束静音时长,单位为毫秒(ms),若语音结束后静音时长超过该预设值,系统将判定当前语句已结束
        )
        translator.start()
        message = ""
        while True:
            if asr_callback._stream:
                data = asr_callback._stream.read(3200, exception_on_overflow=False)
                if not translator.send_audio_frame(data):
                    message = asr_callback.asr_result
                    break
            else:
                break
        translator.stop()
        return message

    def send_message(self, messages: str):
        if messages == "":
            return
        # 向线程发送消息
        message = dashscope.Messages.create(self.thread.id, content=messages)
        # 检测消息创建是否成功
        if not self.__check_status(message, "消息创建"):
            exit()

        # 向助手发送消息
        run = dashscope.Runs.create(
            self.thread.id, assistant_id=self.assistant.id, stream=True  # 开启流式输出
        )

        # 创建tts合成器并启动
        tts_callback = self.TTSCallback()
        synthesizer = SpeechSynthesizer(
            model=self.tts_model,
            voice=self.tts_voice,
            format=AudioFormat.PCM_22050HZ_MONO_16BIT,
            callback=tts_callback,
        )

        while True:  # 添加外层循环
            for event, data in run:  # 事件流和事件数据的详细信息
                if event == "thread.run.requires_action":  # Assistant 调用了工具，正在等待函数输出
                    tool_outputs = []  # 提交输出的方法与第五步类似
                    for tool in data.required_action.submit_tool_outputs.tool_calls:
                        name = tool.function.name
                        args = json.loads(tool.function.arguments)
                        output = tools_map[name](**args)
                        tool_outputs.append(
                            {
                                "tool_call_id": tool.id,
                                "output": output,
                            }
                        )
                    run = dashscope.Runs.submit_tool_outputs(  # 提交函数输出
                        thread_id=self.thread.id,
                        run_id=data.id,
                        tool_outputs=tool_outputs,
                        stream=True,  # 此处也需要开启流式输出
                    )
                    break  # 跳出当前的 for 循环，下一次循环将轮询新的 Runs 对象。
                elif event == "thread.message.delta":
                    print(data.delta.content.text.value, end="", flush=True)
                    # 只有在synthesizer可用时才进行语音合成
                    if synthesizer:
                        try:
                            synthesizer.streaming_call(data.delta.content.text.value)
                        except Exception as e:
                            print(f"语音合成出错: {e}")
            else:
                break  # 如果首轮 for 循环正常结束（没有触发函数调用），就直接退出 while 循环

        # 完成语音合成
        if synthesizer:
            try:
                synthesizer.streaming_complete()
            except Exception as e:
                print(f"完成语音合成时出错: {e}")
        messages = dashscope.Messages.list(self.thread.id)
        if self.__check_status(messages, "消息检索"):
            if messages.data:
                # 显示最后一条消息的内容（助手的响应）
                last_message = messages.data[0]
                return last_message["content"][0]["text"]["value"]
                
    def reset(self):
        # 创建助手的线程
        self.thread = dashscope.Threads.create()
        # 检测线程创建是否成功
        if not self.__check_status(self.thread, "线程创建"):
            exit()
            
    def speak_text(self, text):
        """仅使用TTS朗读指定文本，不进行对话"""
        if not text:
            return False
            
        # 创建tts合成器
        tts_callback = self.TTSCallback()
        synthesizer = SpeechSynthesizer(
            model=self.tts_model,
            voice=self.tts_voice,
            format=AudioFormat.PCM_22050HZ_MONO_16BIT,
            callback=tts_callback,
        )

        synthesizer.streaming_call(text)
        synthesizer.streaming_complete()
    
class ChatbotService:
    """语音助手服务，用于语音交互"""

    def __init__(self):
        try:
            with open("Audio/config.json", "r", encoding="utf-8") as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            # 尝试使用绝对路径
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(base_path, "Audio/config.json"), "r", encoding="utf-8") as config_file:
                self.config = json.load(config_file)
                
        self.instructions = self.config["instructions"]
        dashscope.api_key = self.config["api_key"]
        
        # 构建绝对路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tools_path = os.path.join(base_path, "Audio/tools.json")

        self.loop_cnt = 0  # 用于计数对话次数
        
        # # 初始化串口处理器
        # try:
        #     self.serial_handler = SerialHandler(baudrate=SERIAL_BAUDRATE)
        #     self.serial_available = (self.serial_handler is not None and 
        #                            hasattr(self.serial_handler, 'initialized'))
        #     print(f"串口通信初始化: {'成功' if self.serial_available else '失败'}")
        # except Exception as e:
        #     print(f"串口通信初始化失败: {str(e)}")
        #     self.serial_handler = None
        #     self.serial_available = False
        
        try:
            self.lampbot = Lampbot_Instance()
        except Exception as e:
            self.lampbot = None
            print(f"Lampbot实例初始化失败: {str(e)}")

        self.my_agent = Agent(
            instructions=self.instructions,
            tools_json_path=tools_path,
        )

        # 关键词模型路径 - 使用绝对路径
        self.kws_models = [
            os.path.join(base_path, "Snowboy/resources/models/snowboy.umdl"),
            os.path.join(base_path, "Snowboy/resources/models/computer.umdl"),
        ]

        self.lampbot.lamp_status = {}
        self.lampbot.lamp_status['power'] = True
        self.lampbot.lamp_status['brightness'] = 500
        self.lampbot.lamp_status['color_temp'] = 5300


    def initialize(self):
        """初始化语音助手"""
        print("语音助手初始化完成")
        return True

    def send_message(self, message):
        """发送消息并获取响应"""
        if not message:
            return "请提供有效的消息内容。"
        
        response = self.my_agent.send_message(message)
        if response:
            print(f"==>助手响应：{response}<==")
        else:
            print("==>助手未能生成响应<==")
        return response

    def chat_loop(self):
        """进入包含语音识别的交互"""

        kws_models = ["Audio/Snowboy/resources/models/lampbot.pmdl"]

        detector = snowboydecoder.HotwordDetector(kws_models, sensitivity=MODULE_SENSITY)

        key = input() #等待输入s
        if key == 's':
            # 发送欢迎消息，获取自我介绍
            if ENABLE_WELCOME_MESSAGE and self.loop_cnt == 0:
                try:
                    print("正在请求语音助手自我介绍...")
                    # msg = "你好，请简要介绍一下自己的功能，不要举例,不要使用\"嗨\",不要提到自己机械臂的功能。并且告诉用户，用“你好小灵”来唤醒你"
                    # response = chatbot_service.send_message(msg)
                    self.speak_text("你好！我是瞳灵智能台灯，我能开关灯光、调节亮度，让房间变亮或者变暗哦！还能控制机械臂把光照到你需要的地方呢！")
                except Exception as e:
                    print(f"语音助手自我介绍时出错: {str(e)}")
            # print("正在监听唤醒词... 按 Ctrl+C 退出")
            # detector.start(sleep_time=0.03, stop_on_detect=True)
            # detector.terminate()
            # print("唤醒词被检测到，开始语音识别...")
            # msg = "你好，小灵"
            # self.send_message(msg) # 语音识别成功的交互

            start_time = datetime.now()
            timeout_seconds = TIME_OUT

            for i in range(50): #允许最多30次对话，对话之后进入休眠
                current_time = datetime.now()
                elapsed_time = (current_time - start_time).total_seconds()
                
                # if elapsed_time >= timeout_seconds:
                #     print(f"==>对话超时({timeout_seconds}秒)，助手将进入休眠状态<==")
                #     break

                sentence = self.my_agent.get_message()

                # if ("休息" in sentence or "结束" in sentence or "退出" in sentence) and AUTO_RETURN:
                #     print("==>检测到结束语，助手将进入休眠状态<==")
                #     break
                print(f"==>识别结果：{sentence}<==")
                self.my_agent.send_message(sentence)

            # msg = "小灵先休息啦，有事情可以随时叫我哦！"
            # self.my_agent.speak_text(msg)
            # print("==>对话结束，助手进入休眠状态<==")
            self.loop_cnt += 1

    def reset(self):
        """重置对话上下文"""
        self.my_agent.reset()
        return True
        
    def speak_text(self, text):
        """朗读指定文本，无需进行对话"""
        return self.my_agent.speak_text(text)
    


# 全局变量用于存储聊天机器人实例
_chatbot_instance = None

def get_chatbot_instance():
    """获取聊天机器人实例"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ChatbotService()
    return _chatbot_instance

# 修改后的工具函数，支持串口通信
def light_on():
    """打开灯光"""
    print("==>打开灯光<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你开灯哦！"
        chatbot.speak_text(msg)  # 朗读开灯提示
        chatbot.lampbot.light_on()  # 调用Lampbot实例的开灯方法
    except Exception as e:
        print(f"发送开灯命令时出错: {str(e)}")
        return "开灯命令执行出错，请检查串口连接"

def light_off():
    """关闭灯光"""
    print("==>关闭灯光<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你关灯哦！"
        chatbot.speak_text(msg)  # 朗读关灯提示
        chatbot.lampbot.light_off()  # 调用Lampbot实例的关灯方法   
    except Exception as e:
        print(f"发送关灯命令时出错: {str(e)}")
        return "关灯命令执行出错，请检查串口连接"

def light_brighter():
    """调高灯光亮度"""
    print("==>调高灯光亮度<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你调整一下哦！"
        chatbot.speak_text(msg) 
        chatbot.lampbot.light_brighter()
    except Exception as e:
        print(f"发送调高亮度命令时出错: {str(e)}")
        return "调高亮度命令执行出错，请检查串口连接"

def light_dimmer():
    """调低灯光亮度"""
    print("==>调低灯光亮度<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你调整一下哦！"
        chatbot.speak_text(msg)
        chatbot.lampbot.light_dimmer();
    except Exception as e:
        print(f"发送调低亮度命令时出错: {str(e)}")
        return "调低亮度命令执行出错，请检查串口连接"

def color_temperature_up():
    """提升光照色温"""
    print("==>提升光照色温<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你调整一下哦！"
        chatbot.speak_text(msg)
        chatbot.lampbot.color_temperature_up()
    except Exception as e:
        print(f"发送提升色温命令时出错: {str(e)}")
        return "提升色温命令执行出错，请检查串口连接"

def color_temperature_down():
    """降低光照色温"""
    print("==>降低光照色温<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你调整一下哦！"
        chatbot.speak_text(msg)
        chatbot.lampbot.color_temperature_down()
    except Exception as e:
        print(f"发送降低色温命令时出错: {str(e)}")
        return "降低色温命令执行出错，请检查串口连接"

def posture_reminder():
    """进行坐姿提醒"""
    print("==>进行坐姿提醒<==")
    chatbot = get_chatbot_instance()
    try:
        chatbot.lampbot.posture_reminder()
    except Exception as e:
        print(f"发送坐姿提醒命令时出错: {str(e)}")
        return "坐姿提醒命令执行出错，请检查串口连接"

def reading_mode():
    """进行阅读模式"""
    print("==>进行阅读模式<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你打开阅读模式哦！"
        chatbot.speak_text(msg)
        chatbot.lampbot.reading_mode()
    except Exception as e:
        print(f"发送阅读模式命令时出错: {str(e)}")
        return "阅读模式命令执行出错，请检查串口连接"

def learning_mode():
    """进行学习模式"""
    print("==>进行学习模式<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你打开学习模式哦！"
        chatbot.speak_text(msg)
        chatbot.lampbot.learning_mode()
    except Exception as e:
        print(f"发送进行学习模式命令时出错: {str(e)}")
        return "进行学习模式命令执行出错，请检查串口连接"
    
def vision_reminder():
    """进行远眺提醒"""
    print("==>进行远眺提醒<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "不如稍微休息一下，远眺一下哦！"
        chatbot.speak_text(msg)
        # 使用serial_module中的send_command方法
        chatbot.lampbot.vision_reminder()
    except Exception as e:
        print(f"发送远眺提醒命令时出错: {str(e)}")
        return "远眺提醒命令执行出错，请检查串口连接"

def get_status():
    """获取台灯状态"""
    print("==>获取台灯状态<==")
    chatbot = get_chatbot_instance()
    try:
        msg = "稍等我帮你看看哦！"
        chatbot.speak_text(msg)  # 朗读获取状态提示
        result = chatbot.lampbot.update_status()  # 调用Lampbot实例的获取状态方法
        if result is None:
            return "获取台灯状态失败，请检查串口连接"
        
        # 打印当前状态
        print(f"当前台灯状态: {result}")
        return result
    except Exception as e:
        chatbot.logger.error(f"获取台灯状态失败: {e}")
        return None

def arm_forward():
    """机械臂向前移动"""
    print("==>机械臂向前移动<==")
    chatbot = get_chatbot_instance()
    try:
        # msg = "稍等我帮你调整一下哦！"
        # chatbot.speak_text(msg)
        chatbot.lampbot.arm_forward() # 调用Lampbot实例的机械臂向前移动方法
    except Exception as e:
        print(f"发送机械臂向前移动命令时出错: {str(e)}")
        return "机械臂向前移动命令执行出错，请检查串口连接"

def arm_backward():
    """机械臂向后移动"""
    print("==>机械臂向后移动<==")
    chatbot = get_chatbot_instance()
    try:
        # msg = "稍等我帮你调整一下哦！"
        # chatbot.speak_text(msg)
        chatbot.lampbot.arm_backward() # 调用Lampbot实例的机械臂向后移动方法
    except Exception as e:
        print(f"发送机械臂向后移动命令时出错: {str(e)}")
        return "机械臂向后移动命令执行出错，请检查串口连接"

def arm_left():
    """机械臂左转"""
    print("==>机械臂左转<==")
    chatbot = get_chatbot_instance()
    try:
        # msg = "稍等我帮你调整一下哦！"
        # chatbot.speak_text(msg)
        chatbot.lampbot.arm_left() # 调用Lampbot实例的机械臂左转方法
    except Exception as e:
        print(f"发送机械臂左转命令时出错: {str(e)}")
        return "机械臂左转命令执行出错，请检查串口连接"

def arm_right():
    """机械臂右转"""
    print("==>机械臂右转<==")
    chatbot = get_chatbot_instance()
    try:
        # msg = "稍等我帮你调整一下哦！"
        # chatbot.speak_text(msg)
        chatbot.lampbot.arm_right() # 调用Lampbot实例的机械臂右转方法
    except Exception as e:
        print(f"发送机械臂右转命令时出错: {str(e)}")
        return "机械臂右转命令执行出错，请检查串口连接"

# 更新工具函数映射
tools_map = {
    "light_on": light_on,
    "light_off": light_off,
    "light_brighter": light_brighter,
    "light_dimmer": light_dimmer,
    "color_temperature_up": color_temperature_up,
    "color_temperature_down": color_temperature_down,
    "posture_reminder": posture_reminder,
    "vision_reminder": vision_reminder,
    "get_status": get_status,
    "arm_forward": arm_forward,
    "arm_backward": arm_backward,
    "arm_left": arm_right,
    "arm_right": arm_left,
    "reading_mode": reading_mode,
    "learning_mode": learning_mode,  
}


def main():
    chatbot = ChatbotService()
    _chatbot_instance = chatbot  # 将实例赋值给全局变量
    print("==>语音助手服务开始启动<==")
    chatbot.initialize()
    
    # # 朗读开场白
    chatbot.speak_text("小可爱，你好！我是瞳灵智能台灯，我能开关灯光、调节亮度，让房间变亮或者变暗哦！还能控制机械臂把光照到你需要的地方呢，有什么需要就告诉我吧！")
    time.sleep(2)

    # 随机生成的开场白
    # msg = "你好，请尽量简短地介绍一下自己的功能，控制在两句话以内，不要举例。"
    # chatbot.send_message(msg)
    # time.sleep(2)

    # 进入正常对话循环
    while True:
        chatbot.chat_loop()

if __name__ == "__main__":
    main()