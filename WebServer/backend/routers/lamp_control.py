"""
Lamp 控制路由：通过 get_lampbot_instance() 获取全局 LampbotService 实例，
并调用其方法完成灯光、电源、色温、模式、提醒、机械臂等控制。
路径前缀统一为 /api/lamp
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import asyncio

# 引入项目根目录的模块
import os, sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from modules.Lampbot_manager import get_lampbot_instance
except Exception as e:
    # 延迟在请求时抛错
    get_lampbot_instance = None  # type: ignore

# 引入 chatbot 提醒带语音的方法
try:
    from modules.chatbot_module import posture_reminder_voiced, vision_reminder_voiced
except Exception:
    posture_reminder_voiced = None  # type: ignore
    vision_reminder_voiced = None  # type: ignore


router = APIRouter(prefix="/api/lamp", tags=["lamp_control"])


class PowerBody(BaseModel):
    power: bool


class BrightnessSetBody(BaseModel):
    brightness: int = Field(..., ge=0, le=100, description="目标亮度百分比 0-100；0 表示关灯")


class ColorTempSetBody(BaseModel):
    # 兼容前端传 temperature 字段
    temperature: Optional[int] = Field(None, ge=3500, le=6000)
    colorTemperature: Optional[int] = Field(None, ge=3500, le=6000)

    def target_kelvin(self) -> int:
        if self.temperature is not None:
            return int(self.temperature)
        if self.colorTemperature is not None:
            return int(self.colorTemperature)
        raise ValueError("缺少色温字段 temperature 或 colorTemperature")


def _get_service():
    if get_lampbot_instance is None:
        raise HTTPException(status_code=500, detail="Lamp 服务未就绪")
    svc = get_lampbot_instance()
    if svc is None:
        raise HTTPException(status_code=503, detail="Lamp 服务不可用")
    return svc


@router.get("/status")
async def lamp_status():
    svc = _get_service()
    try:
        # 更新并返回状态
        await asyncio.to_thread(svc.update_status)
        return {"success": True, "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {e}")


@router.post("/power")
async def lamp_power(body: PowerBody):
    svc = _get_service()
    try:
        if body.power:
            res = await asyncio.to_thread(svc.light_on)
        else:
            res = await asyncio.to_thread(svc.light_off)
        ok = (res == "success")
        # 同步一次状态（尽量不阻塞太久）
        try:
            await asyncio.wait_for(asyncio.to_thread(svc.update_status), timeout=1.2)
        except Exception:
            pass
        return {"success": ok, "message": "已开启" if body.power else "已关闭", "status": svc.lamp_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置电源失败: {e}")


@router.post("/brightness/up")
async def lamp_brightness_up():
    svc = _get_service()
    try:
        ok = await asyncio.to_thread(svc.light_brighter)
        await asyncio.to_thread(svc.update_status)
        return {"success": ok == "success", "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调高亮度失败: {e}")


@router.post("/brightness/down")
async def lamp_brightness_down():
    svc = _get_service()
    try:
        ok = await asyncio.to_thread(svc.light_dimmer)
        await asyncio.to_thread(svc.update_status)
        return {"success": ok == "success", "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调低亮度失败: {e}")


@router.post("/brightness/set")
async def lamp_brightness_set(body: BrightnessSetBody):
    """尝试将亮度调整到目标百分比。
    由于硬件仅提供增减步进接口，这里采用“多次微调+查询”的策略迭代逼近。
    """
    svc = _get_service()
    target_pct = int(body.brightness)

    try:
        # 读取当前状态
        await asyncio.to_thread(svc.update_status)
        cur_units = int(svc.lamp_status.get('brightness', 500) or 500)
        cur_power = bool(svc.lamp_status.get('power', True))

        # 目标为 0 -> 直接关灯并返回
        if target_pct <= 0:
            await asyncio.to_thread(svc.light_off)
            # 刷新一次状态
            try:
                await asyncio.wait_for(asyncio.to_thread(svc.update_status), timeout=1.2)
            except Exception:
                pass
            return {"success": True, "target": 0, "status": svc.lamp_status}

        # 目标>0 且当前为关灯，则先开灯
        if not cur_power:
            await asyncio.to_thread(svc.light_on)
            await asyncio.sleep(0.08)
            await asyncio.to_thread(svc.update_status)
            cur_units = int(svc.lamp_status.get('brightness', cur_units) or cur_units)

        # 经验映射：设备内部亮度大概率是 0-1000，将百分比映射到 0-1000
        target_units = max(0, min(1000, target_pct * 10))

        # 最近步数 + 半步阈值，避免在两档之间来回
        STEP = 200
        delta = target_units - cur_units
        if abs(delta) > STEP // 2:
            steps_to_move = int(round(delta / STEP))
            # 单次最多 5 步，避免长时间阻塞
            steps_to_move = max(-5, min(5, steps_to_move))
            SLEEP = 0.06
            for _ in range(abs(steps_to_move)):
                if steps_to_move > 0:
                    await asyncio.to_thread(svc.light_brighter)
                else:
                    await asyncio.to_thread(svc.light_dimmer)
                await asyncio.sleep(SLEEP)
            # 调整后刷新一次
            await asyncio.to_thread(svc.update_status)

        return {"success": True, "target": target_pct, "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置亮度失败: {e}")


@router.post("/colortemp/up")
async def lamp_colortemp_up():
    svc = _get_service()
    try:
        ok = await asyncio.to_thread(svc.color_temperature_up)
        await asyncio.to_thread(svc.update_status)
        return {"success": ok == "success", "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提升色温失败: {e}")


@router.post("/colortemp/down")
async def lamp_colortemp_down():
    svc = _get_service()
    try:
        ok = await asyncio.to_thread(svc.color_temperature_down)
        await asyncio.to_thread(svc.update_status)
        return {"success": ok == "success", "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"降低色温失败: {e}")


@router.post("/colortemp/set")
async def lamp_colortemp_set(body: ColorTempSetBody):
    """尝试将色温调整到目标 K 值。同样采用步进逼近。"""
    svc = _get_service()
    try:
        target_k = body.target_kelvin()
        await asyncio.to_thread(svc.update_status)
        cur_k = int(svc.lamp_status.get('color_temp', 5300) or 5300)

        # 最近步数 + 半步阈值
        STEP = 800
        delta = target_k - cur_k
        if abs(delta) > STEP // 2:  # 400K 内不调整
            steps_to_move = int(round(delta / STEP))
            steps_to_move = max(-3, min(3, steps_to_move))
            SLEEP = 0.06
            for _ in range(abs(steps_to_move)):
                if steps_to_move > 0:
                    await asyncio.to_thread(svc.color_temperature_up)
                else:
                    await asyncio.to_thread(svc.color_temperature_down)
                await asyncio.sleep(SLEEP)
            await asyncio.to_thread(svc.update_status)

        return {"success": True, "target": target_k, "status": svc.lamp_status}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置色温失败: {e}")


@router.post("/mode/reading")
async def lamp_mode_reading():
    svc = _get_service()
    try:
        ok = await asyncio.to_thread(svc.reading_mode)
        await asyncio.to_thread(svc.update_status)
        return {"success": ok == "success", "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"阅读模式失败: {e}")


@router.post("/mode/learning")
async def lamp_mode_learning():
    svc = _get_service()
    try:
        ok = await asyncio.to_thread(svc.learning_mode)
        await asyncio.to_thread(svc.update_status)
        return {"success": ok == "success", "status": svc.lamp_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"学习模式失败: {e}")


@router.post("/reminder/posture")
async def lamp_reminder_posture():
    # 优先调用 chatbot 模块的语音提醒版本
    try:
        if posture_reminder_voiced is None:
            raise RuntimeError("chatbot 模块未就绪")
        ok = await asyncio.to_thread(posture_reminder_voiced)
        return {"success": ok == "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"坐姿提醒失败: {e}")


@router.post("/reminder/vision")
async def lamp_reminder_vision():
    # 优先调用 chatbot 模块的语音提醒版本
    try:
        if vision_reminder_voiced is None:
            raise RuntimeError("chatbot 模块未就绪")
        ok = await asyncio.to_thread(vision_reminder_voiced)
        return {"success": ok == "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"远眺提醒失败: {e}")


@router.post("/arm/{action}")
async def lamp_arm_control(action: str):
    svc = _get_service()
    action = (action or '').lower()
    try:
        if action == 'forward':
            ok = await asyncio.to_thread(svc.arm_forward)
        elif action == 'backward':
            ok = await asyncio.to_thread(svc.arm_backward)
        elif action == 'left':
            ok = await asyncio.to_thread(svc.arm_left)
        elif action == 'right':
            ok = await asyncio.to_thread(svc.arm_right)
        else:
            raise HTTPException(status_code=400, detail="不支持的机械臂动作")
        return {"success": ok == "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"机械臂控制失败: {e}")
