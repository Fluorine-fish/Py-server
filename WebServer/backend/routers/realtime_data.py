"""
实时数据接口路由模块
处理移动端首页实时数据获取功能
包括设备状态、坐姿检测、用眼监测、情绪检测数据
"""

from fastapi import APIRouter, HTTPException, Query, Request
from datetime import datetime, timezone, date, time as dt_time
from pydantic import BaseModel, Field
import json
import logging
import sys
import os
from typing import Dict, Any, Optional

# 添加项目路径以导入现有模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    # 尝试导入数据库统计函数
    from modules.database_module import get_posture_stats
except Exception:
    get_posture_stats = None  # type: ignore
from pathlib import Path
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["realtime_data"]
)

# 定义请求体模型
class PostureUpdateRequest(BaseModel):
    score: int
    warn_count: Optional[int] = None

class EyeUpdateRequest(BaseModel):
    distance: float
    screen_time: Optional[int] = None

class EmotionUpdateRequest(BaseModel):
    emotion: str
    confidence: float

# 设备控制与设置相关模型
class LightBrightnessRequest(BaseModel):
    brightness: int = Field(..., ge=0, le=100)

class LightColorRequest(BaseModel):
    colorTemperature: int = Field(..., ge=2700, le=6500)

class LightPowerRequest(BaseModel):
    power: bool

class NotificationsConfig(BaseModel):
    postureReminder: bool
    eyeReminder: bool
    emotionAlert: bool
    dailyReport: bool
    reminderInterval: int
    quietHours: Dict[str, Any]

