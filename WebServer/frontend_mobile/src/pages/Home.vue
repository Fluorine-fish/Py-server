<template>
  <div class="mobile-page">
    <div class="mobile-dashboard">
      <!-- 主要内容区域：统一背景卡片 -->
      <div class="main-content-card">
        <div class="mobile-card">
          <div class="mobile-card-header green-gradient">
            <div class="mobile-card-title main-title-large">瞳灵智能台灯-家长呵护端</div>
            <div class="refresh-button" @click="refreshData">
              <i class="bi bi-arrow-clockwise"></i>
            </div>
          </div>
          <div class="mobile-card-content">
            <div class="unified-layout">
              <!-- 左侧：视频 + 评分 -->
              <div class="video-stats-section">
                <!-- 视频区域 -->
                <div class="video-container-unified">
                  <img :src="videoUrl" class="video-stream" alt="实时监控" />
                  <div class="video-overlay">
                    <div class="video-status">
                      <i class="bi bi-circle-fill text-danger"></i> 实时
                    </div>
                  </div>
                </div>
                
                <!-- 评分区域（在视频下方），只保留坐姿得分和情绪状态 -->
                <div class="stats-horizontal-unified">
                  <div class="stat-item-unified">
                    <div class="stat-label">坐姿得分</div>
                    <div class="stat-value">{{ monitorStore.postureData.currentScore || '-' }}</div>
                  </div>
                  <div class="stat-item-unified">
                    <div class="stat-label">情绪状态</div>
                    <div class="stat-value">{{ monitorStore.emotionLabel }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 右侧：工具按钮区域 -->
              <div class="tools-section-unified">
                <div class="tools-header">
                  <h4 class="tools-title">快捷功能</h4>
                </div>
                <div class="tools-list">
                  <router-link to="/posture" class="tool-button-unified tool-posture">
                    <div class="tool-icon-unified">
                      <i class="bi bi-activity"></i>
                    </div>
                    <div class="tool-text-unified">坐姿检测</div>
                  </router-link>
                  <router-link to="/eye" class="tool-button-unified tool-eye">
                    <div class="tool-icon-unified">
                      <i class="bi bi-eye"></i>
                    </div>
                    <div class="tool-text-unified">用眼监护</div>
                  </router-link>
                  <router-link to="/emotion" class="tool-button-unified tool-emotion">
                    <div class="tool-icon-unified">
                      <i class="bi bi-emoji-smile"></i>
                    </div>
                    <div class="tool-text-unified">情绪监测</div>
                  </router-link>
                  <router-link to="/guardian" class="tool-button-unified tool-analysis">
                    <div class="tool-icon-unified">
                      <i class="bi bi-graph-up"></i>
                    </div>
                    <div class="tool-text-unified">数据分析</div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 最近活动卡片 -->
      <div class="mobile-card">
        <div class="mobile-card-header green-gradient">
          <div class="mobile-card-title">最近活动</div>
        </div>
        <div class="mobile-card-content">
          <div v-if="activities.length === 0" class="empty-state">
            <i class="bi bi-calendar-x"></i>
            <p>暂无活动记录</p>
          </div>
          <div v-else class="activity-list">
            <div v-for="(activity, index) in activities" :key="index" class="activity-item">
              <div class="activity-icon">
                <i :class="activity.icon"></i>
              </div>
              <div class="activity-info">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useDeviceStore, useMonitorStore } from '../stores';

const deviceStore = useDeviceStore();
const monitorStore = useMonitorStore();

// 视频流URL
const videoUrl = ref('/api/video');

// 模拟最近活动数据
const activities = ref([
  {
    icon: 'bi bi-exclamation-triangle-fill text-warning',
    title: '检测到不良坐姿',
    time: '10分钟前'
  },
  {
    icon: 'bi bi-clock-fill text-primary',
    title: '提醒休息',
    time: '30分钟前'
  },
  {
    icon: 'bi bi-lightbulb-fill text-success',
    title: '自动调整灯光亮度',
    time: '1小时前'
  }
]);

// 刷新数据
const refreshData = async () => {
  await Promise.all([
    deviceStore.fetchDeviceStatus(),
    monitorStore.fetchPostureData(),
    monitorStore.fetchEyeData(),
    monitorStore.fetchEmotionData()
  ]);
};

