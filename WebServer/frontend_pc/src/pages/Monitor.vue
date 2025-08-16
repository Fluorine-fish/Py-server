<template>
  <div class="monitor-container">
    <van-nav-bar title="家长监护" fixed />
    
    <div class="dashboard-title">孩子状态实时监护面板</div>
    
    <div class="alert alert-info">
      <div class="alert-icon">ℹ️</div>
      <div class="alert-content">
        <h3>实时监控</h3>
        <p>您可以在这里实时查看孩子的学习状态，并发送消息进行互动</p>
      </div>
    </div>
    
    <div class="dashboard">
      <!-- 第一行布局：左侧2/3为实时画面，右侧1/3为孩子状态 -->
      <div class="dashboard-row">
        <!-- 实时画面卡片 (左侧2/3) -->
        <div class="card video-card">
          <div class="card-header">
            <div class="card-title">实时监控</div>
            <div class="card-icon">📹</div>
          </div>
          <div class="video-container" id="video-container">
            <div class="video-status">
              <div class="loading-indicator" v-if="isVideoLoading">
                <div class="loading-spinner"></div>
                <div class="loading-text">加载中...</div>
              </div>
              <img :src="videoSource" alt="实时监控" @error="handleVideoError" @load="hideVideoLoading" />
            </div>
            <div class="video-controls">
              <div class="resolution-control">
                <label for="resolution">分辨率:</label>
                <select id="resolution" v-model="videoResolution" @change="changeVideoResolution">
                  <option value="low">低 (360p)</option>
                  <option value="medium">中 (480p)</option>
                  <option value="high">高 (720p)</option>
                </select>
              </div>
              <van-button type="primary" size="small" @click="refreshVideoStream">刷新视频</van-button>
            </div>
            <div class="network-status">
              <span class="status-label">网络状态:</span>
              <span class="status-value" :class="networkStatus.class">{{ networkStatus.text }}</span>
                <span class="divider">|</span>
                <span class="status-label">实时数据:</span>
                <span class="status-value" :class="wsConnected ? 'good' : 'error'">{{ wsConnected ? '已连接' : '未连接，重试中…' }}</span>
            </div>

              <!-- 实时消息（来自 WebSocket） -->
              <div class="realtime-messages">
                <div class="rtm-header">
                  <div class="rtm-title">实时消息</div>
                  <div class="rtm-count" v-if="messages.length">{{ messages.length }} 条</div>
                </div>
                <div class="rtm-empty" v-if="messages.length === 0">暂无实时消息</div>
                <div class="rtm-list" v-else>
                  <div class="rtm-item" v-for="m in messages" :key="m.id">
                    <div class="rtm-time">{{ m.time }}</div>
                    <div class="rtm-text">{{ m.text }}</div>
                  </div>
                </div>
              </div>
          </div>
        </div>
        
        <!-- 孩子状态卡片 (右侧1/3) -->
        <div class="card status-card">
          <div class="card-header">
            <div class="card-title">孩子状态</div>
            <div class="card-icon">📊</div>
          </div>
          
          <van-tabs v-model="activeTab" animated swipeable>
            <van-tab title="实时状态">
              <div class="status-container">
                <div class="status-item">
                  <div class="status-label">当前活动</div>
                  <div class="status-value">学习中</div>
                </div>
                <div class="status-item">
                  <div class="status-label">情绪状态</div>
                  <div class="status-value">{{ emotionLabel }}</div>
                </div>
                <div class="status-item">
                  <div class="status-label">坐姿状态</div>
                  <div class="status-value">{{ postureLabel }}</div>
                </div>
                <div class="status-item">
                  <div class="status-label">持续学习时间</div>
                  <div class="status-value">45分钟</div>
                </div>
                <div class="status-item">
                  <div class="status-label">最近休息时间</div>
                  <div class="status-value">15:30</div>
                </div>
                <div class="status-item">
                  <div class="status-label">光照条件</div>
                  <div class="status-value">良好</div>
                </div>
              </div>
            </van-tab>
            <van-tab title="统计数据">
              <div class="status-container">
                <div class="status-item">
                  <div class="status-label">今日学习时长</div>
                  <div class="status-value">3小时45分</div>
                </div>
                <div class="status-item">
                  <div class="status-label">休息次数</div>
                  <div class="status-value">4次</div>
                </div>
                <div class="status-item">
                  <div class="status-label">姿势提醒</div>
                  <div class="status-value">2次</div>
                </div>
                <div class="status-item">
                  <div class="status-label">注意力评分</div>
                  <div class="status-value">87分</div>
                </div>
              </div>
            </van-tab>
          </van-tabs>
        </div>
      </div>
      
      <!-- 第二行布局：左侧1/3为发送消息，右侧2/3为消息历史 -->
      <div class="dashboard-row">
        <!-- 消息发送卡片 (左侧1/3) -->
        <div class="card message-card">
          <div class="card-header">
            <div class="card-title">发送消息</div>
            <div class="card-icon">💬</div>
          </div>
          <div class="message-form">
            <div class="message-input">
              <label for="message-content">消息内容:</label>
              <textarea id="message-content" v-model="messageContent" rows="4" placeholder="输入想要发送给孩子的消息..."></textarea>
            </div>
            
            <!-- 快捷消息模板 -->
            <div class="quick-messages">
              <div class="section-title">快捷消息:</div>
              <div class="quick-message-list">
                <div class="quick-message-item" v-for="(template, index) in messageTemplates" :key="index" @click="useMessageTemplate(template)">
                  {{ template }}
                </div>
              </div>
            </div>
            
            <div class="message-options">
              <div class="schedule-option">
                <label class="schedule-checkbox">
                  <input type="checkbox" v-model="isScheduled" @change="toggleScheduleOptions">
                  <span class="checkbox-label">定时发送</span>
                </label>
              </div>
              
              <div class="schedule-details" v-if="isScheduled">
                <div class="schedule-date">
                  <label for="schedule-date">日期:</label>
                  <input type="date" id="schedule-date" v-model="scheduleDate">
                </div>
                <div class="schedule-time">
                  <label for="schedule-time">时间:</label>
                  <input type="time" id="schedule-time" v-model="scheduleTime">
                </div>
              </div>
            </div>
            
            <div class="message-actions">
              <van-button type="primary" size="large" @click="sendMessage">发送消息</van-button>
            </div>
          </div>
        </div>
        
        <!-- 消息历史卡片 (右侧2/3) -->
        <div class="card history-card">
          <div class="card-header">
            <div class="card-title">消息历史</div>
            <div class="card-icon">📝</div>
          </div>
          <div class="message-history">
            <div v-if="messageHistory.length === 0" class="no-messages">
              暂无消息记录
            </div>
            <div v-else class="message-list">
              <div 
                v-for="(message, index) in messageHistory" 
                :key="index" 
                class="message-item"
                :class="{ 'scheduled': message.scheduled && !message.sent, 'sent': message.sent }"
              >
                <div class="sender">
                  <span v-if="message.scheduled && !message.sent">⏰ 定时消息</span>
                  <span v-else>✉️ 已发送</span>
                </div>
                <div class="content">{{ message.content }}</div>
                <div class="time">{{ message.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MonitorPage',
  data() {
    return {
      activeTab: 0,
      videoSource: '',  // 将在mounted中设置
      isVideoLoading: true,
      videoResolution: 'medium',
      networkStatus: {
        text: '良好',
        class: 'good'
      },
      ws: null,
      wsConnected: false,
      latestRealtime: {
        posture_score: null,
        eye_distance: null,
        emotion: null,
        timestamp: null
      },
      messages: [],
      messageContent: '',
      isScheduled: false,
      scheduleDate: this.getTodayDate(),
      scheduleTime: this.getCurrentTime(),
      messageTemplates: [
        '记得休息一下眼睛',
        '坐姿要正确，不要弯腰驼背',
        '做完作业了吗？',
        '需要帮助吗？',
        '该吃饭了，下来吧'
      ],
  messageHistory: [
        {
          content: '别忘了做数学作业',
          time: '今天 14:30',
          scheduled: false,
          sent: true
        },
        {
          content: '休息一下眼睛，看看远处',
          time: '今天 16:00',
          scheduled: true,
          sent: true
        },
        {
          content: '晚餐准备好了，可以下来吃饭了',
          time: '今天 18:30',
          scheduled: true,
          sent: false
        }
      ]
    }
  },
  mounted() {
    this.setupVideoMonitoring();
    this.initRealtime();
  },
  beforeUnmount() {
    if (this.ws) {
      try { this.ws.close(); } catch (e) {}
      this.ws = null;
    }
  },
  computed: {
    emotionLabel() {
      const e = (this.latestRealtime.emotion || '').toLowerCase();
      const map = {
        happy: '愉悦',
        neutral: '平静',
        sad: '低落',
        angry: '生气',
        focused: '专注'
      };
      return map[e] || (e ? e : '未知');
    },
    postureLabel() {
      const s = this.latestRealtime.posture_score;
      if (s == null) return '未知';
  // 阈值规则：>70 优秀，>62 及格，>=55 一般，否则 需纠正
  if (s > 70) return '优秀';
  if (s > 62) return '及格';
  if (s >= 55) return '一般';
  return '需纠正';
    }
  },
  methods: {
    initRealtime() {
      const url = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/realtime`;
      const ws = new WebSocket(url);
      this.ws = ws;
      ws.onopen = () => { this.wsConnected = true; };
      ws.onclose = () => {
        this.wsConnected = false;
        // 指数退避简单实现：2s 后重连
        setTimeout(() => this.initRealtime(), 2000);
      };
      ws.onerror = () => { this.wsConnected = false; };
      ws.onmessage = (evt) => {
        try {
          const d = JSON.parse(evt.data);
          // 更新最新态
          this.latestRealtime = {
            posture_score: d.posture_score ?? this.latestRealtime.posture_score,
            eye_distance: d.eye_distance ?? this.latestRealtime.eye_distance,
            emotion: d.emotion ?? this.latestRealtime.emotion,
            timestamp: d.timestamp ?? Date.now()/1000
          };
          // 记录消息
          const time = new Date((d.timestamp || Date.now()/1000) * 1000).toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
          const text = JSON.stringify({ posture: d.posture_score, eye: d.eye_distance, emotion: d.emotion });
          this.messages.unshift({ id: `${Date.now()}-${Math.random()}`, time, text });
          if (this.messages.length > 50) this.messages.pop();
        } catch (e) { /* ignore parse error */ }
      };
    },
    setupVideoMonitoring() {
      // 使用实际的视频流API
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      this.videoSource = `${baseUrl}/api/video?t=${Date.now()}`;
      this.isVideoLoading = false;
    },
    refreshVideoStream() {
      this.isVideoLoading = true;
      
      // 先获取摄像头状态
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      fetch(`${baseUrl}/api/video/status`)
        .then(response => response.json())
        .then(data => {
          if (data.available) {
            // 摄像头可用（物理或模拟），显示视频流
            this.videoSource = `${baseUrl}/api/video?t=${Date.now()}`;
            
            // 更新网络状态
            if (data.mode === "模拟摄像头") {
              this.networkStatus = {
                text: '模拟摄像头模式',
                class: 'warning'
              };
            } else {
              this.networkStatus = {
                text: '连接正常',
                class: 'good'
              };
            }
          } else {
            // 摄像头不可用，显示错误
            this.handleVideoError();
          }
        })
        .catch(() => {
          this.handleVideoError();
        })
        .finally(() => {
          setTimeout(() => {
            this.isVideoLoading = false;
          }, 500);
        });
    },
    changeVideoResolution() {
      this.isVideoLoading = true;
      
      // 切换分辨率
      let resolution;
      switch(this.videoResolution) {
        case 'low':
          resolution = '360';
          break;
        case 'high':
          resolution = '720';
          break;
        default:
          resolution = '480';
      }
      
      // 添加分辨率参数到视频URL
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      this.videoSource = `${baseUrl}/api/video?resolution=${resolution}&t=${Date.now()}`;
      
      setTimeout(() => {
        this.isVideoLoading = false;
        this.updateNetworkStatus();
      }, 500);
    },
    updateNetworkStatus() {
      switch(this.videoResolution) {
        case 'low':
          this.networkStatus = {
            text: '良好',
            class: 'good'
          };
          break;
        case 'medium':
          this.networkStatus = {
            text: '一般',
            class: 'medium'
          };
          break;
        case 'high':
          this.networkStatus = {
            text: '较慢',
            class: 'poor'
          };
          break;
      }
    },
    handleVideoError() {
  // 第一步：回退到后端提供的快照
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  this.videoSource = `${baseUrl}/api/video/fallback?t=${Date.now()}`;
      
      this.isVideoLoading = false;
      this.networkStatus = {
        text: '连接失败',
        class: 'error'
      };
      
      console.log("视频流连接失败，3秒后自动重试...");
      
      // 3秒后自动重试
      setTimeout(() => this.refreshVideoStream(), 3000);
    },
    hideVideoLoading() {
      this.isVideoLoading = false;
    },
    showVideoLoading() {
      this.isVideoLoading = true;
    },
    toggleScheduleOptions() {
      if (!this.isScheduled) {
        this.scheduleDate = this.getTodayDate();
        this.scheduleTime = this.getCurrentTime();
      }
    },
    sendMessage() {
      if (!this.messageContent.trim()) {
        alert('请输入消息内容');
        return;
      }
      
      const now = new Date();
      const messageData = {
        content: this.messageContent,
        time: this.formatTime(now),
        scheduled: this.isScheduled,
        sent: !this.isScheduled
      };
      
      if (this.isScheduled) {
        const scheduledTime = new Date(`${this.scheduleDate}T${this.scheduleTime}`);
        if (scheduledTime <= now) {
          alert('定时发送时间必须是未来时间');
          return;
        }
        messageData.time = this.formatDate(scheduledTime) + ' ' + this.scheduleTime;
      }
      
      // 添加消息到历史记录
      this.messageHistory.unshift(messageData);
      
      // 清空消息内容
      this.messageContent = '';
      this.isScheduled = false;
      
      // 模拟消息发送成功
      alert(this.isScheduled ? '消息已成功设置定时发送' : '消息已成功发送');
    },
    getTodayDate() {
      const today = new Date();
      return today.toISOString().slice(0, 10);
    },
    getCurrentTime() {
      const now = new Date();
      return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    },
    formatTime(date) {
      return '今天 ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
    },
    formatDate(date) {
      return date.toLocaleDateString('zh-CN', {month: '2-digit', day: '2-digit'});
    },
    useMessageTemplate(template) {
      this.messageContent = template;
    }
  }
}
</script>

<style scoped>
.monitor-container {
  padding-top: 46px; /* 为固定的NavBar留出空间 */
  padding: 46px 20px 20px;
  --primary-color: #4285f4;
  --secondary-color: #34a853;
  --warning-color: #fbbc05;
  --danger-color: #ea4335;
  --dark-gray: #333333;
  --medium-gray: #666666;
  --light-gray: #f5f5f5;
}

.dashboard-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 20px 0;
  color: var(--dark-gray);
  text-align: center;
}

.alert {
  display: flex;
  padding: 15px;
  background-color: rgba(66, 133, 244, 0.1);
  border-radius: 8px;
  margin-bottom: 20px;
  gap: 15px;
  align-items: flex-start;
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-content h3 {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
}

.alert-content p {
  margin: 0;
  color: var(--medium-gray);
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-row {
  display: flex;
  gap: 20px;
  width: 100%;
}

/* 第一行布局：左侧2/3为实时画面，右侧1/3为孩子状态 */
.video-card {
  flex: 2; /* 占2/3 */
}

.status-card {
  flex: 1; /* 占1/3 */
}

/* 第二行布局：左侧1/3为发送消息，右侧2/3为消息历史 */
.message-card {
  flex: 1; /* 占1/3 */
}

.history-card {
  flex: 2; /* 占2/3 */
}

.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: #333;
}

.card-icon {
  font-size: 1.3rem;
}

.video-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.video-status {
  position: relative;
  width: 100%;
  height: 400px; /* 增加视频高度 */
  background: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: inset 0 0 5px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.video-status img {
  width: 100%;
  display: block;
  transition: opacity 0.3s ease;
}

.loading-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(66, 133, 244, 0.2);
  border-top-color: #4285f4;
  border-radius: 50%;
  animation: spinner 1s linear infinite;
}

@keyframes spinner {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 10px;
  color: #333;
  font-size: 14px;
}

.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resolution-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.resolution-control label {
  font-weight: 500;
}

.resolution-control select {
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.network-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-label {
  color: #666;
}

.status-value {
  font-weight: 600;
}

.divider { color:#ccc; }

.realtime-messages { 
  margin-top: 10px; 
  background: #fafafa; 
  border-radius: 8px; 
  border: 1px solid #eee; 
  padding: 10px; 
}
.rtm-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.rtm-title { font-weight:600; color:#333; }
.rtm-count { font-size:12px; color:#999; }
.rtm-empty { color:#999; font-style: italic; }
.rtm-list { max-height: 160px; overflow:auto; display:flex; flex-direction:column; gap:6px; }
.rtm-item { display:flex; gap:10px; font-size:12px; }
.rtm-time { color:#666; width:72px; flex: 0 0 auto; }
.rtm-text { color:#333; word-break: break-all; }

.status-value.good {
  color: #34a853;
}

.status-value.medium {
  color: #fbbc05;
}

.status-value.poor {
  color: #ea4335;
}

.status-value.error {
  color: #ea4335;
}

.message-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px 0;
}

.message-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-input label {
  font-weight: 500;
}

.message-input textarea {
  resize: vertical;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
}

.message-input textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.1);
}

/* 快捷消息样式 */
.quick-messages {
  margin: 10px 0;
}

.section-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--medium-gray);
}

.quick-message-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-message-item {
  background-color: var(--light-gray);
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 5px 12px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-message-item:hover {
  background-color: rgba(66, 133, 244, 0.1);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.message-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.schedule-option {
  display: flex;
  align-items: center;
}

.schedule-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.schedule-checkbox input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label {
  font-weight: 500;
}

.schedule-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.schedule-date, .schedule-time {
  display: flex;
  align-items: center;
  gap: 10px;
}

.schedule-date label, .schedule-time label {
  font-weight: 500;
  width: 40px;
}

.schedule-date input, .schedule-time input {
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.message-actions {
  margin-top: 10px;
}

.message-history {
  height: 400px;
  overflow-y: auto;
  padding: 10px;
  scrollbar-width: thin;
  scrollbar-color: #ccc #f5f5f5;
}

.no-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-style: italic;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 3px solid var(--primary-color);
}

.message-item.scheduled {
  border-left-color: var(--warning-color);
  background: rgba(251, 188, 5, 0.1);
}

.message-item.sent {
  border-left-color: var(--secondary-color);
  background: rgba(52, 168, 83, 0.05);
}

.message-item .sender {
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.message-item.scheduled .sender {
  color: var(--warning-color);
}

.message-item.sent .sender {
  color: var(--secondary-color);
}

.message-item .content {
  margin-bottom: 5px;
}

.message-item .time {
  font-size: 0.8rem;
  color: #666;
}

.status-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  padding: 15px 10px;
}

/* 标签页样式 */
:deep(.van-tabs) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.van-tabs__wrap) {
  flex-shrink: 0;
  background-color: var(--light-gray);
  border-radius: 8px 8px 0 0;
}

:deep(.van-tabs__content) {
  flex: 1;
  overflow: auto;
}

:deep(.van-tab) {
  font-size: 0.9rem;
  color: var(--medium-gray);
}

:deep(.van-tab--active) {
  color: var(--primary-color);
  font-weight: 600;
}

:deep(.van-tabs__line) {
  background-color: var(--primary-color);
}

.status-item {
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
}

.status-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.status-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--dark-gray);
}

@media (max-width: 1024px) {
  .status-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-row {
    flex-direction: column;
  }
  
  .video-card,
  .status-card,
  .message-card,
  .history-card {
    flex: 1;
    width: 100%;
    margin-bottom: 20px;
  }
  
  .video-status {
    height: 300px;
  }
  
  .message-history {
    height: 300px;
  }
}

@media (max-width: 480px) {
  .monitor-container {
    padding: 46px 10px 10px;
  }
  
  .video-status {
    height: 240px;
  }
  
  .dashboard-title {
    font-size: 1.3rem;
  }
  
  .card-header {
    padding: 10px 15px;
  }
  
  .message-history {
    height: 250px;
  }
}
</style>