class RealTimeDataManager:
    """实时数据管理器"""
    
    def __init__(self):
        self.device_status = {
            "online": True,
            "lastSeen": datetime.now(timezone.utc).isoformat(),
            "batteryLevel": 85,
            "charging": True
        }
        # 设备设置（内存态）
        self.device_settings = {
            "brightness": 70,
            "colorTemperature": 5500,
            "autoAdjust": True,
            "power": True
        }
        # 用户与通知配置（内存态）
        self.user_info = {
            "username": "家长用户",
            "avatar": "/static/avatars/default.jpg",
            "phone": "138****1234",
            "email": "user@example.com"
        }
        self.notifications = {
            "postureReminder": True,
            "eyeReminder": True,
            "emotionAlert": True,
            "dailyReport": True,
            "reminderInterval": 30,
            "quietHours": {
                "enabled": True,
                "start": "22:00",
                "end": "07:00"
            }
        }
        
        # 模拟数据，后续可以从实际的检测模块获取
        self.latest_posture_data = {
            "currentScore": 85,
            "warnCount": 3,
            "averageScore": 78,
            "lastDetected": datetime.now(timezone.utc).isoformat()
        }
        # 额外状态用于平滑与告警节流
        self._posture_avg_internal = 78.0
        self._last_warn_ts = None
        self._last_score = None

        self.latest_eye_data = {
            "eyeDistance": 45,
            "screenTime": 7200,  # 秒
            "breakReminder": "每30分钟",
            "lastWarning": datetime.now(timezone.utc).isoformat()
        }
        
        self.latest_emotion_data = {
            "currentEmotion": "happy",
            "confidence": 0.92,
            "history": [
                {
                    "time": datetime.now(timezone.utc).isoformat(),
                    "emotion": "neutral",
                    "duration": 1200
                }
            ]
        }
    
    def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            # 这里可以集成实际的设备状态检测
            self.device_status["lastSeen"] = datetime.now(timezone.utc).isoformat()
            return self.device_status.copy()
        except Exception as e:
            logger.error(f"获取设备状态失败: {e}")
            return {
                "online": False,
                "lastSeen": datetime.now(timezone.utc).isoformat(),
                "batteryLevel": 0,
                "charging": False,
                "error": str(e)
            }
    
    def get_posture_data(self) -> Dict[str, Any]:
        """获取实时坐姿检测数据（默认模拟）"""
        try:
            self.latest_posture_data["lastDetected"] = datetime.now(timezone.utc).isoformat()
            data = self.latest_posture_data.copy()
            # 按需求：平均分提升15分（上限100，下限0），仅对返回值生效
            try:
                avg = int(data.get("averageScore", 0))
            except Exception:
                avg = 0
            data["averageScore"] = max(0, min(100, avg + 15))
            # 当前分数提升20分（上限100，下限0），仅对返回值生效
            try:
                cur = int(data.get("currentScore", 0))
            except Exception:
                cur = 0
            data["currentScore"] = max(0, min(100, cur + 20))
            return data
        except Exception as e:
            logger.error(f"获取坐姿数据失败: {e}")
            return {
                "currentScore": 0,
                "warnCount": 0,
                "averageScore": 0,
                "lastDetected": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    def get_eye_data(self) -> Dict[str, Any]:
        """获取实时用眼监测数据"""
        try:
            # TODO: 集成实际的用眼检测模块
            self.latest_eye_data["lastWarning"] = datetime.now(timezone.utc).isoformat()
            return self.latest_eye_data.copy()
        except Exception as e:
            logger.error(f"获取用眼数据失败: {e}")
            return {
                "eyeDistance": 0,
                "screenTime": 0,
                "breakReminder": "未设置",
                "lastWarning": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    def get_emotion_data(self) -> Dict[str, Any]:
        """获取实时情绪检测数据（默认模拟）"""
        try:
            emotion_history = self.latest_emotion_data["history"]
            current_time = datetime.now(timezone.utc).isoformat()
            if len(emotion_history) == 0 or emotion_history[-1]["emotion"] != self.latest_emotion_data["currentEmotion"]:
                emotion_history.append({
                    "time": current_time,
                    "emotion": self.latest_emotion_data["currentEmotion"],
                    "duration": 0
                })
            data = self.latest_emotion_data.copy()
            # 规格化未知情绪
            emo = (data.get("currentEmotion") or "").lower()
            if emo in ("unknown", "unkown", "", None):
                data["currentEmotion"] = "neutral"
            return data
        except Exception as e:
            logger.error(f"获取情绪数据失败: {e}")
            return {
                "currentEmotion": "unknown",
                "confidence": 0.0,
                "history": [],
                "error": str(e)
            }

    # ---- 以下为从 AppContext 读取实时数据的适配器 ----
    def posture_from_context(self, ctx) -> Optional[Dict[str, Any]]:
        """从 AppContext 的 posture_monitor 提取实时坐姿数据，返回None表示不可用"""
        try:
            pm = getattr(ctx, 'posture_monitor', None)
            if not pm or not hasattr(pm, 'pose_result'):
                return None
            pose_res = pm.pose_result or {}
            angle = pose_res.get('angle')
            is_bad = pose_res.get('is_bad_posture')
            is_occ = pose_res.get('is_occluded')
            # 角度转分数：角度越小越好，简化映射
            if angle is None:
                score = 50
            else:
                score = int(max(0, min(100, 100 - angle * 1.2)))
            # 平滑平均分
            prev_avg = self._posture_avg_internal
            new_avg = 0.9 * prev_avg + 0.1 * score
            self._posture_avg_internal = new_avg
            avg_score = int(new_avg)
            # 平均分对前端展示提升15分（0-100）
            avg_score = max(0, min(100, avg_score + 15))
            # 当前分数对前端展示提升20分（0-100）
            score = max(0, min(100, score + 20))
            # 告警计数节流：30秒内只计一次
            warn_count = self.latest_posture_data.get('warnCount', 0)
            import time as _t
            now_ts = _t.time()
            if is_bad and not is_occ:
                if self._last_warn_ts is None or (now_ts - self._last_warn_ts) >= 30:
                    warn_count += 1
                    self._last_warn_ts = now_ts
            # 组装
            data = {
                "currentScore": score,
                "warnCount": warn_count,
                "averageScore": avg_score,
                "lastDetected": datetime.now(timezone.utc).isoformat()
            }
            # 写回缓存
            self.latest_posture_data.update(data)
            return data
        except Exception as e:
            logger.error(f"从上下文读取坐姿数据失败: {e}")
            return None

    def emotion_from_context(self, ctx) -> Optional[Dict[str, Any]]:
        """从 AppContext 的 emotion_detector 或 posture_monitor 提取情绪数据，返回None表示不可用"""
        try:
            # 优先使用 EmotionDetectorRKNN
            ed = getattr(ctx, 'emotion_detector', None)
            if ed and hasattr(ed, 'emotion_type') and hasattr(ed, 'emotion_confidence'):
                emo = ed.emotion_type or 'unknown'
                conf = float(ed.emotion_confidence) if ed.emotion_confidence is not None else 0.0
            else:
                # 退回 WebPostureMonitor 的 emotion_result
                pm = getattr(ctx, 'posture_monitor', None)
                emo = None
                conf = 0.0
                if pm and hasattr(pm, 'emotion_result'):
                    er = pm.emotion_result or {}
                    emo_raw = er.get('emotion')  # 可能是 'NEUTRAL', 'HAPPY' 等
                    if isinstance(emo_raw, str):
                        emo = emo_raw.lower()
            if not emo:
                return None
            # 规范化到前端预期标签
            mapping = {
                'neutral': 'neutral', 'happy': 'happy', 'sad': 'sad', 'angry': 'angry',
                'surprised': 'surprised', 'fearful': 'fearful', 'disgusted': 'disgusted',
                'focused': 'focused', 'unknown': 'neutral'
            }
            emo_std = mapping.get(emo, 'neutral')
            if emo_std in ("unknown", "unkown"):
                emo_std = 'neutral'
            # 更新历史
            self.latest_emotion_data['currentEmotion'] = emo_std
            self.latest_emotion_data['confidence'] = max(0.0, min(1.0, conf))
            hist = self.latest_emotion_data.get('history', [])
            now_iso = datetime.now(timezone.utc).isoformat()
            if not hist or hist[-1].get('emotion') != emo_std:
                hist.append({
                    'time': now_iso,
                    'emotion': emo_std,
                    'duration': 0
                })
                if len(hist) > 50:
                    hist.pop(0)
            self.latest_emotion_data['history'] = hist
            return {
                'currentEmotion': emo_std,
                'confidence': self.latest_emotion_data['confidence'],
                'history': hist
            }
        except Exception as e:
            logger.error(f"从上下文读取情绪数据失败: {e}")
            return None
    
    def update_posture_data(self, score: int, warn_count: Optional[int] = None):
        """更新坐姿数据"""
        try:
            self.latest_posture_data["currentScore"] = max(0, min(100, score))
            if warn_count is not None:
                self.latest_posture_data["warnCount"] = max(0, warn_count)
            self.latest_posture_data["lastDetected"] = datetime.now(timezone.utc).isoformat()
            
            # 更新平均分
            current_avg = self.latest_posture_data["averageScore"]
            self.latest_posture_data["averageScore"] = int((current_avg * 0.9) + (score * 0.1))
            
        except Exception as e:
            logger.error(f"更新坐姿数据失败: {e}")
    
    def update_eye_data(self, distance: float, screen_time: Optional[int] = None):
        """更新用眼数据"""
        try:
            self.latest_eye_data["eyeDistance"] = max(0, distance)
            if screen_time is not None:
                self.latest_eye_data["screenTime"] = max(0, screen_time)
            self.latest_eye_data["lastWarning"] = datetime.now(timezone.utc).isoformat()
        except Exception as e:
            logger.error(f"更新用眼数据失败: {e}")
    
    def update_emotion_data(self, emotion: str, confidence: float):
        """更新情绪数据"""
        try:
            if 0 <= confidence <= 1:
                self.latest_emotion_data["currentEmotion"] = emotion
                self.latest_emotion_data["confidence"] = confidence
                
                # 更新历史记录
                current_time = datetime.now(timezone.utc).isoformat()
                history = self.latest_emotion_data["history"]
                
                if len(history) == 0 or history[-1]["emotion"] != emotion:
                    history.append({
                        "time": current_time,
                        "emotion": emotion,
                        "duration": 0
                    })
                    # 保持历史记录数量限制
                    if len(history) > 50:
                        history.pop(0)
                        
        except Exception as e:
            logger.error(f"更新情绪数据失败: {e}")

# 全局实时数据管理器实例
realtime_data_manager = RealTimeDataManager()

@router.get("/device/status")
async def get_device_status(request: Request):
    """
    获取设备在线状态和基本信息
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 设备状态信息
    """
    try:
        logger.info("获取设备状态")
        # 优先从 AppContext 读取
        try:
            ctx = getattr(request.app.state, 'ctx', None)
            if ctx is not None:
                metrics = ctx.get_metrics() if hasattr(ctx, 'get_metrics') else {}
                services = ctx.get_service_status() if hasattr(ctx, 'get_service_status') else {}
                return {
                    "online": bool(services.get("video_stream", False)),
                    "lastSeen": datetime.now(timezone.utc).isoformat(),
                    "batteryLevel": metrics.get("battery_level", 85),
                    "charging": metrics.get("charging", True)
                }
        except Exception as _e:
            logger.warning(f"从上下文读取设备状态失败，回退默认: {_e}")
        return realtime_data_manager.get_device_status()
    except Exception as e:
        logger.error(f"获取设备状态接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取设备状态失败: {str(e)}")

@router.get("/monitor/posture")
async def get_posture_data(request: Request):
    """
    获取实时坐姿检测数据
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 坐姿检测数据
    """
    try:
        logger.info("获取坐姿数据")
        # 尝试从 AppContext 的姿势模块读取
        try:
            ctx = getattr(request.app.state, 'ctx', None)
            if ctx is not None:
                live = realtime_data_manager.posture_from_context(ctx)
                if live is not None:
                    return live
        except Exception as _e:
            logger.warning(f"从上下文读取坐姿失败，回退默认: {_e}")
        return realtime_data_manager.get_posture_data()
    except Exception as e:
        logger.error(f"获取坐姿数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取坐姿数据失败: {str(e)}")

@router.get("/monitor/eye")
async def get_eye_data(request: Request):
    """
    获取实时用眼监测数据
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 用眼监测数据
    """
    try:
        logger.info("获取用眼数据")
        # 暂无真实用眼模块，保留默认模拟
        return realtime_data_manager.get_eye_data()
    except Exception as e:
        logger.error(f"获取用眼数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取用眼数据失败: {str(e)}")

@router.get("/monitor/emotion")
async def get_emotion_data(request: Request):
    """
    获取实时情绪检测数据
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 情绪检测数据
    """
    try:
        logger.info("获取情绪数据")
        try:
            ctx = getattr(request.app.state, 'ctx', None)
            if ctx is not None:
                live = realtime_data_manager.emotion_from_context(ctx)
                if live is not None:
                    return live
        except Exception as _e:
            logger.warning(f"从上下文读取情绪失败，回退默认: {_e}")
        return realtime_data_manager.get_emotion_data()
    except Exception as e:
        logger.error(f"获取情绪数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取情绪数据失败: {str(e)}")

@router.get("/monitor/all")
async def get_all_monitor_data(request: Request):
    """
    一次性获取所有监测数据
    
    优化接口，减少前端请求次数
    
    Returns:
        dict: 包含所有监测数据的字典
    """
    try:
        logger.info("获取所有监测数据")
        # 先分别按“从上下文读取优先、否则回退”策略取值
        device = None
        posture = None
        emotion = None
        try:
            device = await get_device_status(request)  # type: ignore
        except Exception:
            device = realtime_data_manager.get_device_status()
        try:
            posture = await get_posture_data(request)  # type: ignore
        except Exception:
            posture = realtime_data_manager.get_posture_data()
        eye = realtime_data_manager.get_eye_data()
        try:
            emotion = await get_emotion_data(request)  # type: ignore
        except Exception:
            emotion = realtime_data_manager.get_emotion_data()
        return {
            "device": device,
            "posture": posture,
            "eye": eye,
            "emotion": emotion,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"获取所有监测数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取监测数据失败: {str(e)}")

# 数据更新接口（供其他模块调用）
@router.post("/monitor/posture/update")
async def update_posture_data(request: PostureUpdateRequest):
    """
    更新坐姿检测数据
    
    供坐姿检测模块调用
    
    Args:
        request: 包含score和warn_count的请求体
    
    Returns:
        dict: 更新结果
    """
    try:
        if not (0 <= request.score <= 100):
            raise HTTPException(status_code=400, detail="坐姿评分必须在0-100之间")
        
        realtime_data_manager.update_posture_data(request.score, request.warn_count)
        logger.info(f"坐姿数据已更新: score={request.score}, warn_count={request.warn_count}")
        
        return {
            "success": True,
            "message": "坐姿数据更新成功",
            "data": realtime_data_manager.get_posture_data()
        }
    except Exception as e:
        logger.error(f"更新坐姿数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新坐姿数据失败: {str(e)}")

@router.post("/monitor/eye/update")
async def update_eye_data(request: EyeUpdateRequest):
    """
    更新用眼监测数据
    
    供用眼检测模块调用
    
    Args:
        request: 包含distance和screen_time的请求体
    
    Returns:
        dict: 更新结果
    """
    try:
        if request.distance < 0:
            raise HTTPException(status_code=400, detail="用眼距离不能为负数")
        
        realtime_data_manager.update_eye_data(request.distance, request.screen_time)
        logger.info(f"用眼数据已更新: distance={request.distance}, screen_time={request.screen_time}")
        
        return {
            "success": True,
            "message": "用眼数据更新成功",
            "data": realtime_data_manager.get_eye_data()
        }
    except Exception as e:
        logger.error(f"更新用眼数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新用眼数据失败: {str(e)}")

@router.post("/monitor/emotion/update")
async def update_emotion_data(request: EmotionUpdateRequest):
    """
    更新情绪检测数据
    
    供情绪检测模块调用
    
    Args:
        request: 包含emotion和confidence的请求体
    
    Returns:
        dict: 更新结果
    """
    try:
        if not (0 <= request.confidence <= 1):
            raise HTTPException(status_code=400, detail="置信度必须在0-1之间")
        
        valid_emotions = ["happy", "sad", "angry", "neutral", "surprised", "fearful", "disgusted", "focused"]
        if request.emotion not in valid_emotions:
            logger.warning(f"未知情绪类型: {request.emotion}")
        
        realtime_data_manager.update_emotion_data(request.emotion, request.confidence)
        logger.info(f"情绪数据已更新: emotion={request.emotion}, confidence={request.confidence}")
        
        return {
            "success": True,
            "message": "情绪数据更新成功",
            "data": realtime_data_manager.get_emotion_data()
        }
    except Exception as e:
        logger.error(f"更新情绪数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新情绪数据失败: {str(e)}")

@router.get("/monitor/stats")
async def get_monitor_stats():
    """
    获取监测统计信息
    
    Returns:
        dict: 统计信息
    """
    try:
        posture_data = realtime_data_manager.get_posture_data()
        eye_data = realtime_data_manager.get_eye_data()
        emotion_data = realtime_data_manager.get_emotion_data()
        
        return {
            "posture_score": posture_data["currentScore"],
            "posture_average": posture_data["averageScore"],
            "warn_count": posture_data["warnCount"],
            "eye_distance": eye_data["eyeDistance"],
            "screen_time_hours": round(eye_data["screenTime"] / 3600, 1),
            "current_emotion": emotion_data["currentEmotion"],
            "emotion_confidence": emotion_data["confidence"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"获取监测统计信息错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

# -------------------------------
# 坐姿检测页面相关接口
# -------------------------------

@router.get("/monitor/posture/history")
async def get_posture_history(timeRange: str = Query("day", pattern="^(day|week|month)$")):
    """
    获取坐姿历史统计数据
    参数: timeRange (day/week/month)
    """
    try:
        sample = {
            "day": {"goodTime": "3.2", "mildTime": "1.2", "badTime": "0.6", "goodRate": "64", "problemTimeSlot": "下午3-5点", "improvementMessage": "今天坐姿良好，请继续保持。"},
            "week": {"goodTime": "18.4", "mildTime": "6.3", "badTime": "3.1", "goodRate": "62", "problemTimeSlot": "下午4-6点", "improvementMessage": "本周整体表现不错，注意下午时段姿势。"},
            "month": {"goodTime": "76.0", "mildTime": "22.5", "badTime": "9.5", "goodRate": "68", "problemTimeSlot": "晚上7-9点", "improvementMessage": "本月姿势有所提升，继续加油。"}
        }
        return sample[timeRange]
    except Exception as e:
        logger.error(f"获取坐姿历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取坐姿历史失败")

@router.get("/monitor/posture/distribution")
async def get_posture_distribution(
    timeRange: str = Query("day", pattern="^(day|week|month|custom)$"),
    start: Optional[str] = Query(None, description="自定义开始时间，ISO格式，如 2025-08-01 或 2025-08-01T08:00:00"),
    end: Optional[str] = Query(None, description="自定义结束时间，ISO格式，如 2025-08-16 或 2025-08-16T23:59:59")
):
    """获取坐姿时间占比（饼图）数据，按 good/mild/moderate/severe 聚合。

    优先从数据库统计；若不可用或失败，回退到0占比结构。
    """
    try:
        # 解析自定义时间范围
        custom_start_dt = None
        custom_end_dt = None
        if timeRange == 'custom':
            if not start or not end:
                raise HTTPException(status_code=400, detail="timeRange=custom 需要提供 start 和 end 参数")
            try:
                # 支持仅日期或完整时间
                try:
                    sdt = datetime.fromisoformat(start)
                except ValueError:
                    sdt = datetime.combine(date.fromisoformat(start), dt_time.min)
                try:
                    edt = datetime.fromisoformat(end)
                except ValueError:
                    edt = datetime.combine(date.fromisoformat(end), dt_time.max)
                if sdt > edt:
                    raise HTTPException(status_code=400, detail="start 不能晚于 end")
                custom_start_dt, custom_end_dt = sdt, edt
            except HTTPException:
                raise
            except Exception as pe:
                raise HTTPException(status_code=400, detail=f"时间格式错误: {pe}")

        if get_posture_stats:
            if timeRange == 'custom':
                stats = get_posture_stats(time_range='custom', custom_start_date=custom_start_dt, custom_end_date=custom_end_dt)
            else:
                stats = get_posture_stats(time_range=timeRange)
            total = max(1, int(stats.get('total_time', {}).get('seconds', 0) or 0))
            # 取各类的秒数
            good_s = int(stats.get('good', {}).get('seconds', 0) or 0)
            mild_s = int(stats.get('mild', {}).get('seconds', 0) or 0)
            moderate_s = int(stats.get('moderate', {}).get('seconds', 0) or 0)
            severe_s = int(stats.get('severe', {}).get('seconds', 0) or 0)
            data = [good_s, mild_s, moderate_s, severe_s]
            # 百分比（保留1位）
            if total > 0:
                percents = [round(v * 100.0 / total, 1) for v in data]
            else:
                percents = [0.0, 0.0, 0.0, 0.0]
            return {
                "labels": ["良好", "轻度", "中度", "重度"],
                "data": percents,
                "rawSeconds": data,
                "totalSeconds": total,
                "timeRange": timeRange,
                "start": custom_start_dt.isoformat() if custom_start_dt else stats.get('start_time'),
                "end": custom_end_dt.isoformat() if custom_end_dt else stats.get('end_time'),
                "formatted": {
                    "good": stats.get('good', {}).get('formatted_time', '0m'),
                    "mild": stats.get('mild', {}).get('formatted_time', '0m'),
                    "moderate": stats.get('moderate', {}).get('formatted_time', '0m'),
                    "severe": stats.get('severe', {}).get('formatted_time', '0m'),
                    "total": stats.get('total_time', {}).get('formatted_time', '0m'),
                }
            }
        else:
            logger.warning("数据库统计函数不可用，返回占位数据")
            return {
                "labels": ["良好", "轻度", "中度", "重度"],
                "data": [0.0, 0.0, 0.0, 0.0],
                "rawSeconds": [0, 0, 0, 0],
                "totalSeconds": 0,
                "timeRange": timeRange,
            }
    except Exception as e:
        logger.error(f"获取坐姿分布失败: {e}")
        # 回退
        return {
            "labels": ["良好", "轻度", "中度", "重度"],
            "data": [0.0, 0.0, 0.0, 0.0],
            "rawSeconds": [0, 0, 0, 0],
            "totalSeconds": 0,
            "timeRange": timeRange,
            "error": str(e)
        }

@router.get("/monitor/posture/images")
async def get_posture_images(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    filter_type: Optional[str] = Query(None, description="筛选类型good/bad/all，当前文件模式下忽略")
):
    """从静态目录返回坐姿图像记录（分页）。

    数据来源: static/posture_images 目录下的文件。
    返回: { data: [ ...images ], total, page, limit }
    """
    try:
        static_dir = Path(__file__).resolve().parents[2] / 'static' / 'posture_images'
        if not static_dir.exists():
            return {"data": [], "total": 0, "page": page, "limit": limit}

        files = [p for p in static_dir.iterdir() if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
        # 按修改时间倒序
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        total = len(files)
        start = (page - 1) * limit
        end = start + limit
        slice_files = files[start:end]

        def parse_time_from_name(name: str) -> Optional[str]:
            # 试解析 posture_YYYYMMDD_HHMMSS_xxx.jpg
            try:
                stem = Path(name).stem
                parts = stem.split('_')
                for i in range(len(parts) - 1):
                    if len(parts[i]) == 8 and len(parts[i+1]) == 6 and parts[i].isdigit() and parts[i+1].isdigit():
                        dt = datetime.strptime(parts[i] + parts[i+1], '%Y%m%d%H%M%S')
                        return dt.replace(tzinfo=timezone.utc).isoformat()
            except Exception:
                return None
            return None

        data = []
        for p in slice_files:
            url = f"/static/posture_images/{p.name}"
            data.append({
                "id": p.stem,
                "url": url,
                "thumbnail": url,
                "timestamp": parse_time_from_name(p.name) or datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
                "score": None,
                "posture_type": "坐姿记录",
                "is_good_posture": True
            })

        return {"data": data, "total": total, "page": page, "limit": limit}
    except Exception as e:
        logger.error(f"获取坐姿图片失败: {e}")
        raise HTTPException(status_code=500, detail="获取坐姿图片失败")

@router.get("/monitor/posture/images/{image_id}")
async def get_posture_image_detail(image_id: str):
    """返回单张图像的详细信息（示例实现）"""
    try:
        static_dir = Path(__file__).resolve().parents[2] / 'static' / 'posture_images'
        candidates = list(static_dir.glob(f"{image_id}.*"))
        if not candidates:
            raise HTTPException(status_code=404, detail="未找到该图像")
        p = candidates[0]
        url = f"/static/posture_images/{p.name}"
        return {
            "id": image_id,
            "url": url,
            "timestamp": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
            "score": None,
            "posture_type": "坐姿记录",
            "analysis": {
                "angles": {"neck": 18, "shoulder": 12, "back": 10}
            },
            "suggestions": ["保持背部挺直", "调整椅子高度", "每30分钟起身活动"],
            "environment": {"lighting": "正常", "screen_distance": "50cm", "desk_height": "合适"}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图像详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取图像详情失败")

@router.get("/monitor/posture/statistics")
async def get_posture_statistics(time_range: str = Query('day')):
    """示例统计接口：根据静态目录文件数返回概要统计。"""
    try:
        static_dir = Path(__file__).resolve().parents[2] / 'static' / 'posture_images'
        total = len([p for p in static_dir.iterdir() if p.is_file()]) if static_dir.exists() else 0
        # 简单占位分布
        good = int(total * 0.6)
        mild = int(total * 0.2)
        moderate = int(total * 0.15)
        severe = total - good - mild - moderate
        return {
            "total_records": total,
            "distribution": {"good": good, "mild": mild, "moderate": moderate, "severe": severe},
            "improvement": {"rate": "+8%", "compared_to": "昨天", "is_better": True}
        }
    except Exception as e:
        logger.error(f"获取坐姿统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取坐姿统计失败")

@router.get("/monitor/posture/improvement")
async def get_posture_improvement():
    """获取坐姿改善建议"""
    return {
        "problemTimeSlot": "下午3-5点",
        "improvementMessage": "本周坐姿改善效果明显，请继续保持良好习惯。",
        "suggestions": ["建议在下午时段设置提醒", "适当调整椅子高度", "保持背部挺直"]
    }

# -------------------------------
# 用眼监护页面相关接口
# -------------------------------

@router.get("/monitor/eye/trends")
async def get_eye_trends():
    return {
        "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "datasets": [
            {"label": "眨眼频率", "data": [15, 18, 22, 19, 16, 20], "borderColor": "#4CAF50"},
            {"label": "用眼距离", "data": [45, 42, 38, 41, 44, 46], "borderColor": "#2196F3"}
        ]
    }

@router.get("/monitor/eye/environment")
async def get_eye_environment():
    return {
        "labels": ["环境光", "屏幕亮度", "对比度", "色温", "反射", "眩光"],
        "data": [80, 75, 85, 90, 70, 65],
        "optimal": [85, 80, 80, 85, 75, 70]
    }

@router.get("/monitor/eye/heatmap")
async def get_eye_heatmap():
    return {
        "hours": ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
        "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "data": [
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],
            [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
        ]
    }

@router.get("/monitor/eye/data")
async def get_eye_detail_data():
    return {
        "focus_time": "25",
        "blink_rate": "18",
        "distance": "45",
        "eyeStrain": "low",
        "recommendations": ["每20分钟远眺20秒", "调整屏幕亮度到舒适水平"]
    }

# -------------------------------
# 情绪监护页面相关接口
# -------------------------------

@router.get("/monitor/emotion/trends")
async def get_emotion_trends():
    return {
        "labels": ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
        "data": [0.7, 0.8, 0.75, 0.9, 0.85, 0.8, 0.82, 0.78],
        "emotions": ["neutral", "happy", "focused", "happy", "focused", "happy", "happy", "neutral"]
    }

@router.get("/monitor/emotion/radar")
async def get_emotion_radar():
    return {
        "labels": ["专注度", "愉悦度", "放松度", "疲劳度", "压力值"],
        "current": [85, 75, 60, 30, 25],
        "average": [80, 70, 65, 35, 30],
        "optimal": [90, 80, 70, 20, 15]
    }

@router.get("/monitor/emotion/distribution")
async def get_emotion_distribution(date: Optional[str] = None):
    """情绪时段分布柱状图数据
    可选参数:
      - date: YYYY-MM-DD，默认当天
    统计上午/中午/下午/晚上各主导情绪出现次数
    """
    try:
        from datetime import datetime, timedelta
        from modules.database_module import get_emotion_timeslot_distribution

        start_time = None
        end_time = None
        if date:
            try:
                d = datetime.strptime(date, "%Y-%m-%d")
                start_time = d.replace(hour=8, minute=0, second=0, microsecond=0)
                end_time = d.replace(hour=22, minute=0, second=0, microsecond=0)
            except ValueError:
                start_time = None
                end_time = None

        data = get_emotion_timeslot_distribution(start_time=start_time, end_time=end_time)
        return data
    except Exception as e:
        logger.error(f"获取情绪时段分布失败: {e}")
        # 回退静态结构，避免前端崩溃
        return {
            "timeSlots": ["上午", "中午", "下午", "晚上"],
            "emotions": {}
        }

@router.get("/monitor/emotion/heatmap")
async def get_emotion_heatmap():
    return {
        "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "hours": ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
        "data": [
            [0.8,0.7,0.9,0.85,0.75,0.8,0.9,0.85,0.7,0.75,0.8,0.85,0.9,0.85,0.8,0.75,0.7],
            [0.75,0.8,0.85,0.9,0.8,0.85,0.9,0.8,0.75,0.8,0.85,0.9,0.85,0.8,0.75,0.8,0.75]
        ]
    }

# -------------------------------
# 家长监护页面
# -------------------------------

@router.get("/monitor/guardian/report")
async def get_guardian_report():
    return {
        "labels": ["坐姿", "用眼", "情绪", "学习时长"],
        "scores": [85, 75, 80, 90],
        "warnings": {"posture": 3, "eye": 2, "emotion": 1, "total": 6},
        "recommendations": [
            "坐姿表现良好，继续保持",
            "建议增加用眼休息时间",
            "情绪状态稳定"
        ]
    }

# -------------------------------
# 设备控制与设置
# -------------------------------

@router.post("/control/light/brightness")
async def set_light_brightness(body: LightBrightnessRequest):
    try:
        realtime_data_manager.device_settings["brightness"] = body.brightness
        return {"success": True, "message": "亮度调整成功", "currentBrightness": body.brightness}
    except Exception as e:
        logger.error(f"设置亮度失败: {e}")
        raise HTTPException(status_code=500, detail="设置亮度失败")

@router.post("/control/light/color")
async def set_light_color(body: LightColorRequest):
    try:
        realtime_data_manager.device_settings["colorTemperature"] = body.colorTemperature
        return {"success": True, "message": "色温调整成功", "currentTemperature": body.colorTemperature}
    except Exception as e:
        logger.error(f"设置色温失败: {e}")
        raise HTTPException(status_code=500, detail="设置色温失败")

@router.post("/control/light/power")
async def set_light_power(body: LightPowerRequest):
    try:
        realtime_data_manager.device_settings["power"] = body.power
        return {"success": True, "message": "灯光已开启" if body.power else "灯光已关闭", "powerState": body.power}
    except Exception as e:
        logger.error(f"设置电源失败: {e}")
        raise HTTPException(status_code=500, detail="设置电源失败")

@router.get("/device/settings")
async def get_device_settings():
    return realtime_data_manager.device_settings

# -------------------------------
# 用户与通知设置
# -------------------------------

@router.get("/user/info")
async def get_user_info():
    return realtime_data_manager.user_info

@router.get("/user/notifications")
async def get_notifications():
    return realtime_data_manager.notifications

@router.post("/user/notifications")
async def update_notifications(cfg: NotificationsConfig):
    try:
        # 基础验证
        if cfg.reminderInterval < 5 or cfg.reminderInterval > 240:
            raise HTTPException(status_code=400, detail="提醒间隔应在5-240分钟之间")
        realtime_data_manager.notifications = cfg.dict()
        return {"success": True, "message": "通知设置已更新"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新通知设置失败: {e}")
        raise HTTPException(status_code=500, detail="更新通知设置失败")