// 组件挂载时加载数据
onMounted(async () => {
  await refreshData();
});
</script>

<style scoped>


.refresh-button {
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--gradient-light);
  color: #1B4332;
  box-shadow: 0 2px 6px rgba(27, 67, 50, 0.15);
  border: 1px solid rgba(230, 242, 237, 0.8);
}

.empty-state {
  text-align: center;
  padding: 20px 0;
  color: var(--color-text-tertiary);
}

.empty-state i {
  font-size: 32px;
  margin-bottom: 12px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 8px;
  background-color: var(--color-card-hover);
  border-radius: 8px;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--gradient-light); /* 使用浅色渐变背景 */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
  color: #1B4332; /* 深绿色图标 */
  box-shadow: 0 2px 6px rgba(27, 67, 50, 0.12); /* 轻微阴影 */
  border: 1px solid rgba(230, 242, 237, 0.8); /* 添加浅色边框 */
}

.activity-info {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.monitor-layout {
  display: flex;
  gap: 16px; /* 保持原来的间距 */
  height: 250px; /* 设置固定高度以确保适配 */
  margin: 2px; /* 保持原来的边距 */
  position: relative; /* 添加相对定位便于视觉效果 */
}

.video-section {
  flex: 2;
  min-width: 0;
  position: relative;
  height: 100%;
  border-radius: 16px; /* 增大圆角 */
  overflow: hidden; /* 确保内容不溢出圆角边框 */
  box-shadow: 0 6px 16px rgba(90, 152, 128, 0.18); /* 绿色调阴影 */
  border: 1px solid rgba(255, 255, 255, 0.8); /* 添加白色边框 */
}

.stats-section {
  flex: 1;
  min-width: 0;
  display: flex;
  justify-content: center;
  height: 100%;
  padding-left: 6px; /* 小幅增加左内边距 */
  border-radius: 16px; /* 匹配左侧圆角 */
  background-color: rgba(255, 255, 255, 0.75); /* 半透明背景 */
  backdrop-filter: blur(5px); /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.8); /* 添加白色边框 */
}

.stats-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  height: 100%;
  justify-content: space-between; /* 均匀分布各个状态项 */
}

.stat-item-vertical {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px; /* 保持原来的内边距 */
  border-radius: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1; /* 让每个状态项平均分配高度 */
  box-shadow: 0 4px 10px rgba(126, 191, 167, 0.12); /* 绿色调阴影 */
  transition: all 0.25s; /* 过渡效果 */
  border: 1px solid rgba(255, 255, 255, 0.9); /* 更明显的边框 */
  backdrop-filter: blur(3px); /* 轻微模糊效果 */
  -webkit-backdrop-filter: blur(3px);
}

.stat-item-vertical:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(126, 191, 167, 0.18);
  background-color: rgba(255, 255, 255, 0.95);
}

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: #5A9880; /* 使用主题绿色 */
  margin-bottom: 8px;
  letter-spacing: 0.5px; /* 字间距 */
  text-transform: uppercase; /* 小型大写字母 */
  font-size: 11px;
}

.stat-value {
  font-weight: 600;
  font-size: 20px;
  color: #404F48; /* 深色文本 */
  margin-top: 2px;
  letter-spacing: 0.5px;
  font-size: 16px;
  font-weight: 600;
}

.video-container {
  position: relative;
  width: 100%;
  height: 100%; /* 使用 100% 高度填充父容器 */
  border-radius: var(--radius);
  overflow: hidden;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block; /* 防止底部间隙 */
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.video-status {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10; /* 确保在视频上方显示 */
  display: flex;
  align-items: center;
  gap: 4px;
}

.video-status {
  top: 10px;
  right: 10px;
}

.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-danger); }
.text-primary { color: var(--color-primary); }
.text-secondary { color: var(--color-text-secondary); }

/* 工具区域标题样式 */
.tools-header {
  margin-bottom: 12px;
}

.tools-title {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin: 0;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.tools-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 工具图标样式 - 圆角矩形避免变形 */
.tool-icon-unified {
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;
  max-width: 28px !important;
  max-height: 28px !important;
  
  /* 圆角矩形 - 不会变形 */
  border-radius: 8px !important;
  
  /* 布局 */
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  
  /* 防止变形 */
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  
  /* 盒模型 */
  box-sizing: border-box !important;
  padding: 0 !important;
  margin: 0 !important; /* 去掉下边距 */
  
  /* 背景和颜色 */
  background: #f8f9fa; /* 浅灰色背景，与底部标签栏一致 */
  color: #6c757d; /* 深灰色图标 */
  font-size: 16px; /* 增大图标字体 */
  
  /* 阴影效果让它更立体 */
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.2) !important;
}

