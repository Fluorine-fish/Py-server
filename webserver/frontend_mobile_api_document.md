# Lampbot 移动端后端 API 接口文档

## 文档概述

本文档详细说明了 Lampbot 智能台灯移动端前端所需的后端 API 接口规范。接口按照页面功能和数据类型进行分类，优先列出当前有假数据注入的接口。

## 目录
- [大页面接口](#大页面接口)
  - [首页视频流传输](#1-首页视频流传输)
  - [首页实时数据获取](#2-首页实时数据获取)
- [子页面接口](#子页面接口)
  - [坐姿检测页面](#3-坐姿检测页面)
  - [用眼监护页面](#4-用眼监护页面)
  - [情绪监护页面](#5-情绪监护页面)
  - [家长监护页面](#6-家长监护页面)
- [工具功能接口](#工具功能接口)
  - [远程控制功能](#7-远程控制功能)
  - [设置页面功能](#8-设置页面功能)
- [实时数据通信](#实时数据通信)
  - [WebSocket实时推送](#9-websocket-实时推送)
- [数据类型分类总结](#数据类型分类总结)

---

## 大页面接口

### 1. 首页视频流传输

**功能位置**: `Home.vue` 视频区域  
**优先级**: 高 🔥  
**前端调用方式**:
```javascript
const videoUrl = ref('/api/video');
```

**后端需要注册的函数**:

#### `GET /api/video`
**功能**: 实时传输摄像头视频流  
**返回类型**: `video/jpeg` 流或 `multipart/x-mixed-replace`  
**实现建议**: 使用 FastAPI StreamingResponse

```python
from fastapi.responses import StreamingResponse
import cv2

@app.get("/api/video")
async def video_stream():
    """视频流接口"""
    def generate():
        # 实现视频流生成逻辑
        pass
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
```

---

### 2. 首页实时数据获取

**功能位置**: `Home.vue` 统计区域  
**优先级**: 高 🔥  
**现有假数据注入**: ✅ (monitorStore 中有模拟数据)

**前端调用方式**:
```javascript
await deviceStore.fetchDeviceStatus();
await monitorStore.fetchPostureData();
await monitorStore.fetchEyeData();
await monitorStore.fetchEmotionData();
```

**后端需要注册的函数**:

#### `GET /api/device/status`
**功能**: 获取设备在线状态和基本信息
```json
{
  "online": true,
  "lastSeen": "2025-08-14T10:30:00Z",
  "batteryLevel": 85,
  "charging": true
}
```

#### `GET /api/monitor/posture`
**功能**: 获取实时坐姿检测数据
```json
{
  "currentScore": 85,
  "warnCount": 3,
  "averageScore": 78,
  "lastDetected": "2025-08-14T10:30:00Z"
}
```

#### `GET /api/monitor/eye`
**功能**: 获取实时用眼监测数据
```json
{
  "eyeDistance": 45,
  "screenTime": 7200,
  "breakReminder": "每30分钟",
  "lastWarning": "2025-08-14T10:15:00Z"
}
```

#### `GET /api/monitor/emotion`
**功能**: 获取实时情绪检测数据
```json
{
  "currentEmotion": "happy",
  "confidence": 0.92,
  "history": [
    {
      "time": "2025-08-14T10:00:00Z",
      "emotion": "neutral",
      "duration": 1200
    }
  ]
}
```

---

## 子页面接口

### 3. 坐姿检测页面

**功能位置**: `Posture.vue`  
**优先级**: 高 🔥  
**现有假数据注入**: ✅ (fetchPostureHistoryByTimeRange 中有模拟数据)

**后端需要注册的函数**:

#### `GET /api/monitor/posture/history`
**功能**: 获取坐姿历史统计数据  
**参数**: `timeRange` (day/week/month)

**响应示例**:
```json
{
  "goodTime": "3.2",
  "mildTime": "1.2", 
  "badTime": "0.6",
  "goodRate": "64",
  "problemTimeSlot": "下午3-5点",
  "improvementMessage": "今天坐姿良好，请继续保持。"
}
```

#### `GET /api/monitor/posture/distribution`
**功能**: 获取坐姿时间分布数据  
**参数**: `timeRange` (day/week/month)

**响应示例**:
```json
{
  "data": [2, 1, 0, 3, 4, 2, 1, 0, 5, 3, 1, 0],
  "labels": ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]
}
```

#### `GET /api/monitor/posture/images`
**功能**: 获取坐姿检测图像记录  
**参数**: `page` (页码), `limit` (每页数量)

**响应示例**:
```json
{
  "data": [
    {
      "id": "img_1_1",
      "url": "/static/posture/img_001.jpg",
      "timestamp": "2025-08-14T10:30:00Z",
      "score": 85,
      "status": "good"
    }
  ],
  "total": 120,
  "page": 1,
  "limit": 6
}
```

#### `GET /api/monitor/posture/improvement`
**功能**: 获取坐姿改善建议
```json
{
  "problemTimeSlot": "下午3-5点",
  "improvementMessage": "本周坐姿改善效果明显，请继续保持良好习惯。",
  "suggestions": [
    "建议在下午时段设置提醒",
    "适当调整椅子高度",
    "保持背部挺直"
  ]
}
```

---

### 4. 用眼监护页面

**功能位置**: `Eye.vue` 多标签页面  
**优先级**: 高 🔥  
**现有假数据注入**: ✅ (组件内有图表模拟数据)

**后端需要注册的函数**:

#### `GET /api/monitor/eye/trends`
**功能**: 获取护眼趋势图表数据
```json
{
  "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
  "datasets": [
    {
      "label": "眨眼频率",
      "data": [15, 18, 22, 19, 16, 20],
      "borderColor": "#4CAF50"
    },
    {
      "label": "用眼距离",
      "data": [45, 42, 38, 41, 44, 46],
      "borderColor": "#2196F3"
    }
  ]
}
```

#### `GET /api/monitor/eye/environment`
**功能**: 获取光照环境雷达图数据
```json
{
  "labels": ["环境光", "屏幕亮度", "对比度", "色温", "反射", "眩光"],
  "data": [80, 75, 85, 90, 70, 65],
  "optimal": [85, 80, 80, 85, 75, 70]
}
```

#### `GET /api/monitor/eye/heatmap`
**功能**: 获取用眼时间热力图数据
```json
{
  "hours": ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
  "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
  "data": [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
  ]
}
```

#### `GET /api/monitor/eye/data`
**功能**: 获取详细用眼数据
```json
{
  "focus_time": "25",
  "blink_rate": "18",
  "distance": "45",
  "eyeStrain": "low",
  "recommendations": [
    "每20分钟远眺20秒",
    "调整屏幕亮度到舒适水平"
  ]
}
```

---

### 5. 情绪监护页面

**功能位置**: `Emotion.vue` 多标签页面  
**优先级**: 高 🔥  
**现有假数据注入**: ✅ (组件内有图表模拟数据)

**后端需要注册的函数**:

#### `GET /api/monitor/emotion/trends`
**功能**: 获取情绪趋势图数据
```json
{
  "labels": ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
  "data": [0.7, 0.8, 0.75, 0.9, 0.85, 0.8, 0.82, 0.78],
  "emotions": ["neutral", "happy", "focused", "happy", "focused", "happy", "happy", "neutral"]
}
```

#### `GET /api/monitor/emotion/radar`
**功能**: 获取情绪雷达图数据
```json
{
  "labels": ["专注度", "愉悦度", "放松度", "疲劳度", "压力值"],
  "current": [85, 75, 60, 30, 25],
  "average": [80, 70, 65, 35, 30],
  "optimal": [90, 80, 70, 20, 15]
}
```

#### `GET /api/monitor/emotion/distribution`
**功能**: 获取情绪时段分布数据
```json
{
  "timeSlots": ["上午", "中午", "下午", "晚上"],
  "emotions": {
    "happy": [30, 25, 20, 15],
    "neutral": [40, 45, 50, 55],
    "sad": [20, 20, 20, 20],
    "focused": [10, 10, 10, 10]
  }
}
```

#### `GET /api/monitor/emotion/heatmap`
**功能**: 获取周情绪热力图数据
```json
{
  "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
  "hours": ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
  "data": [
    [0.8, 0.7, 0.9, 0.85, 0.75, 0.8, 0.9, 0.85, 0.7, 0.75, 0.8, 0.85, 0.9, 0.85, 0.8, 0.75, 0.7],
    [0.75, 0.8, 0.85, 0.9, 0.8, 0.85, 0.9, 0.8, 0.75, 0.8, 0.85, 0.9, 0.85, 0.8, 0.75, 0.8, 0.75]
  ]
}
```

---

### 6. 家长监护页面

**功能位置**: `Guardian.vue`  
**优先级**: 中等  
**现有假数据注入**: ✅ (复用 monitorStore 数据)

**后端需要注册的函数**:

#### `GET /api/monitor/guardian/report`
**功能**: 获取监护报告图表数据
```json
{
  "labels": ["坐姿", "用眼", "情绪", "学习时长"],
  "scores": [85, 75, 80, 90],
  "warnings": {
    "posture": 3,
    "eye": 2,
    "emotion": 1,
    "total": 6
  },
  "recommendations": [
    "坐姿表现良好，继续保持",
    "建议增加用眼休息时间",
    "情绪状态稳定"
  ]
}
```

---

## 工具功能接口

### 7. 远程控制功能

**功能位置**: `Remote.vue` 控制面板  
**优先级**: 中等  
**现有假数据注入**: ✅ (组件内有初始值)

**后端需要注册的函数**:

#### `POST /api/control/light/brightness`
**功能**: 调整灯光亮度
**请求体**:
```json
{
  "brightness": 75
}
```
**响应**:
```json
{
  "success": true,
  "message": "亮度调整成功",
  "currentBrightness": 75
}
```

#### `POST /api/control/light/color`
**功能**: 调整色温
**请求体**:
```json
{
  "colorTemperature": 4000
}
```
**响应**:
```json
{
  "success": true,
  "message": "色温调整成功",
  "currentTemperature": 4000
}
```

#### `POST /api/control/light/power`
**功能**: 开关控制
**请求体**:
```json
{
  "power": true
}
```
**响应**:
```json
{
  "success": true,
  "message": "灯光已开启",
  "powerState": true
}
```

#### `GET /api/device/settings`
**功能**: 获取当前设备设置
```json
{
  "brightness": 70,
  "colorTemperature": 5500,
  "autoAdjust": true,
  "power": true
}
```

---

### 8. 设置页面功能

**功能位置**: `Settings.vue` 及子页面  
**优先级**: 低

**后端需要注册的函数**:

#### `GET /api/user/info`
**功能**: 获取用户基本信息
```json
{
  "username": "家长用户",
  "avatar": "/static/avatars/default.jpg",
  "phone": "138****1234",
  "email": "user@example.com"
}
```

#### `GET /api/user/notifications`
**功能**: 获取通知设置
```json
{
  "postureReminder": true,
  "eyeReminder": true,
  "emotionAlert": true,
  "dailyReport": true,
  "reminderInterval": 30,
  "quietHours": {
    "enabled": true,
    "start": "22:00",
    "end": "07:00"
  }
}
```

#### `POST /api/user/notifications`
**功能**: 更新通知设置
**请求体**: 同上获取接口的响应格式
**响应**:
```json
{
  "success": true,
  "message": "通知设置已更新"
}
```

#### `GET /api/device-info`
**功能**: 获取设备详细信息
```json
{
  "deviceId": "LAMP_001",
  "version": "1.2.3",
  "model": "智能台灯Pro",
  "manufacturer": "Lampbot",
  "status": "online",
  "lastUpdate": "2025-08-14T09:00:00Z",
  "features": ["坐姿检测", "用眼监护", "情绪识别", "远程控制"]
}
```

---

## 实时数据通信

### 9. WebSocket 实时推送

**功能位置**: 全局实时数据更新  
**优先级**: 高 🔥  
**现有假数据注入**: ✅ (WebSocketManager 已实现)

**后端需要注册的函数**:

#### WebSocket 连接: `ws://host/ws/realtime`
**功能**: 实时推送监测数据更新

**推送数据格式**:
```json
{
  "type": "monitor_update",
  "data": {
    "posture_score": 85,
    "eye_distance": 45,
    "emotion": "happy",
    "emotion_confidence": 0.92,
    "timestamp": "2025-08-14T10:30:00Z"
  }
}
```

**连接状态消息**:
```json
{
  "type": "connection_status",
  "data": {
    "status": "connected",
    "clientId": "client_12345",
    "timestamp": "2025-08-14T10:30:00Z"
  }
}
```

**错误消息**:
```json
{
  "type": "error",
  "data": {
    "message": "设备连接失败",
    "code": "DEVICE_OFFLINE",
    "timestamp": "2025-08-14T10:30:00Z"
  }
}
```

---

## 数据类型分类总结

### 📹 视频流类型
- **接口**: `/api/video`
- **格式**: MJPEG 视频流
- **用途**: 实时监控画面显示

### 📊 JSON 数据类型
- **设备状态数据**: 在线状态、电池信息、设备配置
- **监控统计数据**: 坐姿、用眼、情绪的实时和历史数据
- **图表数据**: 趋势图、雷达图、热力图、分布图数据
- **用户设置数据**: 个人信息、通知偏好、系统配置

### 🖼️ 图片文件类型
- **坐姿检测截图**: `/static/posture/*.jpg`
- **用户头像**: `/static/avatars/*.jpg`
- **占位图片**: `/static/mobile/placeholder.jpg`

### ⚡ 实时流数据类型
- **WebSocket JSON 消息**: 实时监测数据推送
- **连接状态管理**: 自动重连、错误处理

---

## 优先级实现建议

### 🔥 高优先级 (立即实现)
1. **视频流接口** - 核心功能，用户最直观的体验
2. **实时数据接口** - 替换现有模拟数据
3. **WebSocket 推送** - 实现真正的实时更新

### 🔶 中等优先级 (第二阶段)
1. **历史数据查询** - 图表展示功能
2. **远程控制** - 实用工具功能
3. **图像记录** - 历史回顾功能

### 🔷 低优先级 (后续优化)
1. **用户设置管理** - 个性化配置
2. **设备信息查询** - 系统信息展示
3. **通知设置** - 提醒功能配置

---

## 接口实现注意事项

### 错误处理
所有接口都应该包含统一的错误响应格式：
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息"
  }
}
```

### 数据验证
- 对输入参数进行严格验证
- 返回数据格式保持一致性
- 时间格式统一使用 ISO 8601 标准

### 性能优化
- 图表数据支持缓存机制
- 图像文件支持压缩和懒加载
- WebSocket 连接支持心跳检测

### 安全考虑
- API 访问需要认证机制
- 敏感数据需要加密传输
- 设备控制权限需要验证

---

**文档版本**: v1.0  
**最后更新**: 2025年8月14日  
**维护者**: Lampbot 开发团队
