import os
import sys
import cv2
import json
import numpy as np
from typing import Optional, Generator
from fastapi import FastAPI, APIRouter, Request, WebSocket, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from .context import AppContext

def _detect_device_type(request: Request) -> str:
    """检测设备类型"""
    ua = request.headers.get("User-Agent", "").lower()
    hint = request.headers.get("X-Device-Type", "").lower()
    
    if hint in ("pc", "mobile"):
        return hint
    if any(mobile_ua in ua for mobile_ua in ["iphone", "android", "mobile", "tablet"]):
        return "mobile"
    return "pc"

def get_app_context(request: Request) -> AppContext:
    """依赖注入：获取应用上下文"""
    return request.app.state.ctx

class WebServer:
    def __init__(self, ctx: AppContext, include_mock: bool = True) -> None:
        self.ctx = ctx
        self.include_mock = include_mock
        self.app = self._build_app()

    def _build_app(self) -> FastAPI:
        app = FastAPI(
            title="Py-server WebServer (FastAPI)", 
            version="1.0.0",
            description="智能台灯后端服务"
        )
        app.state.ctx = self.ctx

        # 配置CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境建议限制具体域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 设备类型检测中间件
        @app.middleware("http")
        async def add_device_detection(request: Request, call_next):
            device = _detect_device_type(request)
            # 支持查询参数覆盖设备类型
            override = request.query_params.get("device")
            if override in ["pc", "mobile"]:
                device = override
            request.scope["device_type"] = device
            response = await call_next(request)
            return response

        # 引入Lampbot_server的路由
        self._include_lampbot_routes(app)

        # 添加本地适配路由
        app.include_router(self._create_local_routes())

        # 添加WebSocket支持
        self._add_websocket_routes(app)
        
        # 挂载WebServer的前端静态文件（在根路径路由之前）
        self._mount_static_files(app)
        
        # 添加根路径路由
        self._add_root_routes(app)

        # 全局异常处理
        self._setup_exception_handlers(app)

        return app

    def _include_lampbot_routes(self, app: FastAPI) -> None:
        """引入WebServer的路由"""
        # 添加WebServer/backend路径到sys.path
        webserver_backend_path = os.path.join(os.path.dirname(__file__), '..', 'WebServer', 'backend')
        if os.path.exists(webserver_backend_path) and webserver_backend_path not in sys.path:
            sys.path.insert(0, webserver_backend_path)
            print(f"[WebServer] 添加路径到sys.path: {webserver_backend_path}")

        try:
            from WebServer.backend import pc_api
            app.include_router(pc_api.router, tags=["PC API"])
            print("[WebServer] 成功挂载 pc_api 路由")
        except Exception as e:
            print(f"[WebServer] 未能挂载 pc_api 路由：{e}")

        try:
            from WebServer.backend import mobile_api
            if hasattr(mobile_api, "router"):
                app.include_router(mobile_api.router, tags=["Mobile API"])
                print("[WebServer] 成功挂载 mobile_api 路由")
        except Exception as e:
            print(f"[WebServer] 未能挂载 mobile_api 路由：{e}")
            # 作为降级方案，直接挂载视频流路由，确保 /api/video 可用
            try:
                from WebServer.backend.routers import video_router
                app.include_router(video_router, tags=["Video API"])
                print("[WebServer] 降级: 成功挂载 video_stream 路由")
            except Exception as e2:
                print(f"[WebServer] 降级也失败，未能挂载 video_stream 路由：{e2}")

        # 挂载通用实时数据与视频流路由（提供大页面接口所需的API）
        try:
            from WebServer.backend.routers import realtime_router
            app.include_router(realtime_router, tags=["Realtime API"])
            print("[WebServer] 成功挂载 realtime_data 路由")
        except Exception as e:
            print(f"[WebServer] 未能挂载 realtime_data 路由：{e}")

    # 注意：正常情况下由 mobile_api 统一引入视频流路由

        if self.include_mock:
            try:
                from WebServer.backend.mock_api import router as mock_api_router
                app.include_router(mock_api_router, tags=["Mock API"])
                print("[WebServer] 成功挂载 mock_api 路由")
            except Exception as e:
                print(f"[WebServer] 未能挂载 mock_api 路由：{e}")

    def _create_local_routes(self) -> APIRouter:
        """创建本地适配路由"""
        router = APIRouter(prefix="/api", tags=["Local API"])

        @router.get("/health")
        async def health_check(request: Request):
            """健康检查"""
            device = request.scope.get("device_type", "unknown")
            ctx: AppContext = request.app.state.ctx
            services = ctx.get_service_status()
            return {
                "status": "ok",
                "device_type": device,
                "services": services,
                "timestamp": __import__('time').time()
            }

        # 注意：/api/device/status 已由 realtime_data 路由提供
        # 本地版本保留在 /api/device/status/local 以便调试
        @router.get("/device/status/local")
        async def get_device_status(ctx: AppContext = Depends(get_app_context)):
            """获取设备状态"""
            metrics = ctx.get_metrics()
            services = ctx.get_service_status()
            return {
                "online": services.get("video_stream", False),
                "lastSeen": metrics.get("last_seen"),
                "batteryLevel": metrics.get("battery_level", 100),
                "charging": metrics.get("charging", False),
                "services": services
            }

        @router.get("/video/local")
        async def video_stream_endpoint(ctx: AppContext = Depends(get_app_context)):
            """视频流接口（本地调试版）"""
            try:
                # 首先尝试使用本地video_stream
                if ctx.video_stream is not None:
                    def generate_local_mjpeg() -> Generator[bytes, None, None]:
                        try:
                            while True:
                                frame = None
                                if hasattr(ctx.video_stream, 'get_latest_frame'):
                                    frame = ctx.video_stream.get_latest_frame()
                                elif hasattr(ctx.video_stream, 'current_frame'):
                                    frame = ctx.video_stream.current_frame
                                if frame is not None and isinstance(frame, np.ndarray):
                                    _, buffer = cv2.imencode('.jpg', frame)
                                    frame_bytes = buffer.tobytes()
                                    yield (b'--frame\r\n'
                                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                                else:
                                    blank = np.zeros((480, 640, 3), dtype=np.uint8)
                                    _, buffer = cv2.imencode('.jpg', blank)
                                    yield (b'--frame\r\n'
                                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                                import time; time.sleep(1/30)
                        except Exception as e:
                            print(f"视频流生成错误: {e}")
                            return
                    return StreamingResponse(generate_local_mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame")
                # 使用WebServer摄像头
                from WebServer.backend.video_stream import camera
                def generate_webserver_mjpeg() -> Generator[bytes, None, None]:
                    try:
                        import time
                        while True:
                            frame_bytes = camera.read()
                            if frame_bytes:
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                            else:
                                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                                _, buffer = cv2.imencode('.jpg', blank)
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                            time.sleep(1/30)
                    except Exception as e:
                        print(f"WebServer视频流生成错误: {e}")
                        return
                return StreamingResponse(generate_webserver_mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame")
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"视频流服务错误: {str(e)}")

        @router.post("/control/posture/{action}")
        async def posture_control(action: str, ctx: AppContext = Depends(get_app_context)):
            """姿势监控控制"""
            if ctx.posture_monitor is None:
                raise HTTPException(status_code=503, detail="姿势监控服务未初始化")
            try:
                if action == "start":
                    result = ctx.posture_monitor.start()
                    return {"status": "success" if result else "failed", "action": action}
                elif action == "stop":
                    result = ctx.posture_monitor.stop()
                    return {"status": "success" if result else "failed", "action": action}
                else:
                    raise HTTPException(status_code=400, detail="不支持的操作")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")

        @router.get("/emotion/status")
        async def get_emotion_status(ctx: AppContext = Depends(get_app_context)):
            """获取情绪检测状态"""
            if ctx.emotion_detector is None:
                raise HTTPException(status_code=503, detail="情绪检测服务未初始化")
            try:
                return {
                    "is_face_detected": ctx.emotion_detector.is_face_detected,
                    "face_area": ctx.emotion_detector.face_area,
                    "emotion_type": ctx.emotion_detector.emotion_type,
                    "emotion_confidence": ctx.emotion_detector.emotion_confidence,
                    "status": "active" if ctx.emotion_detector.cap is not None else "inactive"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"获取情绪检测状态失败: {str(e)}")

        @router.post("/emotion/control/{action}")
        async def control_emotion_detection(action: str, ctx: AppContext = Depends(get_app_context)):
            """情绪检测控制"""
            if ctx.emotion_detector is None:
                raise HTTPException(status_code=503, detail="情绪检测服务未初始化")
            try:
                if action == "start":
                    result = ctx.emotion_detector.start()
                    return {"status": "success" if result else "failed", "action": action}
                elif action == "stop":
                    ctx.emotion_detector.stop()
                    return {"status": "success", "action": action}
                else:
                    raise HTTPException(status_code=400, detail="不支持的操作")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")

        return router

    def _add_root_routes(self, app: FastAPI) -> None:
        """添加根路径路由"""
        @app.get("/", tags=["Root"])
        async def root(request: Request):
            """根路径 - 智能重定向或返回API信息"""
            # 获取Accept头，确定请求类型
            accept = request.headers.get("Accept", "")
            
            # 如果是浏览器请求HTML，重定向到对应前端
            if "text/html" in accept:
                device = request.scope.get("device_type", "unknown")
                if device == "mobile":
                    return RedirectResponse(url="/mobile/")
                else:
                    return RedirectResponse(url="/pc/")
            
            # API请求，返回API信息
            return {
                "message": "智能台灯后端服务 (FastAPI)",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/api/health",
                "video_stream": "/api/video",
                "device_status": "/api/device/status",
                "pc_client": "/pc/",
                "mobile_client": "/mobile/"
            }
            
        # 移动端根路径处理
        @app.get("/mobile")
        @app.get("/mobile/")
        async def mobile_root():
            """移动端根路径"""
            index_path = os.path.join(
                os.path.dirname(__file__), '..', 'WebServer', 'frontend_mobile', 'dist', 'index.html'
            )
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                return JSONResponse({"error": "移动端前端不可用"}, status_code=404)
                
        # 前端客户端路由将由自定义处理函数处理
        @app.get("/mobile/{path:path}")
        async def serve_mobile_spa(path: str):
            """处理移动端SPA路由"""
            # 优先处理资源文件路径
            if path.startswith("assets/") or path.startswith("charts/"):
                # 不在这里处理资源文件
                raise HTTPException(status_code=404)
            
            # 非资源路径，返回index.html
            index_path = os.path.join(
                os.path.dirname(__file__), '..', 'WebServer', 'frontend_mobile', 'dist', 'index.html'
            )
            
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                return JSONResponse({"error": "移动端前端不可用"}, status_code=404)
        
        # PC端根路径处理
        @app.get("/pc")
        @app.get("/pc/")
        async def pc_root():
            """PC端根路径"""
            index_path = os.path.join(
                os.path.dirname(__file__), '..', 'WebServer', 'frontend_pc', 'dist', 'index.html'
            )
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                return JSONResponse({"error": "PC端前端不可用"}, status_code=404)
                
        @app.get("/pc/{path:path}")
        async def serve_pc_spa(path: str):
            """处理PC端SPA路由"""
            # 优先处理资源文件路径
            if path.startswith("assets/"):
                # 不在这里处理资源文件
                raise HTTPException(status_code=404)
            
            # 非资源路径，返回index.html
            index_path = os.path.join(
                os.path.dirname(__file__), '..', 'WebServer', 'frontend_pc', 'dist', 'index.html'
            )
            
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                return JSONResponse({"error": "PC端前端不可用"}, status_code=404)

        @app.get("/favicon.ico", include_in_schema=False)
        async def favicon():
            """处理favicon请求"""
            from fastapi import Response
            return Response(status_code=204)

    def _setup_exception_handlers(self, app: FastAPI) -> None:
        """设置异常处理器"""
        @app.exception_handler(404)
        async def not_found_handler(request, exc):
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "资源不存在",
                    "path": request.url.path
                }
            )

        @app.exception_handler(500)
        async def server_error_handler(request, exc):
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "服务器内部错误",
                    "detail": str(exc)
                }
            )

    def _add_websocket_routes(self, app: FastAPI) -> None:
        """添加WebSocket支持"""
        try:
            from WebServer.backend.websocket_manager import manager as ws_manager
            
            @app.websocket("/ws")
            async def websocket_endpoint(websocket: WebSocket, ctx: AppContext = None):
                await ws_manager.connect(websocket)
                try:
                    if ctx:
                        # 发送初始状态
                        await ws_manager.send_personal_message({
                            "type": "init",
                            "services": ctx.get_service_status(),
                            "metrics": ctx.get_metrics()
                        }, websocket)
                    
                    # 持续接收消息
                    while True:
                        data = await websocket.receive_text()
                        try:
                            message = json.loads(data)
                            # 处理消息...
                            
                            # 回显消息
                            await ws_manager.send_personal_message({
                                "type": "echo",
                                "message": message
                            }, websocket)
                        except Exception as e:
                            await ws_manager.send_personal_message({
                                "type": "error",
                                "message": str(e)
                            }, websocket)
                except Exception as e:
                    print(f"[WebSocket] 错误: {str(e)}")
                finally:
                    ws_manager.disconnect(websocket)
                
            print("[WebServer] 成功挂载WebSocket支持")

            # 兼容前端期望的 /ws/realtime 路径
            @app.websocket("/ws/realtime")
            async def websocket_endpoint_realtime(websocket: WebSocket):
                # 复用相同的管理器与逻辑
                await ws_manager.connect(websocket)
                try:
                    # 发送一次初始化信息（若可获取到上下文）
                    try:
                        ctx: AppContext = websocket.app.state.ctx  # type: ignore
                        await ws_manager.send_personal_message({
                            "type": "init",
                            "services": ctx.get_service_status() if ctx else {},
                            "metrics": ctx.get_metrics() if ctx else {}
                        }, websocket)
                    except Exception:
                        pass

                    while True:
                        data = await websocket.receive_text()
                        try:
                            message = json.loads(data)
                            await ws_manager.send_personal_message({
                                "type": "echo",
                                "message": message
                            }, websocket)
                        except Exception as e:
                            await ws_manager.send_personal_message({
                                "type": "error",
                                "message": str(e)
                            }, websocket)
                except Exception as e:
                    print(f"[WebSocket] 错误: {str(e)}")
                finally:
                    ws_manager.disconnect(websocket)

            # 启动后台广播任务，定期推送姿势/情绪到所有连接，驱动前端实时更新
            @app.on_event("startup")
            async def _start_ws_broadcast_task():
                import asyncio
                async def _broadcast_loop():
                    while True:
                        try:
                            ctx: AppContext = app.state.ctx  # type: ignore
                            posture_score = 50
                            emotion = "neutral"
                            emotion_conf = 0.0

                            # 读取姿势分数
                            try:
                                pm = getattr(ctx, 'posture_monitor', None)
                                if pm and hasattr(pm, 'pose_result'):
                                    pose_res = pm.pose_result or {}
                                    angle = pose_res.get('angle')
                                    if angle is None:
                                        posture_score = 50
                                    else:
                                        posture_score = int(max(0, min(100, 100 - angle * 1.2)))
                            except Exception:
                                posture_score = 50

                            # 读取情绪
                            try:
                                ed = getattr(ctx, 'emotion_detector', None)
                                if ed and hasattr(ed, 'emotion_type') and hasattr(ed, 'emotion_confidence'):
                                    emotion = (ed.emotion_type or 'neutral').lower()
                                    emotion_conf = float(ed.emotion_confidence or 0.0)
                                else:
                                    pm = getattr(ctx, 'posture_monitor', None)
                                    if pm and hasattr(pm, 'emotion_result') and pm.emotion_result:
                                        raw = pm.emotion_result.get('emotion')
                                        if isinstance(raw, str):
                                            emotion = raw.lower()
                            except Exception:
                                pass

                            # 统一将unknown/unkown视为neutral
                            if not emotion or emotion in ("unknown", "unkown"):
                                emotion = "neutral"

                            # 情绪变化“和缓”：
                            # - 对置信度做指数平滑
                            # - 对类别做短暂保持：连续N次不同才切换
                            state = getattr(app.state, '_emo_state', {
                                'label': None,
                                'conf': 0.0,
                                'pending': None,
                                'pending_count': 0
                            })
                            # 调高平滑系数，使置信度对新值更敏感
                            alpha = 0.85  # 越大越敏感（此前为0.3 → 0.6 → 0.85）
                            # 平滑置信度
                            smoothed_conf = (1 - alpha) * state.get('conf', 0.0) + alpha * (emotion_conf or 0.0)
                            # 类别：立即切换，最大灵敏度
                            state['label'] = emotion
                            state['pending'] = None
                            state['pending_count'] = 0
                            state['conf'] = smoothed_conf
                            app.state._emo_state = state

                            # 当前分数对前端展示+20
                            posture_score = max(0, min(100, posture_score + 20))

                            payload = {
                                'timestamp': __import__('time').time(),
                                'posture_score': posture_score,
                                'eye_distance': 40,  # 暂无真实用眼模块，使用占位值
                                'emotion': state['label'],
                                'emotion_confidence': state['conf']
                            }
                            await ws_manager.broadcast(payload)
                        except Exception as e:
                            print(f"[WebSocket] 广播错误: {e}")
                        await asyncio.sleep(1.0)

                # 创建后台任务
                import asyncio as _asyncio
                app.state._ws_broadcast_task = _asyncio.create_task(_broadcast_loop())

            @app.on_event("shutdown")
            async def _stop_ws_broadcast_task():
                task = getattr(app.state, '_ws_broadcast_task', None)
                if task:
                    try:
                        task.cancel()
                    except Exception:
                        pass
        except Exception as e:
            print(f"[WebServer] 无法挂载WebSocket支持: {str(e)}")
    
    def _mount_static_files(self, app: FastAPI) -> None:
        """挂载静态文件"""
        # 获取路径
        mobile_dist_path = os.path.join(os.path.dirname(__file__), '..', 'WebServer', 'frontend_mobile', 'dist')
        pc_dist_path = os.path.join(os.path.dirname(__file__), '..', 'WebServer', 'frontend_pc', 'dist')

        # 调试路径信息
        print(f"[DEBUG] Mobile dist path: {os.path.abspath(mobile_dist_path)}")
        print(f"[DEBUG] Mobile dist exists: {os.path.exists(mobile_dist_path)}")

        # 使用 StaticFiles 挂载静态资源，避免阻塞事件循环
        try:
            mobile_assets = os.path.join(mobile_dist_path, 'assets')
            mobile_charts = os.path.join(mobile_dist_path, 'charts')
            pc_assets = os.path.join(pc_dist_path, 'assets')
            static_root = os.path.join(os.path.dirname(__file__), '..', 'static')

            if os.path.isdir(mobile_assets):
                app.mount("/mobile/assets", StaticFiles(directory=mobile_assets), name="mobile_assets")
                # 兼容旧路径
                app.mount("/mobile_assets", StaticFiles(directory=mobile_assets), name="mobile_assets_compat")
            if os.path.isdir(mobile_charts):
                app.mount("/mobile/charts", StaticFiles(directory=mobile_charts), name="mobile_charts")
                # 兼容旧路径
                app.mount("/mobile_charts", StaticFiles(directory=mobile_charts), name="mobile_charts_compat")
            if os.path.isdir(pc_assets):
                app.mount("/pc/assets", StaticFiles(directory=pc_assets), name="pc_assets")
                # 兼容旧路径（PC端构建通常在根用 /assets 引用）
                app.mount("/assets", StaticFiles(directory=pc_assets), name="pc_assets_root")
            # 提供通用静态目录（用于姿态图片等）
            if os.path.isdir(static_root):
                app.mount("/static", StaticFiles(directory=static_root), name="static_root")
        except Exception as e:
            print(f"[WebServer] 挂载静态资源失败: {e}")

        # 打印成功信息
        if os.path.exists(mobile_dist_path):
            print(f"[WebServer] 成功设置移动端前端路径: {mobile_dist_path}")
        else:
            print(f"[WebServer] 警告: 移动端前端构建目录不存在: {mobile_dist_path}")

        if os.path.exists(pc_dist_path):
            print(f"[WebServer] 成功设置PC端前端路径: {pc_dist_path}")
        else:
            print(f"[WebServer] 警告: PC端前端构建目录不存在: {pc_dist_path}")

        # 添加重定向路由
        @app.get("/redirect")
        async def redirect_to_client(request: Request):
            """根据设备类型重定向到对应前端"""
            device = request.scope.get("device_type", "unknown")
            if device == "mobile":
                return RedirectResponse(url="/mobile/")
            else:
                return RedirectResponse(url="/pc/")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
        """启动服务器"""
        import uvicorn
        import logging
        import sys
        
        # 使用最简单的方式启动，避免日志配置冲突
        try:
            print(f"正在启动服务器: http://{host}:{port}")
            
            # 禁用uvicorn自己的日志配置
            uvicorn.run(
                self.app, 
                host=host, 
                port=port, 
                reload=reload,
                log_config=None,  # 禁用内置日志配置
                use_colors=False,  # 禁用颜色输出
                access_log=False   # 禁用访问日志
            )
        except Exception as e:
            print(f"服务器启动失败: {e}")
            # 最后的备用方案 - 手动创建服务器
            try:
                import asyncio
                # 动态导入以避免静态检查错误
                _hypercorn = __import__('hypercorn')
                _asyncio_mod = __import__('hypercorn.asyncio', fromlist=['asyncio'])
                HypercornConfig = getattr(__import__('hypercorn', fromlist=['Config']), 'Config')

                print("尝试使用Hypercorn启动服务器...")
                config = HypercornConfig()
                config.bind = [f"{host}:{port}"]
                asyncio.run(_asyncio_mod.serve(self.app, config))
            except ImportError:
                print("Hypercorn不可用，尝试直接运行...")
                # 如果都失败了，至少保持程序运行
                print("服务器无法启动，但其他服务已初始化完成")
                try:
                    while True:
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("程序被用户中断")
