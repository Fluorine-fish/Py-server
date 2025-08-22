import axios from 'axios';

// 全局请求控制：记录所有在途请求，支持路由切换时统一取消
const inflightControllers = new Set();

export function cancelAllRequests(reason = 'route-change') {
  for (const ctrl of inflightControllers) {
    try { ctrl.abort(new Error(reason)); } catch (_) {}
  }
  inflightControllers.clear();
}

// 创建axios实例
export const api = axios.create({
  // 开发使用相对路径，让Vite代理处理
  baseURL: '/api',
  timeout: 12000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 这里可以添加认证信息等
    // 为每个请求附加 AbortController，便于在页面切换时中止
    const ctrl = new AbortController();
    config.signal = config.signal || ctrl.signal;
    // 记录 controller，便于统一取消
    inflightControllers.add(ctrl);
    // 保存到配置，响应阶段移除
    config._abortController = ctrl;
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 清理记录
    if (response.config && response.config._abortController) {
      inflightControllers.delete(response.config._abortController);
    }
    return response.data;
  },
  error => {
    // 清理记录
    if (error.config && error.config._abortController) {
      inflightControllers.delete(error.config._abortController);
    }
    // 对被取消/超时的请求进行静默处理，避免快速切换时页面卡死或充斥错误日志
    const isAbort = error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError' || error?.message?.includes('aborted') || error?.config?.signal?.aborted;
    const isTimeout = error?.code === 'ECONNABORTED' || /timeout/i.test(error?.message || '');
    if (isAbort) {
      // 返回带标记的错误，调用方可选择忽略
      return Promise.reject(Object.assign(error, { __canceled__: true }));
    }
    if (isTimeout) {
      console.warn('API超时:', error?.config?.url || '');
      return Promise.reject(Object.assign(error, { __timeout__: true }));
    }
    console.error('API错误:', error);
    return Promise.reject(error);
  }
);

// 设备相关API
export const deviceApi = {
  // 获取设备信息
  getDeviceInfo() {
    return api.get('/device-info');
  },
  
  // 获取设备状态
  getDeviceStatus() {
    return api.get('/device/status');
  },
  
  // 获取设备设置
  getDeviceSettings() {
    return api.get('/device/settings');
  },
  
  // 更新设备设置
  updateDeviceSettings(settings) {
    return api.post('/device/settings', settings);
  }
};

// 监控相关API
export const monitorApi = {
  // 获取实时坐姿数据
  getPostureData() {
    return api.get('/monitor/posture');
  },
  
  // 获取坐姿历史记录
  getPostureHistory(params) {
    return api.get('/monitor/posture/history', { params });
  },
  
  // 获取坐姿时间占比数据
  getPostureTimeDistribution(params) {
    return api.get('/monitor/posture/distribution', { params });
  },
  
  // 获取坐姿图像记录
  getPostureImages(params) {
    return api.get('/monitor/posture/images', { params });
  },
  
  // 获取坐姿改善建议
  getPostureImprovement() {
    return api.get('/monitor/posture/improvement');
  },
  
  // 获取用眼数据
  getEyeData() {
    return api.get('/monitor/eye');
  },
  // 获取用眼趋势（Chart.js 友好结构）
  getEyeTrends(params) {
    return api.get('/monitor/eye/trends', { params });
  },
  // 获取用眼环境指标（雷达图）
  getEyeEnvironment(params) {
    return api.get('/monitor/eye/environment', { params });
  },
  // 获取用眼热力图
  getEyeHeatmap(params) {
    return api.get('/monitor/eye/heatmap', { params });
  },
  // 获取用眼详情数据（仪表盘/统计小卡）
  getEyeDetailData(params) {
    return api.get('/monitor/eye/data', { params });
  },
  
  // 获取用眼历史记录
  getEyeHistory(params) {
    return api.get('/monitor/eye/history', { params });
  },
  
  // 获取情绪数据
  getEmotionData() {
    return api.get('/monitor/emotion');
  },

  // 获取情绪时段分布
  getEmotionDistribution(params) {
    return api.get('/monitor/emotion/distribution', { params });
  },

  // 获取情绪趋势
  getEmotionTrends(params) {
    return api.get('/monitor/emotion/trends', { params });
  },

  // 获取情绪雷达
  getEmotionRadar(params) {
    return api.get('/monitor/emotion/radar', { params });
  },

  // 获取情绪热力图
  getEmotionHeatmap(params) {
    return api.get('/monitor/emotion/heatmap', { params });
  }
};

// 控制相关API
export const controlApi = {
  // 调整灯光亮度
  setLightBrightness(brightness) {
    return api.post('/control/light/brightness', { brightness });
  },
  
  // 调整灯光颜色
  setLightColor(color) {
    return api.post('/control/light/color', { color });
  },
  
  // 控制灯光开关
  setLightPower(power) {
    return api.post('/control/light/power', { power });
  }
};

// 台灯真实状态API
export const lampApi = {
  // 获取真实台灯状态（串口返回）
  getStatus() {
    return api.get('/lamp/status');
  },
  // 触发远眺提醒（调用后端转发到 chatbot 的 vision_reminder）
  sendVisionReminder() {
    return api.post('/lamp/reminder/vision');
  },
  // 触发久坐提醒（调用后端转发到 chatbot 的 posture_reminder）
  sendPostureReminder() {
    return api.post('/lamp/reminder/posture');
  }
};

// 用户相关API
export const userApi = {
  // 获取用户信息
  getUserInfo() {
    return api.get('/user/info');
  },
  
  // 更新用户设置
  updateUserSettings(settings) {
    return api.post('/user/settings', settings);
  },
  
  // 获取通知设置
  getNotificationSettings() {
    return api.get('/user/notifications');
  },
  
  // 更新通知设置
  updateNotificationSettings(settings) {
    return api.post('/user/notifications', settings);
  }
};

// WebSocket管理
export class WebSocketManager {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.listeners = [];
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
  }
  
  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const fullUrl = `${wsProtocol}://${window.location.host}${this.url}`;
    
    this.socket = new WebSocket(fullUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket连接成功');
      this.isConnected = true;
      this.reconnectAttempts = 0;
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.notifyListeners(data);
      } catch (error) {
        console.error('解析WebSocket消息错误:', error);
      }
    };
    
    this.socket.onclose = () => {
      this.isConnected = false;
      this.attemptReconnect();
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('WebSocket重连失败，已达到最大尝试次数');
    }
  }
  
  addListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.removeListener(callback);
    };
  }
  
  removeListener(callback) {
    const index = this.listeners.indexOf(callback);
    if (index !== -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  notifyListeners(data) {
    this.listeners.forEach((callback) => {
      try {
        callback(data);
      } catch (error) {
        console.error('WebSocket监听器错误:', error);
      }
    });
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }
  
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }
}

// 创建实时数据WebSocket管理器实例
export const realtimeWS = new WebSocketManager('/ws/realtime');
