# 安装指南

## 系统要求

### 硬件要求
- USB摄像头
- 串口设备（机械臂）
- 处理器：建议Intel i5或更高
- 内存：最少4GB RAM
- 存储空间：至少1GB可用空间

### 软件要求
- Python 3.8或更高版本
- OpenCV 4.x
- SQLite 3
- 网络浏览器（Chrome/Firefox/Edge最新版本）

## 安装步骤

### 1. Python环境配置

#### 使用Conda（推荐）
```bash
# 创建新的conda环境
conda env create -f environment.yml
# 激活环境
conda activate py-server
```

#### 使用pip
```bash
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置
```bash
# 初始化数据库
python db_handler.py --init
```

### 3. 设备权限配置

#### Linux系统
```bash
# 添加当前用户到dialout组（用于串口访问）
sudo usermod -a -G dialout $USER
# 添加当前用户到video组（用于摄像头访问）
sudo usermod -a -G video $USER
# 配置USB设备权限
sudo cp config/99-usb-serial.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

#### Windows系统
- 确保安装正确的USB串口驱动
- 在设备管理器中检查串口号

### 4. 配置文件设置

1. 复制示例配置文件
```bash
cp config.py.example config.py
```

2. 修改配置文件
- 设置串口参数
- 配置摄像头参数
- 调整系统参数

## 启动系统

1. 启动服务器
```bash
python app.py
```

2. 访问Web界面
打开浏览器访问：http://localhost:5000

## 常见问题

### 串口连接问题
1. 检查设备管理器中的串口号
2. 确认串口权限设置
3. 验证波特率设置

### 摄像头问题
1. 确认摄像头已正确连接
2. 检查设备权限
3. 验证摄像头编号设置

### 数据库问题
1. 确认数据库文件权限
2. 检查磁盘空间
3. 验证数据库连接设置

## 更新说明

### 更新Python包
```bash
# 使用conda
conda env update -f environment.yml

# 使用pip
pip install -r requirements.txt --upgrade
```

### 数据库迁移
```bash
python db_handler.py --migrate
```

## 卸载说明

1. 停止所有运行的服务
2. 删除环境（可选）
```bash
conda remove --name py-server --all  # 如果使用conda
rm -rf venv                         # 如果使用venv
```
3. 删除项目文件夹