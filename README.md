# 儿童智能台灯管理系统

## 项目简介

这是一款基于视觉分析的儿童智能台灯管理系统的Web服务端。系统通过机械臂实现智能照明和姿势提醒功能，为儿童提供健康的学习环境，为家长提供全面的监控和管理功能。

### 主要功能

- 多关节姿势检测和分析
- 用眼距离监测
- 情绪识别和分析
- 久坐提醒
- 智能照明控制（3000-6500K）
- 数据统计和分析

## 系统要求

- Python 3.9+
- MySQL 5.7+
- OpenCV兼容的摄像头
- 串口设备（用于机械臂通信）

## 快速开始

### 安装

1. 克隆仓库：
```bash
git clone [repository-url]
cd Py-server
```

2. 创建虚拟环境：
```bash
conda env create -f environment.yml
conda activate smart-lamp
```

3. 配置环境：
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库和设备参数
```

## 功能特点 | Features

- 自动检测和连接串口设备 | Auto-detect and connect to serial devices
- Web 界面支持数据发送和接收 | Web interface for sending and receiving data
- 支持特定帧格式的通信 | Support for specific frame format communication
- 自动解析并显示接收到的帧数据 | Auto-parse and display received frame data
- 支持久坐提醒和坐姿提醒功能 | Support for sitting and posture reminders
- 为语音交互预留接口 | Reserved interface for voice interaction
- 历史记录管理和分页显示 | Historical record management with pagination
- MySQL 数据存储 | MySQL data storage
- 实时响应显示 | Real-time response display
- 支持清空历史记录 | Support clearing history records
- 基于Server-Sent Events的实时数据推送 | Real-time data push based on Server-Sent Events

## 系统要求 | Requirements

- Python 3.9+
- MySQL 数据库 | MySQL Database
- 串口设备 | Serial Device

## 安装步骤 | Installation

1. 克隆项目 | Clone the project
```bash
git clone <repository-url>
cd Py-server
```

2. 创建并激活虚拟环境 | Create and activate virtual environment
```bash
conda env create -f environment.yml
conda activate pyserver
```

或使用 pip | Or using pip:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. 配置数据库 | Configure Database

编辑 `config.py` 文件，设置数据库连接信息：
Edit `config.py` file to set database connection information:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'serial_data'
}
```

4. 创建数据库 | Create Database
```sql
CREATE DATABASE serial_data;
CREATE USER 'serial_user'@'localhost' IDENTIFIED BY 'Serial123!';
GRANT ALL PRIVILEGES ON serial_data.* TO 'serial_user'@'localhost';
FLUSH PRIVILEGES;
```

## 运行应用 | Running the Application

```bash
python server.py
```

服务器将在 http://127.0.0.1:5000 启动

The server will start at http://127.0.0.1:5000

## 使用说明 | Usage

1. 打开浏览器访问 http://127.0.0.1:5000
2. 选择操作模式：
   - 文本模式：在输入框中输入要发送的文本数据
   - 帧模式：输入 Yaw 和 Pitch 值，设置是否追踪
3. 点击相应按钮发送数据：
   - 文本模式：点击"发送"按钮
   - 帧模式：点击"发送帧数据"按钮
4. 自动接收数据：
   - 系统将自动接收并解析串口发送的帧数据
   - 最新接收的数据会实时显示在界面上
5. 查看接收到的响应和历史记录
6. 可以使用分页按钮浏览历史记录
7. 使用"清空历史记录"按钮清除所有记录

## 帧格式说明 | Frame Format

### 上位机发送帧格式 | Host Send Frame Format
```c
typedef struct {
    char start;         //0 帧头取 's'
    char type;          //1 消息类型：上->下：0xA0/0xA1
    char find_bool;     //2 是否追踪
    float yaw;         //3-6 yaw数据
    float pitch;       //7-10 pitch数据
    char reminder_type; //11 提醒类型：0=无提醒,1=久坐提醒,2=坐姿提醒,3=语音交互
    char reserved[20];  //12-31 保留字节
    char end;          //31 帧尾取'e'
} usb_msg_t;
```

### 下位机发送帧格式 | Device Send Frame Format
```c
typedef struct {
    char start;        //0 帧头取 's'
    char type;         //1 消息类型：下->上：0xB0
    float yaw;        //2-5 yaw数据
    float pitch;      //6-9 pitch数据
    char alert_status; //10 提醒状态
    char reserved[20]; //11-30 保留字节
    char end;         //31 帧尾取'e'
} usb_msgRX_t;
```

### 提醒类型说明 | Reminder Types
- 0x00: 无提醒 | No reminder
- 0x01: 久坐提醒 | Long sitting reminder
- 0x02: 坐姿提醒 | Posture reminder
- 0x03: 语音交互 | Voice interaction

## 项目结构 | Project Structure

- `server.py`: 主服务器程序 | Main server program
- `serial_handler.py`: 串口通信处理类 | Serial communication handler class
- `config.py`: 配置文件 | Configuration file
- `test_db.py`: 数据库连接测试 | Database connection test
- `requirements.txt`: Python 依赖包列表 | Python dependencies list
- `environment.yml`: Conda 环境配置 | Conda environment configuration
- `templates/`: HTML 模板文件 | HTML template files
  - `index.html`: 主页面模板 | Main page template

## 配置选项 | Configuration Options

在 `config.py` 中可以配置以下选项：
The following options can be configured in `config.py`:

