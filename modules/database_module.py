"""
数据库操作模块 - 处理所有与数据库相关的操作
"""
import mysql.connector
from datetime import datetime
import pytz
import json
from config import DB_CONFIG

def init_database():
    """初始化数据库表结构"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建串口记录表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS serial_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sent_data TEXT,
                received_data TEXT,
                status VARCHAR(50),
                message TEXT,
                timestamp DATETIME(6)
            )
        """)

        # 创建姿势记录表（更新后的结构）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posture_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME(6),
                head_angle FLOAT,
                neck_angle FLOAT,
                shoulder_tilt FLOAT,
                spine_angle FLOAT,
                posture_quality VARCHAR(20),
                posture_score FLOAT,
                is_occluded BOOLEAN,
                issues JSON,
                duration INT,
                session_id VARCHAR(36)
            )
        """)

        # 创建情绪记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME(6),
                emotion_type VARCHAR(20),
                confidence FLOAT,
                session_id VARCHAR(36)
            )
        """)

        # 创建专注度记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME(6),
                focus_score FLOAT,
                posture_contribution FLOAT,
                emotion_contribution FLOAT,
                duration INT,
                session_id VARCHAR(36)
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("数据库表初始化成功")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return False

def save_record_to_db(sent_data, received_data, status="success", message=""):
    """保存通信记录到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO serial_records 
                (sent_data, received_data, status, message, timestamp) 
                VALUES (%s, %s, %s, %s, %s)"""
        current_time = datetime.now(pytz.UTC)
        values = (sent_data, received_data, status, message, current_time)
        
        cursor.execute(sql, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存记录到数据库失败: {str(e)}")
        return False

def save_frame_to_db(frame_data):
    """将接收到的帧数据保存到数据库"""
    try:
        sent_info = "自动接收的数据帧"
        received_info = json.dumps(frame_data)
        status = "success"
        message = "自动接收到数据帧"
        
        if save_record_to_db(sent_info, received_info, status, message):
            print(f"帧数据已保存到数据库: {received_info}")
            return True
        return False
    except Exception as e:
        print(f"保存帧数据到数据库时出错: {str(e)}")
        return False

def get_history_records(page=1, per_page=10):
    """获取历史记录，支持分页"""
    try:
        offset = (page - 1) * per_page
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取总记录数
        cursor.execute("SELECT COUNT(*) as total FROM serial_records")
        total = cursor.fetchone()['total']
        
        # 获取分页数据 - 使用简单的倒序查询
        query = """
            SELECT id, sent_data, received_data, status, message, timestamp
            FROM serial_records
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        records = cursor.fetchall()
        
        # 计算记录编号
        total_pages = (total + per_page - 1) // per_page
        for i, record in enumerate(records):
            record['record_number'] = total - offset - i
        
        cursor.close()
        conn.close()
        
        return {
            'records': records,
            'total': total,
            'current_page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
    except Exception as e:
        print(f"获取历史记录失败: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'records': [],
            'total': 0,
            'current_page': page,
            'per_page': per_page,
            'total_pages': 0
        }

def clear_history():
    """清空历史记录"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("TRUNCATE TABLE serial_records")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"清空历史记录失败: {str(e)}")
        return False

def save_posture_record(angle, posture_quality, is_occluded, duration, session_id=None):
    """保存姿势记录到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO posture_records 
                (timestamp, angle, posture_quality, is_occluded, duration, session_id) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        current_time = datetime.now(pytz.UTC)
        values = (current_time, angle, posture_quality, is_occluded, duration, session_id)
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存姿势记录失败: {str(e)}")
        return False

def save_emotion_record(emotion_type, confidence, session_id=None):
    """保存情绪记录到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO emotion_records 
                (timestamp, emotion_type, confidence, session_id) 
                VALUES (%s, %s, %s, %s)"""
        current_time = datetime.now(pytz.UTC)
        values = (current_time, emotion_type, confidence, session_id)
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存情绪记录失败: {str(e)}")
        return False

def save_focus_record(focus_score, posture_contribution, emotion_contribution, duration, session_id=None):
    """保存专注度记录到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO focus_records 
                (timestamp, focus_score, posture_contribution, emotion_contribution, duration, session_id) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        current_time = datetime.now(pytz.UTC)
        values = (current_time, focus_score, posture_contribution, emotion_contribution, duration, session_id)
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存专注度记录失败: {str(e)}")
        return False

def get_posture_stats(start_time=None, end_time=None, session_id=None):
    """获取姿势分析统计数据"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        where_clauses = []
        params = []
        
        if start_time:
            where_clauses.append("timestamp >= %s")
            params.append(start_time)
        if end_time:
            where_clauses.append("timestamp <= %s")
            params.append(end_time)
        if session_id:
            where_clauses.append("session_id = %s")
            params.append(session_id)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # 获取总计统计
        stats_sql = f"""
            SELECT 
                COUNT(*) as total_records,
                AVG(angle) as avg_angle,
                SUM(CASE WHEN posture_quality = 'good' THEN duration ELSE 0 END) as good_duration,
                SUM(CASE WHEN posture_quality = 'bad' THEN duration ELSE 0 END) as bad_duration,
                SUM(CASE WHEN is_occluded = 1 THEN duration ELSE 0 END) as occluded_duration
            FROM posture_records
            WHERE {where_sql}
        """
        cursor.execute(stats_sql, params)
        stats = cursor.fetchone()
        
        # 获取时间趋势数据
        trend_sql = f"""
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                AVG(angle) as avg_angle,
                COUNT(*) as count,
                SUM(CASE WHEN posture_quality = 'good' THEN 1 ELSE 0 END) as good_count
            FROM posture_records
            WHERE {where_sql}
            GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00')
            ORDER BY hour DESC
            LIMIT 24
        """
        cursor.execute(trend_sql, params)
        trends = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'stats': stats,
            'trends': trends
        }
    except Exception as e:
        print(f"获取姿势统计数据失败: {str(e)}")
        return None

def get_emotion_stats(start_time=None, end_time=None, session_id=None):
    """获取情绪分析统计数据"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        where_clauses = []
        params = []
        
        if start_time:
            where_clauses.append("timestamp >= %s")
            params.append(start_time)
        if end_time:
            where_clauses.append("timestamp <= %s")
            params.append(end_time)
        if session_id:
            where_clauses.append("session_id = %s")
            params.append(session_id)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # 获取情绪分布统计
        distribution_sql = f"""
            SELECT 
                emotion_type,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM emotion_records
            WHERE {where_sql}
            GROUP BY emotion_type
        """
        cursor.execute(distribution_sql, params)
        distribution = cursor.fetchall()
        
        # 获取情绪变化趋势
        trend_sql = f"""
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                emotion_type,
                COUNT(*) as count
            FROM emotion_records
            WHERE {where_sql}
            GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00'), emotion_type
            ORDER BY hour DESC
            LIMIT 24
        """
        cursor.execute(trend_sql, params)
        trends = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'distribution': distribution,
            'trends': trends
        }
    except Exception as e:
        print(f"获取情绪统计数据失败: {str(e)}")
        return None

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class PostureRecord(Base):
    __tablename__ = 'posture_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    head_angle = Column(Float)  # 头部角度
    posture_status = Column(String(20))  # good, bad, severe, occluded
    detection_status = Column(String(20))  # detected, not_detected
    duration = Column(Integer)  # 持续时间(秒)
    