/* 不同功能按钮的背景色区分 */
.tool-posture {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.05) 0%, rgba(52, 152, 219, 0.1) 100%);
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.tool-eye {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.05) 0%, rgba(46, 204, 113, 0.1) 100%);
  border: 1px solid rgba(46, 204, 113, 0.2);
}

.tool-emotion {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05) 0%, rgba(255, 193, 7, 0.1) 100%);
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.tool-analysis {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.05) 0%, rgba(156, 39, 176, 0.1) 100%);
  border: 1px solid rgba(156, 39, 176, 0.2);
}

/* 对应的图标颜色 */
.tool-posture .tool-icon-unified {
  background: rgba(52, 152, 219, 0.1) !important;
  color: #3498db !important;
}

.tool-eye .tool-icon-unified {
  background: rgba(46, 204, 113, 0.1) !important;
  color: #2ecc71 !important;
}

.tool-emotion .tool-icon-unified {
  background: rgba(255, 193, 7, 0.1) !important;
  color: #ffc107 !important;
}

.tool-analysis .tool-icon-unified {
  background: rgba(156, 39, 176, 0.1) !important;
  color: #9c27b0 !important;
}

.tool-button-unified {
  display: flex !important;
  flex-direction: row !important; /* 改为水平排列 */
  align-items: center !important;
  justify-content: flex-start !important; /* 左对齐 */
  padding: 12px 16px; /* 调整内边距 */
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%);
  border-radius: var(--radius-small);
  border: 1px solid rgba(116, 198, 157, 0.2);
  cursor: pointer;
  transition: var(--transition);
  backdrop-filter: blur(8px);
  min-height: 70px !important;
  min-width: 60px !important;
  width: 100% !important;
  text-decoration: none;
  color: inherit;
  box-sizing: border-box !important;
  flex-shrink: 0 !important;
  gap: 12px; /* 图标和文字之间的间距 */
}

.tool-button-unified:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 250, 252, 0.9) 100%);
}

.tool-text-unified {
  font-size: 14px; /* 适中的字体大小 */
  color: var(--color-text);
  font-weight: 600; /* 稍微减轻一点粗细 */
  text-align: left; /* 左对齐 */
  line-height: 1.2;
  flex: 1; /* 占据剩余空间 */
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 强制两行显示 */
  line-clamp: 2; /* 标准属性 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all; /* 强制换行 */
}

/* 响应式优化 */
@media (max-width: 480px) {
  .tools-section-unified {
    flex-direction: column !important; /* 在小屏幕上改为垂直排列 */
    width: 100% !important;
    max-width: 100% !important;
    gap: 12px;
  }
  
  .tools-header {
    margin-bottom: 8px;
  }
  
  .tools-title {
    font-size: 13px;
    padding-bottom: 6px;
  }
  
  .tools-list {
    gap: 6px;
  }
  
  .tool-button-unified {
    min-height: 60px !important;
    padding: 12px 16px;
    min-width: 100% !important;
    flex: none !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    flex-direction: row !important; /* 保持水平排列 */
    justify-content: flex-start !important;
    gap: 12px;
  }

  .tool-icon-unified {
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    max-width: 24px !important;
    max-height: 24px !important;
    
    border-radius: 6px !important;
    
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    
    flex-shrink: 0 !important;
    flex-grow: 0 !important;
    
    box-sizing: border-box !important;
    padding: 0 !important;
    margin: 0 !important; /* 去掉边距 */
    
    font-size: 14px; /* 响应式下的图标字体 */
    
    box-shadow: 0 1px 3px rgba(108, 117, 125, 0.2) !important;
  }
  
  .tool-text-unified {
    font-size: 12px; /* 响应式下的文字字体 */
    font-weight: 600; /* 保持适中粗细 */
    text-align: left;
    display: -webkit-box;
    -webkit-line-clamp: 2; /* 强制两行显示 */
    line-clamp: 2; /* 标准属性 */
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: break-all; /* 强制换行 */
    flex: 1;
  }
}
</style>
