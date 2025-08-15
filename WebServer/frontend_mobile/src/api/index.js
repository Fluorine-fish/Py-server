import axios from 'axios';

// 创建axios实例
export const api = axios.create({
  // 开发使用相对路径，让Vite代理处理
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 这里可以添加认证信息等
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
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