class EmotionRecord(Base):
    __tablename__ = 'emotion_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion_type = Column(String(20))  # happy, sad, angry, neutral, focused
    confidence = Column(Float)  # 置信度
    mouth_ratio = Column(Float)  # 嘴部开合比
    eye_ratio = Column(Float)  # 眼睛开合比
    brow_ratio = Column(Float)  # 眉毛下压比
    duration = Column(Integer)  # 持续时间(秒)

class FocusRecord(Base):
    __tablename__ = 'focus_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    focus_score = Column(Float)  # 0-100的专注度得分
    posture_factor = Column(Float)  # 姿势对专注度的影响因子
    emotion_factor = Column(Float)  # 情绪对专注度的影响因子
    duration = Column(Integer)  # 持续时间(秒)

class EyesightRecord(Base):
    __tablename__ = 'eyesight_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    screen_distance = Column(Float)  # 屏幕距离(厘米)
    ambient_light = Column(Float)  # 环境光照强度(lux)
    blink_rate = Column(Float)  # 眨眼频率(次/分钟)
    usage_duration = Column(Integer)  # 用眼时长(秒)
    break_taken = Column(Boolean)  # 是否已休息
    warning_count = Column(Integer)  # 警告次数

class ChildProfile(Base):
    __tablename__ = 'child_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    height = Column(Float)  # 身高(cm)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 阅读习惯设置
    preferred_distance = Column(Float)  # 建议阅读距离(cm)
    max_continuous_time = Column(Integer)  # 最长连续阅读时间(分钟)
    break_duration = Column(Integer)  # 建议休息时长(分钟)

