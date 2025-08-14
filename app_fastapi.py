"""
应用主模块 - 系统入口点，使用FastAPI替换原Flask服务
"""
import os
import atexit
import time
import threading
import traceback

# 导入配置
from config import (OPEN_HOST, OPEN_PORT, SERIAL_BAUDRATE, DEBUG_BUTTON_VISIBLE, 
                   ENABLE_CHATBOT, ENABLE_WELCOME_MESSAGE, AUTO_START_CHATBOT_LOOP)

# 导入各个功能模块
from modules.database_module import init_database
from modules.video_stream_module import VideoStreamHandler
from modules.posture_module import WebPostureMonitor, PROCESS_WIDTH, PROCESS_HEIGHT
from modules.serial_module import SerialCommunicationHandler
from modules.chatbot_module import ChatbotService

# 可选导入DetectionService
try:
    from modules.detection_module import DetectionService
except ImportError as e:
    print(f"警告：检测模块导入失败，跳过检测服务初始化: {e}")
    DetectionService = None

# WebServer（FastAPI）
from webserver.context import AppContext
from webserver.server import WebServer

def create_services_context() -> AppContext:
    """创建服务上下文"""
    print("\n========== 开始初始化服务 ==========")
    
    # 初始化数据库
    init_database()
    print("数据库初始化完成")
    
    # 初始化视频流处理器
    video_stream_handler = None
    try:
        print("正在初始化视频流处理器...")
        video_stream_handler = VideoStreamHandler(
            process_width=PROCESS_WIDTH,
            process_height=PROCESS_HEIGHT
        )
        print("视频流处理器初始化成功")
    except Exception as e:
        print(f"视频流处理器初始化失败: {str(e)}")
        traceback.print_exc()
    
    # 初始化姿势分析器
    posture_monitor = None
    try:
        print("正在初始化姿势分析器...")
        posture_monitor = WebPostureMonitor(video_stream_handler=video_stream_handler)
        print("姿势分析器初始化成功")
    except Exception as e:
        print(f"姿势分析器初始化失败: {str(e)}")
        traceback.print_exc()
    
    # 自动启动姿势分析系统
    posture_start_success = False
    if posture_monitor:
        try:
            print("正在启动姿势分析系统...")
            posture_start_success = posture_monitor.start()
            if posture_start_success:
                print("姿势分析系统自动启动成功")
            else:
                print("警告：姿势分析系统自动启动失败，请手动启动")
        except Exception as e:
            print(f"启动姿势分析系统时出错: {str(e)}")
            traceback.print_exc()
    else:
        print("姿势分析器未成功初始化，无法启动姿势分析系统")

    # 尝试初始化串口通信处理器，允许失败
    serial_handler = None
    serial_available = False
    try:
        serial_handler = SerialCommunicationHandler(baudrate=SERIAL_BAUDRATE)
        serial_available = serial_handler is not None and hasattr(serial_handler, 'initialized') and serial_handler.initialized
    except Exception as e:
        print(f"串口通信初始化失败，但不影响其他系统: {str(e)}")
    
    if serial_available:
        print("串口通信系统初始化成功")
    else:
        print("串口通信系统未启动，但其他系统可以正常工作")

    # 初始化检测服务 (如果可用的话)
    detection_service = None
    detection_available = False
    if DetectionService is not None:
        try:
            print("正在初始化检测服务...")
            # detection_service = DetectionService(...)
            # 目前暂不初始化，预留接口
            detection_available = False
            print("检测服务预留但未激活")
        except Exception as e:
            print(f"检测服务初始化失败: {str(e)}")
            detection_service = None
            detection_available = False
    else:
        print("检测服务模块不可用，跳过初始化")

    # 初始化语音助手服务
    chatbot_service = None
    if ENABLE_CHATBOT:
        try:
            print("正在初始化语音助手服务...")
            chatbot_service = ChatbotService()
            if chatbot_service.initialize():
                print("语音助手服务初始化成功")
                if ENABLE_WELCOME_MESSAGE:
                    try:
                        welcome_msg = "你好！我是瞳灵智能台灯，我能开关灯光、调节亮度，让房间变亮或者变暗哦！还能控制机械臂把光照到你需要的地方呢！"
                        chatbot_service.speak_text(welcome_msg)
                        print("欢迎消息播放成功")
                    except Exception as e:
                        print(f"欢迎消息播放失败: {str(e)}")
            else:
                print("语音助手服务初始化失败")
                chatbot_service = None
        except Exception as e:
            print(f"初始化语音助手服务时出错: {str(e)}")
            traceback.print_exc()
            chatbot_service = None

    # 创建应用上下文
    ctx = AppContext(
        posture_monitor=posture_monitor,
        video_stream=video_stream_handler,
        serial_handler=serial_handler,
        chatbot=chatbot_service,
        detection_service=detection_service
    )

    # 初始化指标数据
    ctx.update_metrics(
        online=True,
        charging=False,
        battery_level=100,
        last_seen=time.time(),
        posture_start_success=posture_start_success,
        serial_available=serial_available,
        detection_available=detection_available
    )

    # 如果启用了语音助手并设置为自动启动对话循环，则在单独的线程中启动
    if chatbot_service and AUTO_START_CHATBOT_LOOP:
        def chatbot_loop():
            print("语音助手对话循环已启动，随时准备接收语音指令...")
            try:
                while True:
                    try:
                        chatbot_service.chat_loop()
                    except Exception as e:
                        print(f"语音助手对话循环出错: {str(e)}")
                        time.sleep(2)  # 出错后等待2秒再重试
            except KeyboardInterrupt:
                print("语音助手对话循环被终止")
        
        # 创建并启动语音助手线程
        chatbot_thread = threading.Thread(target=chatbot_loop, daemon=True)
        chatbot_thread.start()
        print("语音助手线程已启动")

    # 注册应用退出时的清理函数
    def cleanup():
        print("正在关闭服务器...")
        if ctx.posture_monitor:
            try:
                ctx.posture_monitor.stop()
                print("姿势监控服务已停止")
            except Exception as e:
                print(f"停止姿势监控服务时出错: {e}")
        
        if ctx.serial_handler and serial_available:
            try:
                ctx.serial_handler.cleanup()
                print("串口通信服务已关闭")
            except Exception as e:
                print(f"关闭串口通信服务时出错: {e}")
        
        if ctx.chatbot:
            print("正在关闭语音助手服务...")
            try:
                ctx.chatbot.reset()
                print("语音助手服务已关闭")
            except Exception as e:
                print(f"关闭语音助手服务时出错: {e}")
        
        print("所有服务已关闭")
    
    atexit.register(cleanup)
    
    return ctx

def main():
    """主入口函数"""
    print("========== Py-server 启动 (FastAPI) ==========")
    
    # 创建服务上下文
    ctx = create_services_context()
    
    # 创建并启动WebServer
    webserver = WebServer(ctx=ctx, include_mock=True)
    
    print(f"\n========== 启动Web服务器 ==========")
    print(f"服务器地址: http://{OPEN_HOST}:{OPEN_PORT}")
    print(f"API文档: http://{OPEN_HOST}:{OPEN_PORT}/docs")
    print(f"视频流: http://{OPEN_HOST}:{OPEN_PORT}/api/video")
    print(f"健康检查: http://{OPEN_HOST}:{OPEN_PORT}/api/health")
    print("========================================")
    
    try:
        webserver.run(host=OPEN_HOST, port=OPEN_PORT, reload=False)
    except KeyboardInterrupt:
        print("\n收到键盘中断，正在关闭服务器...")
    except Exception as e:
        print(f"服务器运行出错: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
