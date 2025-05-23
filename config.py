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
DEBUG = False  # 设置为True开启调试模式，False关闭调试模式

# 串口配置
SERIAL_BAUDRATE = 115200

# 开放端口配置
# OPEN_HOST = '192.168.67.10'
OPEN_HOST = '127.0.0.1'
OPEN_PORT = 5001  # 修改为5001端口避免冲突