import logging
import os
from datetime import datetime
import json
from typing import Dict, Any, Optional

class LogManager:
    def __init__(self, log_dir: str = "logs"):
        """初始化日志管理器
        
        Args:
            log_dir: 日志文件存储目录
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置系统日志
        self.setup_system_logger()
        
        # 配置性能日志
        self.setup_performance_logger()
        
        # 配置用户行为日志
        self.setup_user_logger()
        
    def setup_system_logger(self):
        """配置系统日志"""
        system_logger = logging.getLogger('system')
        system_logger.setLevel(logging.INFO)
        
        # 文件处理器
        system_file = os.path.join(self.log_dir, 'system.log')
        file_handler = logging.FileHandler(system_file)
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        system_logger.addHandler(file_handler)
        system_logger.addHandler(console_handler)
        
    def setup_performance_logger(self):
        """配置性能日志"""
        perf_logger = logging.getLogger('performance')
        perf_logger.setLevel(logging.INFO)
        
        # 性能日志文件
        perf_file = os.path.join(self.log_dir, 'performance.log')
        handler = logging.FileHandler(perf_file)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        handler.setFormatter(formatter)
        perf_logger.addHandler(handler)
        
    def setup_user_logger(self):
        """配置用户行为日志"""
        user_logger = logging.getLogger('user')
        user_logger.setLevel(logging.INFO)
        
        # 用户行为日志文件
        user_file = os.path.join(self.log_dir, 'user_activity.log')
        handler = logging.FileHandler(user_file)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        handler.setFormatter(formatter)
        user_logger.addHandler(handler)
        
    def log_system_event(self, event_type: str, message: str, level: str = 'info'):
        """记录系统事件
        
        Args:
            event_type: 事件类型
            message: 事件消息
            level: 日志级别 ('debug', 'info', 'warning', 'error', 'critical')
        """
        logger = logging.getLogger('system')
        log_func = getattr(logger, level.lower())
        log_func(f"{event_type}: {message}")
        
    def log_performance(self, metrics: Dict[str, Any]):
        """记录性能指标
        
        Args:
            metrics: 性能指标数据字典
        """
        logger = logging.getLogger('performance')
        logger.info(json.dumps(metrics))
        
    def log_user_activity(self, user_id: str, activity_type: str, 
                         details: Optional[Dict[str, Any]] = None):
        """记录用户活动
        
        Args:
            user_id: 用户ID
            activity_type: 活动类型
            details: 活动详情
        """
        logger = logging.getLogger('user')
        log_data = {
            'user_id': user_id,
            'activity_type': activity_type,
            'details': details or {}
        }
        logger.info(json.dumps(log_data))
        
    def get_recent_logs(self, log_type: str, n_lines: int = 100) -> list:
        """获取最近的日志记录
        
        Args:
            log_type: 日志类型 ('system', 'performance', 'user')
            n_lines: 返回的日志行数
        
        Returns:
            最近的日志记录列表
        """
        log_file = os.path.join(self.log_dir, f'{log_type}.log')
        if not os.path.exists(log_file):
            return []
            
        logs = []
        try:
            with open(log_file, 'r') as f:
                # 使用负索引读取最后n行
                lines = f.readlines()
                logs = lines[-n_lines:]
        except Exception as e:
            logging.getLogger('system').error(f"读取日志文件失败: {e}")
            
        return logs
        
    def clear_old_logs(self, days: int = 30):
        """清理旧日志文件
        
        Args:
            days: 保留最近多少天的日志
        """
        current_time = datetime.now().timestamp()
        max_age = days * 24 * 3600  # 转换为秒
        
        for log_file in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, log_file)
            if os.path.isfile(file_path):
                # 获取文件修改时间
                file_time = os.path.getmtime(file_path)
                if current_time - file_time > max_age:
                    try:
                        os.remove(file_path)
                        logging.getLogger('system').info(f"已删除旧日志文件: {log_file}")
                    except Exception as e:
                        logging.getLogger('system').error(f"删除日志文件失败: {e}")

# 创建全局日志管理器实例
log_manager = LogManager()