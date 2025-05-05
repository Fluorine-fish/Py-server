# 安装指南

## 系统要求

### 硬件要求
- 支持OpenCV的摄像头设备
- 串口设备（用于机械臂通信）
- 处理器：建议Intel i5或更高
- 内存：最小4GB，建议8GB
- 存储空间：至少1GB可用空间

### 软件要求
- Python 3.9+
- MySQL 5.7+
- Git（用于版本控制）
- 支持的操作系统：
  - Linux (推荐 Ubuntu 20.04+)
  - Windows 10+
  - macOS 10.15+

## 安装步骤

### 1. 获取源代码
```bash
git clone [repository-url]
cd Py-server
```

### 2. 创建虚拟环境
使用 Conda：
```bash
conda env create -f environment.yml
conda activate smart-lamp
```
或使用 pip：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. 配置串口权限（Linux系统）
```bash
sudo usermod -a -G dialout $USER
sudo chmod a+rw /dev/ttyUSB0  # 根据实际串口设备修改
```

### 4. 配置数据库
1. 安装MySQL
2. 创建数据库和用户：
```sql
CREATE DATABASE serial_data;
CREATE USER 'serial_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON serial_data.* TO 'serial_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. 配置应用
1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 修改 .env 文件：
```
DB_HOST=localhost
DB_USER=serial_user
DB_PASSWORD=your-password
DB_NAME=serial_data
SERIAL_PORT=/dev/ttyUSB0
SERIAL_BAUDRATE=115200
CAMERA_ID=0
```

## 启动系统

### 1. 开发环境
```bash
python server.py
```

### 2. 生产环境
```bash
gunicorn -k eventlet -w 1 server:app
```

## 验证安装

1. 访问Web界面：http://localhost:5000
2. 检查串口连接状态
3. 验证摄像头工作状态
4. 测试数据库连接

## 常见问题解决

### 1. 串口权限问题
- 确保用户在 dialout 组中
- 检查串口设备权限
- 验证串口设备名称

### 2. 数据库连接问题
- 检查MySQL服务状态
- 验证数据库用户权限
- 确认连接参数正确

### 3. 摄像头问题
- 检查设备是否被系统识别
- 确认摄像头ID设置正确
- 验证摄像头驱动安装状态

### 4. 依赖安装问题
- 确保pip/conda更新到最新版本
- 检查Python版本兼容性
- 解决依赖冲突

## 更新说明

更新系统时请按以下步骤：
1. 备份数据库和配置文件
2. 拉取最新代码
3. 更新依赖包
4. 执行数据库迁移
5. 重启服务

## 卸载说明

1. 停止所有服务进程
2. 删除虚拟环境
3. 删除项目文件
4. 清理数据库（可选）
5. 移除用户组权限（可选）

## 安全建议

1. 更改默认密码
2. 限制数据库远程访问
3. 定期更新系统
4. 启用HTTPS（生产环境）
5. 配置防火墙规则