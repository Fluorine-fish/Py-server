# 安装指南

## 系统要求

### 硬件要求
- 摄像头（支持USB接口）
- 串口设备（支持USB转串口）
- 处理器：推荐Intel i5或更高
- 内存：至少4GB RAM
- 存储：至少100MB可用空间

### 软件要求
- Python 3.9+
- MySQL数据库
- OpenCV支持
- 串口驱动程序

## 安装步骤

### 1. 获取源代码

```bash
git clone <repository-url>
cd Py-server
```

### 2. 创建虚拟环境

使用Conda（推荐）:
```bash
conda env create -f environment.yml
conda activate pyserver
```

或使用pip:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. 配置串口权限

Linux系统需要配置串口访问权限：

1. 添加当前用户到dialout组：
```bash
sudo usermod -a -G dialout $USER
```

2. 创建udev规则：
```bash
sudo nano /etc/udev/rules.d/50-serial.rules
```

添加以下内容：
```
KERNEL=="ttyUSB[0-9]*",MODE="0666"
KERNEL=="ttyACM[0-9]*",MODE="0666"
```

3. 重载udev规则：
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 4. 配置数据库

1. 安装MySQL：
```bash
sudo apt-get install mysql-server  # Ubuntu/Debian
```

2. 创建数据库和用户：
```sql
CREATE DATABASE serial_data;
CREATE USER 'serial_user'@'localhost' IDENTIFIED BY 'Serial123!';
GRANT ALL PRIVILEGES ON serial_data.* TO 'serial_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. 配置系统

1. 复制配置模板：
```bash
cp config.example.py config.py
```

2. 修改配置文件：
- 设置串口参数
- 配置数据库连接
- 调整系统参数

## 启动系统

1. 启动服务器：
```bash
python server.py
```

2. 访问Web界面：
   打开浏览器访问 http://127.0.0.1:5000

## 常见问题

### 串口权限问题
```bash
sudo chmod 666 /dev/ttyUSB0  # 临时解决方案
```

### 数据库连接失败
- 检查MySQL服务是否运行
- 验证数据库用户名和密码
- 确认数据库名称正确

### 摄像头访问失败
- 检查摄像头连接
- 确认设备权限
- 验证OpenCV安装

## 更新说明

定期检查并更新依赖：
```bash
conda env update -f environment.yml  # 使用Conda
# 或
pip install -r requirements.txt --upgrade  # 使用pip
```

## 卸载说明

1. 停止所有服务
2. 删除虚拟环境
3. 删除项目文件
4. 清理数据库（可选）