class DeviceConfig(Base):
    __tablename__ = 'device_configs'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), unique=True)  # 设备唯一标识
    name = Column(String(50))  # 设备名称
    child_id = Column(Integer, ForeignKey('child_profiles.id'))  # 关联的儿童ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 设备参数
    brightness = Column(Integer)  # 亮度设置(0-100)
    color_temp = Column(Integer)  # 色温设置(2700-6500K)
    auto_adjust = Column(Boolean, default=True)  # 是否自动调节
    camera_enabled = Column(Boolean, default=True)  # 摄像头是否启用
    notification_enabled = Column(Boolean, default=True)  # 通知是否启用

class NotificationSettings(Base):
    __tablename__ = 'notification_settings'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('device_configs.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 通知设置
    distance_warning = Column(Boolean, default=True)  # 距离警告
    posture_warning = Column(Boolean, default=True)  # 姿势警告
    time_warning = Column(Boolean, default=True)  # 时间警告
    light_warning = Column(Boolean, default=True)  # 光线警告
    
    # 通知阈值
    continuous_time_threshold = Column(Integer, default=30)  # 连续使用时间阈值(分钟)
    distance_threshold = Column(Float, default=33.0)  # 距离警告阈值(cm)
    light_threshold_min = Column(Integer, default=300)  # 最低照度阈值(lux)
    light_threshold_max = Column(Integer, default=750)  # 最高照度阈值(lux)
    
    # 通知方式
    email_notify = Column(Boolean, default=False)  # 邮件通知
    web_notify = Column(Boolean, default=True)  # 网页通知
    email_address = Column(String(100))  # 通知邮箱

def init_db(db_url='sqlite:///posture_emotion.db'):
    """初始化数据库"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

class DatabaseManager:
    def __init__(self, session):
        self.session = session
    
    def add_posture_record(self, head_angle, posture_status, detection_status, duration):
        record = PostureRecord(
            head_angle=head_angle,
            posture_status=posture_status,
            detection_status=detection_status,
            duration=duration
        )
        self.session.add(record)
        self.session.commit()
    
    def add_emotion_record(self, emotion_type, confidence, mouth_ratio, eye_ratio, brow_ratio, duration):
        record = EmotionRecord(
            emotion_type=emotion_type,
            confidence=confidence,
            mouth_ratio=mouth_ratio,
            eye_ratio=eye_ratio,
            brow_ratio=brow_ratio,
            duration=duration
        )
        self.session.add(record)
        self.session.commit()
    
    def add_focus_record(self, focus_score, posture_factor, emotion_factor, duration):
        record = FocusRecord(
            focus_score=focus_score,
            posture_factor=posture_factor,
            emotion_factor=emotion_factor,
            duration=duration
        )
        self.session.add(record)
        self.session.commit()
    
    def add_eyesight_record(self, screen_distance, ambient_light, blink_rate, usage_duration, break_taken, warning_count):
        record = EyesightRecord(
            screen_distance=screen_distance,
            ambient_light=ambient_light,
            blink_rate=blink_rate,
            usage_duration=usage_duration,
            break_taken=break_taken,
            warning_count=warning_count
        )
        self.session.add(record)
        self.session.commit()
    
    def get_posture_stats(self, start_time=None, end_time=None):
        """获取姿势统计数据"""
        query = self.session.query(PostureRecord)
        if start_time:
            query = query.filter(PostureRecord.timestamp >= start_time)
        if end_time:
            query = query.filter(PostureRecord.timestamp <= end_time)
        return query.all()
    
    def get_emotion_stats(self, start_time=None, end_time=None):
        """获取情绪统计数据"""
        query = self.session.query(EmotionRecord)
        if start_time:
            query = query.filter(EmotionRecord.timestamp >= start_time)
        if end_time:
            query = query.filter(EmotionRecord.timestamp <= end_time)
        return query.all()
    
    def get_focus_stats(self, start_time=None, end_time=None):
        """获取专注度统计数据"""
        query = self.session.query(FocusRecord)
        if start_time:
            query = query.filter(FocusRecord.timestamp >= start_time)
        if end_time:
            query = query.filter(FocusRecord.timestamp <= end_time)
        return query.all()
    
    def get_eyesight_stats(self, start_time=None, end_time=None):
        """获取用眼健康统计数据"""
        query = self.session.query(EyesightRecord)
        if start_time:
            query = query.filter(EyesightRecord.timestamp >= start_time)
        if end_time:
            query = query.filter(EyesightRecord.timestamp <= end_time)
        return query.all()
    
    def clear_old_records(self, days_to_keep=30):
        """清理旧记录"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        self.session.query(PostureRecord).filter(PostureRecord.timestamp < cutoff_date).delete()
        self.session.query(EmotionRecord).filter(EmotionRecord.timestamp < cutoff_date).delete()
        self.session.query(FocusRecord).filter(FocusRecord.timestamp < cutoff_date).delete()
        self.session.query(EyesightRecord).filter(EyesightRecord.timestamp < cutoff_date).delete()
        
        self.session.commit()

# 更新 DatabaseManager 类以添加新的管理方法
def add_child_profile_methods(manager_class):
    def add_child(self, name, age, height):
        child = ChildProfile(name=name, age=age, height=height)
        self.session.add(child)
        self.session.commit()
        return child
        
    def update_child(self, child_id, **kwargs):
        child = self.session.query(ChildProfile).get(child_id)
        if child:
            for key, value in kwargs.items():
                if hasattr(child, key):
                    setattr(child, key, value)
            self.session.commit()
            return child
        return None
        
    def get_child(self, child_id):
        return self.session.query(ChildProfile).get(child_id)
        
    def get_all_children(self):
        return self.session.query(ChildProfile).all()
        
    manager_class.add_child = add_child
    manager_class.update_child = update_child
    manager_class.get_child = get_child
    manager_class.get_all_children = get_all_children
    return manager_class

def add_device_config_methods(manager_class):
    def add_device(self, device_id, name, child_id=None):
        device = DeviceConfig(device_id=device_id, name=name, child_id=child_id)
        self.session.add(device)
        self.session.commit()
        return device
        
    def update_device(self, device_id, **kwargs):
        device = self.session.query(DeviceConfig).filter_by(device_id=device_id).first()
        if device:
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            self.session.commit()
            return device
        return None
        
    def get_device(self, device_id):
        return self.session.query(DeviceConfig).filter_by(device_id=device_id).first()
        
    def get_all_devices(self):
        return self.session.query(DeviceConfig).all()
        
    manager_class.add_device = add_device
    manager_class.update_device = update_device
    manager_class.get_device = get_device
    manager_class.get_all_devices = get_all_devices
    return manager_class

def add_notification_methods(manager_class):
    def add_notification_settings(self, device_id):
        settings = NotificationSettings(device_id=device_id)
        self.session.add(settings)
        self.session.commit()
        return settings
        
    def update_notification_settings(self, device_id, **kwargs):
        settings = self.session.query(NotificationSettings).filter_by(device_id=device_id).first()
        if settings:
            for key, value in kwargs.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            self.session.commit()
            return settings
        return None
        
    def get_notification_settings(self, device_id):
        return self.session.query(NotificationSettings).filter_by(device_id=device_id).first()
        
    manager_class.add_notification_settings = add_notification_settings
    manager_class.update_notification_settings = update_notification_settings
    manager_class.get_notification_settings = get_notification_settings
    return manager_class

# 使用装饰器添加新方法到DatabaseManager类
DatabaseManager = add_child_profile_methods(DatabaseManager)
DatabaseManager = add_device_config_methods(DatabaseManager)
DatabaseManager = add_notification_methods(DatabaseManager)

"""数据库处理模块 - 提供数据存储和检索功能"""
import mysql.connector
import pytz
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_CONFIG

Base = declarative_base()

class PostureRecord(Base):
    """姿势记录表"""
    __tablename__ = 'posture_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    head_angle = Column(Float)        # 头部角度
    neck_angle = Column(Float)        # 颈部角度
    shoulder_tilt = Column(Float)     # 肩部倾斜角度
    spine_angle = Column(Float)       # 脊柱倾斜角度
    posture_quality = Column(String(20))  # good, slightly_bad, bad, severe
    posture_score = Column(Float)     # 姿势综合评分(0-100)
    is_occluded = Column(Boolean)     # 是否被遮挡
    issues = Column(JSON)             # 检测到的问题列表
    duration = Column(Integer)        # 持续时间(秒)
    session_id = Column(String(36))   # 会话ID
    
class EmotionRecord(Base):
    """情绪记录表"""
    __tablename__ = 'emotion_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion_type = Column(String(20))
    confidence = Column(Float)
    session_id = Column(String(36))

class FocusRecord(Base):
    """专注度记录表"""
    __tablename__ = 'focus_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    focus_score = Column(Float)
    posture_weight = Column(Float)
    emotion_weight = Column(Float)
    duration = Column(Integer)
    session_id = Column(String(36))

def init_db():
    """初始化数据库连接和表结构"""
    try:
        engine = create_engine(f'mysql+mysqlconnector://{DB_CONFIG["user"]}:{DB_CONFIG["password"]}@{DB_CONFIG["host"]}/{DB_CONFIG["database"]}')
        Base.metadata.create_all(engine)
        print("数据库表结构初始化成功")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return False

def save_posture_record(posture_data, session_id=None):
    """保存姿势记录到数据库
    
    Args:
        posture_data: 包含多关节姿势分析结果的字典
        session_id: 会话ID
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO posture_records 
                (timestamp, head_angle, neck_angle, shoulder_tilt, spine_angle,
                 posture_quality, posture_score, is_occluded, issues, duration, session_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
        current_time = datetime.now(pytz.UTC)
        
        # 从姿势数据中提取角度信息
        angles = posture_data.get('angles', {})
        
        values = (
            current_time,
            angles.get('head'),
            angles.get('neck'),
            angles.get('shoulder'),
            angles.get('spine'),
            posture_data.get('quality', 'unknown'),
            posture_data.get('score', 0),
            posture_data.get('is_occluded', False),
            json.dumps(posture_data.get('issues', [])),
            posture_data.get('duration', 0),
            session_id
        )
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存姿势记录失败: {str(e)}")
        return False

def save_emotion_record(emotion_type, confidence, session_id=None):
    """保存情绪记录到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO emotion_records 
                (timestamp, emotion_type, confidence, session_id) 
                VALUES (%s, %s, %s, %s)"""
        current_time = datetime.now(pytz.UTC)
        values = (current_time, emotion_type, confidence, session_id)
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存情绪记录失败: {str(e)}")
        return False

def save_focus_record(focus_score, posture_weight, emotion_weight, duration, session_id=None):
    """保存专注度记录到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """INSERT INTO focus_records 
                (timestamp, focus_score, posture_weight, emotion_weight, duration, session_id) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        current_time = datetime.now(pytz.UTC)
        values = (current_time, focus_score, posture_weight, emotion_weight, duration, session_id)
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存专注度记录失败: {str(e)}")
        return False

def get_posture_stats(start_time=None, end_time=None, session_id=None):
    """获取姿势分析统计数据"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        where_clauses = []
        params = []
        
        if start_time:
            where_clauses.append("timestamp >= %s")
            params.append(start_time)
        if end_time:
            where_clauses.append("timestamp <= %s")
            params.append(end_time)
        if session_id:
            where_clauses.append("session_id = %s")
            params.append(session_id)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # 获取总计统计
        stats_sql = f"""
            SELECT 
                COUNT(*) as total_records,
                AVG(head_angle) as avg_head_angle,
                AVG(neck_angle) as avg_neck_angle,
                AVG(shoulder_tilt) as avg_shoulder_tilt,
                AVG(spine_angle) as avg_spine_angle,
                AVG(posture_score) as avg_score,
                SUM(CASE WHEN posture_quality = 'good' THEN duration ELSE 0 END) as good_duration,
                SUM(CASE WHEN posture_quality = 'slightly_bad' THEN duration ELSE 0 END) as slightly_bad_duration,
                SUM(CASE WHEN posture_quality = 'bad' THEN duration ELSE 0 END) as bad_duration,
                SUM(CASE WHEN posture_quality = 'severe' THEN duration ELSE 0 END) as severe_duration,
                SUM(CASE WHEN is_occluded = 1 THEN duration ELSE 0 END) as occluded_duration
            FROM posture_records
            WHERE {where_sql}
        """
        cursor.execute(stats_sql, params)
        stats = cursor.fetchone()
        
        # 获取时间趋势数据
        trend_sql = f"""
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                AVG(head_angle) as avg_head_angle,
                AVG(neck_angle) as avg_neck_angle,
                AVG(shoulder_tilt) as avg_shoulder_tilt,
                AVG(spine_angle) as avg_spine_angle,
                AVG(posture_score) as avg_score,
                COUNT(*) as count,
                SUM(CASE WHEN posture_quality = 'good' THEN 1 ELSE 0 END) as good_count
            FROM posture_records
            WHERE {where_sql}
            GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00')
            ORDER BY hour DESC
            LIMIT 24
        """
        cursor.execute(trend_sql, params)
        trends = cursor.fetchall()
        
        # 获取常见问题统计
        issues_sql = f"""
            SELECT 
                JSON_EXTRACT(issues, '$[*]') as issue_list,
                COUNT(*) as count
            FROM posture_records
            WHERE {where_sql} AND issues IS NOT NULL
            GROUP BY JSON_EXTRACT(issues, '$[*]')
            ORDER BY count DESC
            LIMIT 10
        """
        cursor.execute(issues_sql, params)
        issues = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'stats': stats,
            'trends': trends,
            'common_issues': issues
        }
    except Exception as e:
        print(f"获取姿势统计数据失败: {str(e)}")
        return None