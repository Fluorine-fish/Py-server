"""
轻量版启动脚本：仅启动 WebServer（含前端静态资源与 mock API），避免初始化摄像头/姿势/情绪等重服务，便于前端联调。
用法：python light_server.py
"""
import os
import traceback
from config import OPEN_HOST, OPEN_PORT
from webserver.context import AppContext
from webserver.server import WebServer


def main():
    print("========== Py-server 轻量Web 启动 ==========")
    # 不初始化任何重服务，直接给空上下文
    ctx = AppContext()
    # include_mock=True 将挂载 /api 下的 mock 路由
    web = WebServer(ctx=ctx, include_mock=True)
    host = os.environ.get('HOST', OPEN_HOST)
    try:
        port = int(os.environ.get('PORT', OPEN_PORT))
    except Exception:
        port = OPEN_PORT
    print(f"Web: http://{host}:{port}\nDocs: http://{host}:{port}/docs")
    try:
        web.run(host=host, port=port, reload=False)
    except Exception as e:
        print(f"轻量Web启动失败: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
