from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
from websocket_manager import manager
from video_stream import camera
from user_agents import parse as parse_ua
from mock_api import router as mock_api_router
from mobile_api import router as mobile_api_router

# 创建基础FastAPI应用
app = FastAPI()

# 设备类型检测函数
def get_device_type(request: Request) -> str:
    """根据 User-Agent 判断设备类型"""
    ua = request.headers.get("user-agent", "")
    
    if parse_ua:
        # 使用 user-agents 库进行精确解析
        ua_parsed = parse_ua(ua)
        return "mobile" if (ua_parsed.is_mobile or ua_parsed.is_tablet) else "pc"
    else:
        # 简单的字符串匹配作为备选方案
        ua_lower = ua.lower()
        mobile_keywords = ["mobile", "android", "iphone", "ipad", "windows phone", "mobi", "tablet"]
        return "mobile" if any(keyword in ua_lower for keyword in mobile_keywords) else "pc"

# 允许前端开发时跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根据设备类型重定向到不同的静态文件目录
@app.get('/', include_in_schema=False)
async def root(request: Request):
    device = get_device_type(request)
    # 支持通过参数覆盖设备类型（用于测试）
    override = request.query_params.get("device")
    if override in ["pc", "mobile"]:
        device = override
    
    # 重定向到对应的设备专用路径
    return RedirectResponse(f"/{device}/")

# PC端静态文件 - 完整版
app.mount(
    "/pc", 
    StaticFiles(directory="../frontend_pc/dist", html=True),
    name="pc_static"
)

# 为PC端的assets文件单独创建挂载点
app.mount(
    "/assets",
    StaticFiles(directory="../frontend_pc/dist/assets"),
    name="pc_assets"
)

# 移动端静态资源 - 只挂载assets目录
app.mount(
    "/mobile/assets",
    StaticFiles(directory="../frontend_mobile/dist/assets"),
    name="mobile_assets"
)

# 处理移动端的所有非资源请求，包括根路径和所有SPA路由
@app.get('/mobile')
@app.get('/mobile/')
@app.get('/mobile/{path:path}')
async def mobile_spa_route(path: str = ""):
    # 返回index.html以支持前端路由
    try:
        with open("../frontend_mobile/dist/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"加载移动端页面失败: {str(e)}", status_code=500)

# 设备信息检测接口（调试用）
@app.get('/api/device-info')
async def device_info(request: Request):
    """返回当前检测到的设备信息"""
    device = get_device_type(request)
    ua = request.headers.get("user-agent", "")
    return {
        'detected_device': device,
        'user_agent': ua,
        'timestamp': time.time()
    }

# MJPEG 视频流
@app.get('/video')
async def video_feed():
    async def generator():
        while True:
            frame = camera.read()
            if frame is None:
                await asyncio.sleep(0.05)
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            await asyncio.sleep(0.03)
    return StreamingResponse(generator(), media_type='multipart/x-mixed-replace; boundary=frame')

# 包含模拟API路由
app.include_router(mock_api_router)

# 包含移动端API路由
app.include_router(mobile_api_router)

# SPA前端路由处理 - 捕获所有移动端路由并重定向到index.html
@app.get('/mobile/{path:path}', include_in_schema=False)
async def mobile_spa_routes(path: str):
    """处理移动端SPA的客户端路由，将所有请求重定向到移动端根目录"""
    return RedirectResponse('/mobile/')

# SPA前端路由处理 - 捕获所有PC端路由并重定向到index.html
@app.get('/pc/{path:path}', include_in_schema=False)
async def pc_spa_routes(path: str):
    """处理PC端SPA的客户端路由，将所有请求重定向到PC端根目录"""
    return RedirectResponse('/pc/')

# WebSocket 推送实时数据示例
@app.websocket('/ws/realtime')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = {
                'timestamp': time.time(),
                'posture_score': 80 + int(time.time()) % 10,
                'eye_distance': 40,
                'emotion': 'happy'
            }
            await manager.broadcast(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)