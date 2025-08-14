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

        @router.get("/device/status")
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

        @router.get("/video")
        async def video_stream_endpoint(ctx: AppContext = Depends(get_app_context)):
            """视频流接口"""
            try:
                # 首先尝试使用本地video_stream
                if ctx.video_stream is not None:
                    def generate_local_mjpeg() -> Generator[bytes, None, None]:
                        try:
                            while True:
                                # 尝试从video_stream获取帧
                                frame = None
                                if hasattr(ctx.video_stream, 'get_latest_frame'):
                                    frame = ctx.video_stream.get_latest_frame()
                                elif hasattr(ctx.video_stream, 'current_frame'):
                                    frame = ctx.video_stream.current_frame
                                
                                if frame is not None:
                                    # 确保frame是numpy数组
                                    if isinstance(frame, np.ndarray):
                                        # 编码为JPEG
                                        _, buffer = cv2.imencode('.jpg', frame)
                                        frame_bytes = buffer.tobytes()
                                        
                                        yield (b'--frame\r\n'
                                               b'Content-Type: image/jpeg\r\n\r\n' + 
                                               frame_bytes + b'\r\n')
                                else:
                                    # 如果没有帧，使用空白帧
                                    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                                    _, buffer = cv2.imencode('.jpg', blank_frame)
                                    frame_bytes = buffer.tobytes()
                                    
                                    yield (b'--frame\r\n'
                                           b'Content-Type: image/jpeg\r\n\r\n' + 
                                           frame_bytes + b'\r\n')
                                
                                # 控制帧率
                                import time
                                time.sleep(1/30)  # 30fps
                        except Exception as e:
                            print(f"视频流生成错误: {e}")
                            return
                    
                    return StreamingResponse(
                        generate_local_mjpeg(),
                        media_type="multipart/x-mixed-replace; boundary=frame"
                    )
                
                # 如果本地video_stream不可用，尝试使用WebServer的camera
                else:
                    try:
                        from WebServer.backend.video_stream import camera
                        
                        def generate_webserver_mjpeg() -> Generator[bytes, None, None]:
                            try:
                                while True:
                                    frame_bytes = camera.read()
                                    
                                    if frame_bytes:
                                        yield (b'--frame\r\n'
                                               b'Content-Type: image/jpeg\r\n\r\n' + 
                                               frame_bytes + b'\r\n')
                                    else:
                                        # 如果没有帧，使用空白帧
                                        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                                        _, buffer = cv2.imencode('.jpg', blank_frame)
                                        frame_bytes = buffer.tobytes()
                                        
                                        yield (b'--frame\r\n'
                                               b'Content-Type: image/jpeg\r\n\r\n' + 
                                               frame_bytes + b'\r\n')
                                    
                                    # 控制帧率
                                    import time
                                    time.sleep(1/30)  # 30fps
                            except Exception as e:
                                print(f"WebServer视频流生成错误: {e}")
                                return
                        
                        return StreamingResponse(
                            generate_webserver_mjpeg(),
                            media_type="multipart/x-mixed-replace; boundary=frame"
                        )
                    except Exception as e:
                        print(f"无法加载WebServer的camera模块: {e}")
                        raise HTTPException(status_code=503, detail="视频流服务未初始化")
            
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"视频流服务错误: {str(e)}")

        @router.post("/control/posture/{action}")
        async def posture_control(
            action: str, 
            ctx: AppContext = Depends(get_app_context)
        ):
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
        async def control_emotion_detection(
            action: str, 
            ctx: AppContext = Depends(get_app_context)
        ):
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
        if os.path.exists(mobile_dist_path):
            assets_path = os.path.join(mobile_dist_path, 'assets')
            print(f"[DEBUG] Mobile assets path: {os.path.abspath(assets_path)}")
            print(f"[DEBUG] Mobile assets exists: {os.path.exists(assets_path)}")
            if os.path.exists(assets_path):
                print(f"[DEBUG] Mobile assets files: {os.listdir(assets_path)}")
        
        # 为移动端创建静态文件处理
        @app.get("/mobile/assets/{rest_path:path}")
        async def serve_mobile_assets(rest_path: str):
            """直接提供移动端资源文件"""
            try:
                print(f"[DEBUG] 请求移动端资源: {rest_path}")
                file_path = os.path.join(mobile_dist_path, "assets", rest_path)
                print(f"[DEBUG] 完整文件路径: {file_path}")
                print(f"[DEBUG] 文件是否存在: {os.path.exists(file_path)}")
                print(f"[DEBUG] 是否为文件: {os.path.isfile(file_path) if os.path.exists(file_path) else 'N/A'}")
                
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    print(f"[ERROR] 资源文件不存在: {rest_path} -> {file_path}")
                    raise HTTPException(status_code=404, detail=f"资源文件不存在: {rest_path}")
                    
                # 确定MIME类型
                mime_type = "application/octet-stream"
                if rest_path.endswith(".js"):
                    mime_type = "application/javascript"
                elif rest_path.endswith(".css"):
                    mime_type = "text/css"
                elif rest_path.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif rest_path.endswith(".png"):
                    mime_type = "image/png"
                elif rest_path.endswith(".jpg") or rest_path.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                    
                print(f"[DEBUG] MIME类型: {mime_type}")
                    
                # 读取文件内容
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                print(f"[DEBUG] 文件大小: {len(content)} bytes")
                return Response(content=content, media_type=mime_type)
            except Exception as e:
                print(f"提供移动端资源文件时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
            
        @app.get("/mobile/charts/{rest_path:path}")
        async def serve_mobile_charts(rest_path: str):
            """直接提供移动端图表文件"""
            try:
                file_path = os.path.join(mobile_dist_path, "charts", rest_path)
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    raise HTTPException(status_code=404, detail=f"图表文件不存在: {rest_path}")
                    
                # 确定MIME类型
                mime_type = "application/octet-stream"
                if rest_path.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif rest_path.endswith(".png"):
                    mime_type = "image/png"
                elif rest_path.endswith(".jpg") or rest_path.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                    
                # 读取文件内容
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                return Response(content=content, media_type=mime_type)
            except Exception as e:
                print(f"提供移动端图表文件时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 挂载移动端资源目录到根路径，保持兼容性
        @app.get("/mobile_assets/{rest_path:path}")
        async def serve_root_mobile_assets(rest_path: str):
            """直接提供根路径下的移动端资源文件（兼容性）"""
            try:
                file_path = os.path.join(mobile_dist_path, "assets", rest_path)
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    raise HTTPException(status_code=404, detail=f"资源文件不存在: {rest_path}")
                    
                # 确定MIME类型
                mime_type = "application/octet-stream"
                if rest_path.endswith(".js"):
                    mime_type = "application/javascript"
                elif rest_path.endswith(".css"):
                    mime_type = "text/css"
                elif rest_path.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif rest_path.endswith(".png"):
                    mime_type = "image/png"
                elif rest_path.endswith(".jpg") or rest_path.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                    
                # 读取文件内容
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                return Response(content=content, media_type=mime_type)
            except Exception as e:
                print(f"提供根路径移动端资源文件时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/mobile_charts/{rest_path:path}")
        async def serve_root_mobile_charts(rest_path: str):
            """直接提供根路径下的移动端图表文件（兼容性）"""
            try:
                file_path = os.path.join(mobile_dist_path, "charts", rest_path)
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    raise HTTPException(status_code=404, detail=f"图表文件不存在: {rest_path}")
                    
                # 确定MIME类型
                mime_type = "application/octet-stream"
                if rest_path.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif rest_path.endswith(".png"):
                    mime_type = "image/png"
                elif rest_path.endswith(".jpg") or rest_path.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                    
                # 读取文件内容
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                return Response(content=content, media_type=mime_type)
            except Exception as e:
                print(f"提供根路径移动端图表文件时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
            
        # 为PC端创建静态文件处理
        @app.get("/pc/assets/{rest_path:path}")
        async def serve_pc_assets(rest_path: str):
            """直接提供PC端资源文件"""
            try:
                file_path = os.path.join(pc_dist_path, "assets", rest_path)
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    raise HTTPException(status_code=404, detail=f"资源文件不存在: {rest_path}")
                    
                # 确定MIME类型
                mime_type = "application/octet-stream"
                if rest_path.endswith(".js"):
                    mime_type = "application/javascript"
                elif rest_path.endswith(".css"):
                    mime_type = "text/css"
                elif rest_path.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif rest_path.endswith(".png"):
                    mime_type = "image/png"
                elif rest_path.endswith(".jpg") or rest_path.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                    
                # 读取文件内容
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                return Response(content=content, media_type=mime_type)
            except Exception as e:
                print(f"提供PC端资源文件时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 挂载PC端资源目录到根路径，保持兼容性
        @app.get("/assets/{rest_path:path}")
        async def serve_root_pc_assets(rest_path: str):
            """直接提供根路径下的PC端资源文件（兼容性）"""
            try:
                file_path = os.path.join(pc_dist_path, "assets", rest_path)
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    raise HTTPException(status_code=404, detail=f"资源文件不存在: {rest_path}")
                    
                # 确定MIME类型
                mime_type = "application/octet-stream"
                if rest_path.endswith(".js"):
                    mime_type = "application/javascript"
                elif rest_path.endswith(".css"):
                    mime_type = "text/css"
                elif rest_path.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif rest_path.endswith(".png"):
                    mime_type = "image/png"
                elif rest_path.endswith(".jpg") or rest_path.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                    
                # 读取文件内容
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                return Response(content=content, media_type=mime_type)
            except Exception as e:
                print(f"提供根路径PC端资源文件时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
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
                import hypercorn.asyncio
                from hypercorn import Config as HypercornConfig
                
                print("尝试使用Hypercorn启动服务器...")
                config = HypercornConfig()
                config.bind = [f"{host}:{port}"]
                asyncio.run(hypercorn.asyncio.serve(self.app, config))
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
