from dataclasses import dataclass, field
from threading import RLock
from typing import Optional, Dict, Any

@dataclass
class AppContext:
    """应用上下文，存储各个服务实例和共享数据"""
    posture_monitor: Optional[object] = None
    video_stream: Optional[object] = None
    serial_handler: Optional[object] = None
    chatbot: Optional[object] = None
    detection_service: Optional[object] = None
    emotion_detector: Optional[object] = None  # 新增情绪检测器字段

    # 线程安全的指标存储
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)
    latest_metrics: Dict[str, Any] = field(default_factory=dict)

    def update_metrics(self, **kwargs):
        """线程安全地更新指标数据"""
        with self._lock:
            self.latest_metrics.update(kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """线程安全地获取指标数据"""
        with self._lock:
            return dict(self.latest_metrics)

    def get_service_status(self) -> Dict[str, bool]:
        """获取各服务的状态"""
        return {
            "posture_monitor": self.posture_monitor is not None,
            "video_stream": self.video_stream is not None,
            "serial_handler": self.serial_handler is not None and getattr(self.serial_handler, 'initialized', False),
            "chatbot": self.chatbot is not None,
            "detection_service": self.detection_service is not None,
            "emotion_detector": self.emotion_detector is not None
        }