- 串口设置 | Serial Port Settings
  - `SERIAL_PORTS`: 可用串口列表 | List of available serial ports
  - `SERIAL_BAUDRATE`: 波特率 | Baud rate

- 数据库设置 | Database Settings
  - `DB_CONFIG`: MySQL 连接配置 | MySQL connection configuration

- 服务器设置 | Server Settings
  - `OPEN_HOST`: 服务器监听地址 | Server listening address

## 串口帧数据处理 | Serial Frame Data Processing

系统支持以下串口帧数据操作：

1. 发送帧数据：
   - 通过 `send_yaw_pitch(find_bool, yaw, pitch)` 方法发送特定格式的帧数据
   - 自动按照上位机帧格式打包数据

2. 接收帧数据：
   - 系统自动监控串口，接收并解析下位机发送的帧数据
   - 接收到的数据自动保存到数据库并推送到前端界面

3. 实时更新：
   - 通过 Server-Sent Events (SSE) 技术实现前端数据实时更新
   - 可以通过界面上的"自动更新"按钮控制是否接收实时更新

## API 接口 | API Interfaces

### 1. 久坐提醒接口 | Sitting Reminder API

```http
GET /api/sitting/status
```

获取当前久坐状态，返回：
```json
{
    "is_sitting": true,
    "duration": 25.5,         // 当前持续久坐时间（分钟）
    "last_movement": "2025-05-05T14:30:00Z",
    "warning_count": 3,       // 今日提醒次数
    "daily_stats": {
        "total_sitting_time": 180,    // 总久坐时间（分钟）
        "total_active_time": 45,      // 总活动时间（分钟）
        "max_continuous_sitting": 45   // 最长持续久坐时间（分钟）
    }
}
```

```http
POST /api/sitting/config
Content-Type: application/json

{
    "threshold": 20,          // 久坐阈值（分钟）
    "warning_interval": 5,    // 提醒间隔（分钟）
    "base_intensity": 0.6,    // 基础提醒强度 (0.0-1.0)
    "enabled": true          // 是否启用提醒
}
```

### 2. 坐姿提醒接口 | Posture Reminder API

```http
GET /api/posture/status
```

获取当前坐姿状态，返回：
```json
{
    "quality": "good",
    "angles": {
        "head": 15.5,
        "neck": 12.3,
        "shoulder": 5.2,
        "spine": 8.7
    },
    "stability_scores": {
        "head": 85.5,
        "neck": 90.2,
        "shoulder": 88.7,
        "spine": 92.1
    },
    "issues": ["颈部前倾"],
    "score": 87.5
}
```

```http
POST /api/posture/config
Content-Type: application/json

{
    "thresholds": {
        "head": 25.0,
        "neck": 20.0,
        "shoulder": 12.0,
        "spine": 15.0
    },
    "weights": {
        "head": 0.25,
        "neck": 0.30,
        "shoulder": 0.15,
        "spine": 0.30
    },
    "enabled": true
}
```

### 3. 语音交互接口 | Voice Interaction API

```http
POST /api/voice/control
Content-Type: application/json

{
    "command": "string",     // start, stop, pause, resume
    "volume": 80,           // 音量 (0-100)
    "duration": 10,         // 持续时间（秒）
    "parameters": {}        // 其他参数
}
```

```http
GET /api/voice/status
```

获取语音模块状态：
```json
{
    "status": "active",     // active, stopped, paused
    "volume": 80,
    "last_command": "start",
    "timestamp": "2025-05-05T14:30:00Z"
}
```

### 4. 串口通信协议 | Serial Communication Protocol

#### 帧格式 | Frame Format
所有通信使用32字节的固定长度帧格式：
```c
typedef struct {
    char start;        // 0 帧头 's'
    char type;         // 1 消息类型
    char data[29];     // 2-30 数据区域
    char end;         // 31 帧尾 'e'
} frame_t;
```

#### 消息类型 | Message Types
- 0xA0: 控制指令 | Control command
- 0xA1: 姿势矫正 | Posture correction
- 0xA2: 久坐提醒 | Sitting reminder
- 0xA3: 警报指令 | Alert command
- 0xA4: 照明控制 | Light control
- 0xA5: 语音控制 | Voice control
- 0xB0: 状态反馈 | Status feedback

#### 提醒类型 | Reminder Types
- 0x00: 无提醒 | No reminder
- 0x01: 久坐提醒 | Sitting reminder
- 0x02: 坐姿提醒 | Posture reminder
- 0x03: 语音交互 | Voice interaction

#### 语音命令 | Voice Commands
- 0x01: 开始交互 | Start interaction
- 0x02: 停止交互 | Stop interaction
- 0x03: 暂停交互 | Pause interaction
- 0x04: 恢复交互 | Resume interaction
- 0x05: 音量控制 | Volume control

## 故障排除 | Troubleshooting

1. 串口连接问题 | Serial Connection Issues
   - 检查设备是否正确连接 | Check if the device is properly connected
   - 确认串口权限 | Verify serial port permissions
   - 检查波特率设置 | Check baud rate settings

2. 数据库问题 | Database Issues
   - 运行 `test_db.py` 测试数据库连接 | Run `test_db.py` to test database connection
   - 检查数据库配置 | Check database configuration
   - 确认数据库服务是否运行 | Verify if database service is running

3. 帧数据问题 | Frame Data Issues
   - 检查帧格式是否匹配 | Check if frame format matches
   - 确认字节序是否正确 | Verify byte order is correct
   - 调试发送/接收的原始数据 | Debug raw data sent/received

## 许可证 | License

[MIT License](LICENSE)