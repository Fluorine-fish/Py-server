# 串口配置
SERIAL_PORTS = [
    '/dev/ttyUSB0',
    '/dev/ttyUSB1',
    '/dev/ttyACM0',
    '/dev/ttyACM1'
]
SERIAL_BAUDRATE = 115200

# MySQL配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'serial_user',
    'password': 'Serial123!',  # 使用你设置的密码
    'database': 'serial_data'
}

# 调试配置
DEBUG = True  # 设置为True开启调试模式，False关闭调试模式
DEBUG_BUTTON_VISIBLE = True  # 控制main.html中调试按钮的显示

# 语音助手配置
ENABLE_CHATBOT = True  # 是否启用语音助手
ENABLE_WELCOME_MESSAGE = True  # 是否启用欢迎消息
AUTO_START_CHATBOT_LOOP = True  # 是否自动启动语音助手对话循环

#尽量不要使用QWEN3以后版本模型：
# CHATBOT_MODULE = "qwen-plus-2025-04-28" # 千问plus 4.28的快照目前仍有问题
#QWEN3版本以前的模型：
# CHATBOT_MODULE = "qwen-plus-2025-01-25" # 千问plus 1.25的快照 目前没有问题（测试较少）
CHATBOT_MODULE = "qwen-turbo-2025-02-11" # 千问turbo 2.11的快照 前没有问题（测试较少）
TIME_OUT =  500 # 语音助手对话超时时间，单位为秒
AUTO_RETURN = False # 语音助手是否可以听到结束语后就退出
MODULE_SENSITY = 0.83 #语音唤醒词的敏感度

# 开放端口配置
# 使用0.0.0.0表示监听所有可用网络接口，允许任何IP地址连接
OPEN_HOST = '0.0.0.0'
OPEN_PORT = 5100  # 修改为5050端口避免端口冲突

#坐姿检测的阈值配置
EXCELENT_POSTURE_THRESHOLD = 45.0  # 优秀坐姿的阈值
GOOD_POSTURE_THRESHOLD = 58.0  # 良好坐姿的阈值
FAIR_POSTURE_THRESHOLD = 68.0  # 一般坐姿的阈值
BAD_POSTURE_THRESHOLD = 75.0  # 不良坐姿的阈值
