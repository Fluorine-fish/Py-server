import { defineStore } from 'pinia';
import { deviceApi, monitorApi } from '../api';

export const useDeviceStore = defineStore('device', {
  state: () => ({
    deviceInfo: null,
    deviceStatus: {
      online: false,
      lastSeen: null,
      batteryLevel: null,
      charging: false
    },
    deviceSettings: {
      brightness: 50,
      colorTemperature: 4000,
      autoAdjust: true
    },
    loading: false,
    error: null
  }),
  
  getters: {
    isOnline: (state) => state.deviceStatus.online,
    batteryPercentage: (state) => state.deviceStatus.batteryLevel
  },
  
  actions: {
    async fetchDeviceInfo() {
      this.loading = true;
      this.error = null;
      
      try {
        this.deviceInfo = await deviceApi.getDeviceInfo();
      } catch (error) {
        this.error = '获取设备信息失败';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchDeviceStatus() {
      this.loading = true;
      this.error = null;
      
      try {
        this.deviceStatus = await deviceApi.getDeviceStatus();
      } catch (error) {
        // 模拟数据，实际应用中移除
        this.deviceStatus = {
          online: true,
          lastSeen: new Date().toISOString(),
          batteryLevel: 85,
          charging: true
        };
        
        this.error = '获取设备状态失败，使用模拟数据';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchDeviceSettings() {
      this.loading = true;
      this.error = null;
      
      try {
        this.deviceSettings = await deviceApi.getDeviceSettings();
      } catch (error) {
        // 模拟数据，实际应用中移除
        this.deviceSettings = {
          brightness: 70,
          colorTemperature: 5500,
          autoAdjust: true
        };
        
        this.error = '获取设备设置失败，使用模拟数据';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    async updateDeviceSettings(settings) {
      this.loading = true;
      this.error = null;
      
      try {
        await deviceApi.updateDeviceSettings(settings);
        this.deviceSettings = { ...this.deviceSettings, ...settings };
      } catch (error) {
        this.error = '更新设备设置失败';
        console.error(error);
      } finally {
        this.loading = false;
      }
    }
  }
});

export const useMonitorStore = defineStore('monitor', {
  state: () => ({
    postureData: {
      currentScore: null,
      warnCount: 0,
      averageScore: null,
      lastDetected: null,
      timeDistribution: null,
      improvement: null
    },
    postureHistory: {
      day: null,
      week: null,
      month: null
    },
    postureImages: [],
    eyeData: {
      eyeDistance: null,
      screenTime: 0,
      breakReminder: null,
      lastWarning: null
    },
    emotionData: {
      currentEmotion: null,
      confidence: null,
      history: []
    },
    loading: false,
    error: null
  }),
  
  getters: {
    formattedScreenTime: (state) => {
      const minutes = Math.floor(state.eyeData.screenTime / 60);
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      
      if (hours > 0) {
        return `${hours}小时${remainingMinutes}分钟`;
      } else {
        return `${minutes}分钟`;
      }
    },
    
    postureStatus: (state) => {
      const score = state.postureData.currentScore;
      if (score === null) return '未检测';
      if (score >= 80) return '良好';
      if (score >= 60) return '一般';
      return '不良';
    },
    
    emotionLabel: (state) => {
      const emotionMap = {
        'happy': '开心',
        'sad': '难过',
        'angry': '生气',
        'surprised': '惊讶',
        'fear': '恐惧',
        'disgust': '厌恶',
        'neutral': '平静'
      };
      
      return state.emotionData.currentEmotion 
        ? (emotionMap[state.emotionData.currentEmotion] || state.emotionData.currentEmotion)
        : '未检测';
    }
  },
  
  actions: {
    async fetchPostureData() {
      this.loading = true;
      this.error = null;
      
      try {
        this.postureData = await monitorApi.getPostureData();
      } catch (error) {
        // 模拟数据，实际应用中移除
        this.postureData = {
          currentScore: 85,
          warnCount: 3,
          averageScore: 78,
          lastDetected: new Date().toISOString()
        };
        
        this.error = '获取坐姿数据失败，使用模拟数据';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchPostureHistoryByTimeRange(timeRange) {
      this.loading = true;
      this.error = null;
      
      try {
        // 如果已有缓存数据则使用缓存数据
        if (this.postureHistory[timeRange]) {
          return this.postureHistory[timeRange];
        }
        
        // 否则从API获取
        const params = { timeRange }; // 'day', 'week', 'month'
        const data = await monitorApi.getPostureHistory(params);
        this.postureHistory[timeRange] = data;
        return data;
      } catch (error) {
        // 模拟数据
        const mockData = {
          day: {
            goodTime: '3.2',
            mildTime: '1.2',
            badTime: '0.6',
            goodRate: '64',
            problemTimeSlot: '下午3-5点',
            improvementMessage: '今天坐姿良好，请继续保持。'
          },
          week: {
            goodTime: '18.5',
            mildTime: '7.3',
            badTime: '4.2',
            goodRate: '62',
            problemTimeSlot: '周四下午',
            improvementMessage: '本周坐姿改善效果明显，请继续保持良好习惯。'
          },
          month: {
            goodTime: '72.4',
            mildTime: '31.6',
            badTime: '16.0',
            goodRate: '60',
            problemTimeSlot: '下午时段',
            improvementMessage: '本月总体坐姿较好，但下午时段仍需注意。'
          }
        };
        
        this.postureHistory[timeRange] = mockData[timeRange];
        this.error = `获取${timeRange === 'day' ? '今日' : timeRange === 'week' ? '本周' : '本月'}坐姿数据失败，使用模拟数据`;
        console.error(error);
        return mockData[timeRange];
      } finally {
        this.loading = false;
      }
    },
    
    async fetchPostureTimeDistribution(timeRange) {
      this.loading = true;
      this.error = null;
      
      try {
        const params = { timeRange }; // 'day', 'week', 'month'
        const data = await monitorApi.getPostureTimeDistribution(params);
        this.postureData.timeDistribution = data;
        return data;
      } catch (error) {
        // 模拟数据
        const mockData = {
          day: [2, 1, 0, 3, 4, 2, 1, 0, 5, 3, 1, 0],
          week: [3, 2, 1, 5, 7, 4, 2, 1, 8, 6, 3, 1],
          month: [4, 3, 2, 6, 8, 5, 3, 2, 9, 7, 4, 2]
        };
        
        this.postureData.timeDistribution = mockData[timeRange];
        this.error = '获取坐姿时间分布数据失败，使用模拟数据';
        console.error(error);
        return mockData[timeRange];
      } finally {
        this.loading = false;
      }
    },
    
    async fetchPostureImages(page = 1, limit = 6) {
      this.loading = true;
      this.error = null;
      
      try {
        const params = { page, limit };
        const data = await monitorApi.getPostureImages(params);
        
        if (page === 1) {
          this.postureImages = data;
        } else {
          this.postureImages = [...this.postureImages, ...data];
        }
        
        return data;
      } catch (error) {
        // 模拟图像数据
        const mockImages = Array.from({ length: limit }, (_, i) => ({
          id: `img_${page}_${i}`,
          url: '/static/mobile/placeholder.jpg', // 使用占位图
          timestamp: new Date(Date.now() - i * 3600000).toISOString(),
          score: Math.floor(Math.random() * 100)
        }));
        
        if (page === 1) {
          this.postureImages = mockImages;
        } else {
          this.postureImages = [...this.postureImages, ...mockImages];
        }
        
        this.error = '获取坐姿图像记录失败，使用模拟数据';
        console.error(error);
        return mockImages;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchPostureImprovement() {
      try {
        const data = await monitorApi.getPostureImprovement();
        this.postureData.improvement = data;
        return data;
      } catch (error) {
        // 模拟数据
        const mockData = {
          problemTimeSlot: '下午3-5点',
          improvementMessage: '本周坐姿改善效果明显，请继续保持良好习惯。'
        };
        
        this.postureData.improvement = mockData;
        console.error(error);
        return mockData;
      }
    },
    
    async fetchEyeData() {
      this.loading = true;
      this.error = null;
      
      try {
        this.eyeData = await monitorApi.getEyeData();
      } catch (error) {
        // 模拟数据，实际应用中移除
        this.eyeData = {
          eyeDistance: 45,
          screenTime: 7200, // 2小时
          breakReminder: '每30分钟',
          lastWarning: new Date(Date.now() - 1000 * 60 * 15).toISOString() // 15分钟前
        };
        
        this.error = '获取用眼数据失败，使用模拟数据';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchEmotionData() {
      this.loading = true;
      this.error = null;
      
      try {
        this.emotionData = await monitorApi.getEmotionData();
      } catch (error) {
        // 模拟数据，实际应用中移除
        this.emotionData = {
          currentEmotion: 'happy',
          confidence: 0.92,
          history: [
            { time: new Date(Date.now() - 1000 * 60 * 30).toISOString(), emotion: 'neutral', duration: 1200 },
            { time: new Date(Date.now() - 1000 * 60 * 15).toISOString(), emotion: 'happy', duration: 900 }
          ]
        };
        
        this.error = '获取情绪数据失败，使用模拟数据';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    updateFromWebSocket(data) {
      if (data.posture_score !== undefined) {
        this.postureData.currentScore = data.posture_score;
        this.postureData.lastDetected = new Date().toISOString();
      }
      
      if (data.eye_distance !== undefined) {
        this.eyeData.eyeDistance = data.eye_distance;
      }
      
      if (data.emotion !== undefined) {
        this.emotionData.currentEmotion = data.emotion;
        this.emotionData.confidence = data.emotion_confidence || 0.8;
      }
    }
  }
});
