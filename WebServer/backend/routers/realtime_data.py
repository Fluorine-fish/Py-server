"""
实时数据接口路由模块
处理移动端首页实时数据获取功能
包括设备状态、坐姿检测、用眼监测、情绪检测数据
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import json
import logging
import sys
import os
from typing import Dict, Any, Optional

# 添加项目路径以导入现有模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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
        """获取实时坐姿检测数据"""
        try:
            # TODO: 集成实际的坐姿检测模块
            self.latest_posture_data["lastDetected"] = datetime.now(timezone.utc).isoformat()
            return self.latest_posture_data.copy()
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
        """获取实时情绪检测数据"""
        try:
            # TODO: 集成实际的情绪检测模块
            # 可以从 Emotion_Detector 模块获取数据
            emotion_history = self.latest_emotion_data["history"]
            current_time = datetime.now(timezone.utc).isoformat()
            
            # 更新历史记录
            if len(emotion_history) == 0 or emotion_history[-1]["emotion"] != self.latest_emotion_data["currentEmotion"]:
                emotion_history.append({
                    "time": current_time,
                    "emotion": self.latest_emotion_data["currentEmotion"],
                    "duration": 0
                })
            
            return self.latest_emotion_data.copy()
        except Exception as e:
            logger.error(f"获取情绪数据失败: {e}")
            return {
                "currentEmotion": "unknown",
                "confidence": 0.0,
                "history": [],
                "error": str(e)
            }
    
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
async def get_device_status():
    """
    获取设备在线状态和基本信息
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 设备状态信息
    """
    try:
        logger.info("获取设备状态")
        return realtime_data_manager.get_device_status()
    except Exception as e:
        logger.error(f"获取设备状态接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取设备状态失败: {str(e)}")

@router.get("/monitor/posture")
async def get_posture_data():
    """
    获取实时坐姿检测数据
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 坐姿检测数据
    """
    try:
        logger.info("获取坐姿数据")
        return realtime_data_manager.get_posture_data()
    except Exception as e:
        logger.error(f"获取坐姿数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取坐姿数据失败: {str(e)}")

@router.get("/monitor/eye")
async def get_eye_data():
    """
    获取实时用眼监测数据
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 用眼监测数据
    """
    try:
        logger.info("获取用眼数据")
        return realtime_data_manager.get_eye_data()
    except Exception as e:
        logger.error(f"获取用眼数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取用眼数据失败: {str(e)}")

@router.get("/monitor/emotion")
async def get_emotion_data():
    """
    获取实时情绪检测数据
    
    功能位置: Home.vue 统计区域
    优先级: 高 🔥
    
    Returns:
        dict: 情绪检测数据
    """
    try:
        logger.info("获取情绪数据")
        return realtime_data_manager.get_emotion_data()
    except Exception as e:
        logger.error(f"获取情绪数据接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取情绪数据失败: {str(e)}")

@router.get("/monitor/all")
async def get_all_monitor_data():
    """
    一次性获取所有监测数据
    
    优化接口，减少前端请求次数
    
    Returns:
        dict: 包含所有监测数据的字典
    """
    try:
        logger.info("获取所有监测数据")
        return {
            "device": realtime_data_manager.get_device_status(),
            "posture": realtime_data_manager.get_posture_data(),
            "eye": realtime_data_manager.get_eye_data(),
            "emotion": realtime_data_manager.get_emotion_data(),
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
async def get_posture_distribution(timeRange: str = Query("day", pattern="^(day|week|month)$")):
    """获取坐姿时间分布数据"""
    try:
        data = {
            "day": {
                "data": [2, 1, 0, 3, 4, 2, 1, 0, 5, 3, 1, 0],
                "labels": ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]
            },
            "week": {
                "data": [4, 5, 3, 6, 5, 7, 2],
                "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            },
            "month": {
                "data": [5, 6, 4, 7, 5, 6, 5, 7, 4, 6, 5, 6],
                "labels": [f"{d}日" for d in range(1, 13)]
            }
        }
        return data[timeRange]
    except Exception as e:
        logger.error(f"获取坐姿分布失败: {e}")
        raise HTTPException(status_code=500, detail="获取坐姿分布失败")

@router.get("/monitor/posture/images")
async def get_posture_images(page: int = Query(1, ge=1), limit: int = Query(6, ge=1, le=50)):
    """获取坐姿检测图像记录（分页）"""
    try:
        total = 120
        start_id = (page - 1) * limit + 1
        data = []
        for i in range(limit):
            img_id = f"img_{page}_{i+1}"
            data.append({
                "id": img_id,
                "url": f"/static/posture/img_{start_id + i:03d}.jpg",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "score": 80 - (i % 10),
                "status": ["good", "mild", "bad"][i % 3]
            })
        return {"data": data, "total": total, "page": page, "limit": limit}
    except Exception as e:
        logger.error(f"获取坐姿图片失败: {e}")
        raise HTTPException(status_code=500, detail="获取坐姿图片失败")

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
async def get_emotion_distribution():
    return {
        "timeSlots": ["上午", "中午", "下午", "晚上"],
        "emotions": {
            "happy": [30, 25, 20, 15],
            "neutral": [40, 45, 50, 55],
            "sad": [20, 20, 20, 20],
            "focused": [10, 10, 10, 10]
        }
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
