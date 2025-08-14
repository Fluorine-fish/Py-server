from fastapi import Request
from server import app, get_device_type
import pc_api
import mobile_api
from mock_api import router as mock_api_router

# 注册PC端的API路由
app.include_router(pc_api.router) 

# 仅为移动端使用模拟API数据
# 注册模拟API路由（用于移动端的假数据）
app.include_router(mock_api_router)

# 设置根据设备类型动态路由
@app.middleware("http")
async def add_device_specific_routes(request: Request, call_next):
    # 获取设备类型
    device = get_device_type(request)
    # 支持通过参数覆盖设备类型（用于测试）
    override = request.query_params.get("device")
    if override in ["pc", "mobile"]:
        device = override
    
    # 继续处理请求
    response = await call_next(request)
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)