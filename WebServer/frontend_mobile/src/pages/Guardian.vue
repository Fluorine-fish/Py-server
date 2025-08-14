<template>
  <div class="mobile-page">
    <div class="page-heading">家长监护</div>
    
    <!-- 实时视频 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">实时监控</div>
      </div>
      <div class="mobile-card-content">
        <div class="video-container">
          <img :src="videoUrl" class="video-stream" alt="实时监控" />
          <div class="video-overlay">
            <div class="video-status">
              <i class="bi bi-circle-fill text-danger"></i> 实时
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 监护数据摘要 -->
    <div class="mobile-card">
      <div class="mobile-card-header green-gradient">
        <div class="mobile-card-title">监护数据</div>
      </div>
      <div class="mobile-card-content">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon" :class="{ 'warning': postureWarning }">
              <i class="bi bi-person-standing"></i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ monitorStore.postureData.currentScore || '-' }}</div>
              <div class="stat-label">坐姿得分</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon" :class="{ 'warning': eyeWarning }">
              <i class="bi bi-eye"></i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ monitorStore.eyeData.eyeDistance || '-' }}cm</div>
              <div class="stat-label">眼睛距离</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon" :class="{ 'warning': screenTimeWarning }">
              <i class="bi bi-clock"></i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ monitorStore.formattedScreenTime }}</div>
              <div class="stat-label">今日用眼</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon">
              <i class="bi bi-emoji-smile"></i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ monitorStore.emotionLabel }}</div>
              <div class="stat-label">情绪状态</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 监护报告 -->
    <div class="mobile-card">
      <div class="mobile-card-header green-gradient">
        <div class="mobile-card-title">监护报告</div>
      </div>
      <div class="mobile-card-content">
        <div ref="reportChart" class="chart-container"></div>
        
        <div class="report-summary">
          <div class="summary-item">
            <div class="summary-icon">
              <i class="bi bi-calendar-check text-primary"></i>
            </div>
            <div class="summary-info">
              <div class="summary-title">监护状态</div>
              <div class="summary-value">已开启 (24小时)</div>
            </div>
          </div>
          
          <div class="summary-item">
            <div class="summary-icon">
              <i class="bi bi-exclamation-triangle text-warning"></i>
            </div>
            <div class="summary-info">
              <div class="summary-title">今日警告</div>
              <div class="summary-value">{{ totalWarnings }}次</div>
            </div>
          </div>
          
          <div class="summary-item">
            <div class="summary-icon">
              <i class="bi bi-trophy text-success"></i>
            </div>
            <div class="summary-info">
              <div class="summary-title">总体评级</div>
              <div class="summary-value">{{ overallRating }}</div>
            </div>
          </div>
        </div>
        
        <van-button block type="primary" class="report-button">
          <i class="bi bi-file-earmark-text"></i>
          <span>查看完整监护报告</span>
        </van-button>
      </div>
    </div>
    
    <!-- 监护设置 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">监护设置</div>
      </div>
      <div class="mobile-card-content">
        <div class="settings-list">
          <div class="settings-item">
            <div class="settings-info">
              <i class="bi bi-bell"></i>
              <span>监护提醒</span>
            </div>
            <van-switch v-model="notificationOn" size="24" />
          </div>
          
          <div class="settings-item">
            <div class="settings-info">
              <i class="bi bi-camera-video"></i>
              <span>视频监控</span>
            </div>
            <van-switch v-model="videoOn" size="24" />
          </div>
          
          <div class="settings-item">
            <div class="settings-info">
              <i class="bi bi-graph-up"></i>
              <span>数据分析</span>
            </div>
            <van-switch v-model="analyticsOn" size="24" />
          </div>
          
          <div class="settings-item">
            <div class="settings-info">
              <i class="bi bi-shield-lock"></i>
              <span>隐私保护</span>
            </div>
            <van-switch v-model="privacyOn" size="24" />
          </div>
        </div>
        
        <router-link to="/settings/monitor" class="settings-more">
          <span>更多监护设置</span>
          <i class="bi bi-chevron-right"></i>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useMonitorStore } from '../stores';
import * as echarts from 'echarts';

const monitorStore = useMonitorStore();
const reportChart = ref(null);
let chartInstance = null;

// 视频流URL
const videoUrl = ref('/api/video');

// 监护设置状态
const notificationOn = ref(true);
const videoOn = ref(true);
const analyticsOn = ref(true);
const privacyOn = ref(true);

// 警告状态
const postureWarning = computed(() => {
  const score = monitorStore.postureData.currentScore;
  return score !== null && score < 60;
});

const eyeWarning = computed(() => {
  const distance = monitorStore.eyeData.eyeDistance;
  return distance !== null && distance < 30;
});

const screenTimeWarning = computed(() => {
  return monitorStore.eyeData.screenTime > 7200; // 超过2小时
});

// 总警告次数
const totalWarnings = computed(() => {
  return monitorStore.postureData.warnCount + 
         (monitorStore.eyeData.lastWarning ? 1 : 0);
});

// 总体评级
const overallRating = computed(() => {
  const postureScore = monitorStore.postureData.currentScore || 0;
  const warnings = totalWarnings.value;
  
  if (postureScore >= 80 && warnings <= 2) return '优秀';
  if (postureScore >= 70 && warnings <= 5) return '良好';
  if (postureScore >= 60) return '一般';
  return '需注意';
});

// 初始化图表
const initChart = () => {
  chartInstance = echarts.init(reportChart.value);
  
  // 用眼时长数据，用于判断颜色
  const usageData = [2.5, 3.2, 2.8, 3.5, 2.6, 1.8, 1.2];
  const maxUsage = Math.max(...usageData);
  
  // 根据使用时长设置不同的绿色
  const barColors = usageData.map(value => {
    if (value >= maxUsage * 0.8) return '#2D6A4F'; // 深绿色 - 最高使用时长
    if (value >= maxUsage * 0.6) return '#40916C'; // 中等绿色
    if (value >= maxUsage * 0.4) return '#52B788'; // 浅绿色
    return '#74C69D'; // 最浅绿色 - 最低使用时长
  });
  
  chartInstance.setOption({
    backgroundColor: 'transparent',
    title: {
      text: '近7天监护数据',
      left: 'center',
      top: 10,
      textStyle: { 
        color: '#404F48',
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    legend: {
      data: ['坐姿得分', '用眼时长'],
      bottom: 20,
      textStyle: { 
        color: '#677C73',
        fontSize: 12
      },
      itemGap: 20,
      icon: 'circle'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { 
        lineStyle: { color: '#D4E8DD' }
      },
      axisLabel: { 
        color: '#677C73',
        fontSize: 11
      },
      axisTick: {
        alignWithLabel: true,
        lineStyle: { color: '#D4E8DD' }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '坐姿得分',
        nameLocation: 'middle',
        nameGap: 50,
        nameTextStyle: {
          color: '#677C73',
          fontSize: 11
        },
        min: 0,
        max: 100,
        axisLine: { 
          show: true,
          lineStyle: { color: '#D4E8DD' }
        },
        axisLabel: { 
          color: '#677C73',
          fontSize: 11,
          formatter: '{value}'
        },
        splitLine: { 
          lineStyle: { 
            color: '#E9F2ED',
            type: 'dashed'
          }
        }
      },
      {
        type: 'value',
        name: '用眼时长(小时)',
        nameLocation: 'middle',
        nameGap: 50,
        nameTextStyle: {
          color: '#677C73',
          fontSize: 11
        },
        min: 0,
        max: 5,
        axisLine: { 
          show: true,
          lineStyle: { color: '#D4E8DD' }
        },
        axisLabel: { 
          color: '#677C73',
          fontSize: 11,
          formatter: '{value}h'
        },
        splitLine: { show: false }
      }
    ],
    grid: {
      left: '15%',  // 增加左侧空间以显示完整的轴标签
      right: '15%',
      top: '20%',
      bottom: '25%',
      containLabel: true
    },
    series: [
      {
        name: '坐姿得分',
        type: 'line',
        data: [85, 75, 88, 78, 80, 92, 86],
        itemStyle: { 
          color: '#3A8469',
          borderWidth: 2
        },
        lineStyle: {
          color: '#3A8469',
          width: 3,
          type: 'solid'
        },
        symbol: 'circle',
        symbolSize: 8,
        smooth: true,
        emphasis: {
          focus: 'series',
          itemStyle: {
            borderWidth: 4,
            shadowBlur: 10,
            shadowColor: 'rgba(58, 132, 105, 0.3)'
          }
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(58, 132, 105, 0.3)' },
              { offset: 1, color: 'rgba(58, 132, 105, 0.05)' }
            ]
          }
        }
      },
      {
        name: '用眼时长',
        type: 'bar',
        yAxisIndex: 1,
        data: usageData,
        itemStyle: { 
          color: function(params) {
            return barColors[params.dataIndex];
          },
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(45, 106, 79, 0.3)'
          }
        },
        barWidth: '60%'
      }
    ],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#3A8469',
      borderWidth: 1,
      textStyle: {
        color: '#404F48'
      },
      formatter: function(params) {
        let result = params[0].name + '<br/>';
        params.forEach(function(item) {
          const unit = item.seriesName === '用眼时长' ? 'h' : '分';
          result += `<span style="color:${item.color}">●</span> ${item.seriesName}: ${item.value}${unit}<br/>`;
        });
        return result;
      }
    }
  });
};

// 处理窗口调整
const handleResize = () => {
  chartInstance?.resize();
};

// 刷新图表
const refreshChart = () => {
  if (chartInstance) {
    setTimeout(() => {
      chartInstance.resize();
    }, 100);
  }
};

// 加载数据并初始化图表
onMounted(async () => {
  await Promise.all([
    monitorStore.fetchPostureData(),
    monitorStore.fetchEyeData(),
    monitorStore.fetchEmotionData()
  ]);
  
  // 等待DOM完全渲染后初始化图表
  setTimeout(() => {
    initChart();
    // 延迟刷新确保图表正确显示
    setTimeout(refreshChart, 300);
  }, 100);
  
  window.addEventListener('resize', handleResize);
});

// 清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});
</script>

<style scoped>
.page-heading {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.video-container {
  position: relative;
  width: 100%;
  border-radius: var(--radius);
  overflow: hidden;
  aspect-ratio: 16/9;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  display: flex;
  align-items: center;
  gap: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  background-color: var(--color-card-hover);
  border-radius: var(--radius);
  padding: 14px;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--gradient-light); /* 使用浅色渐变背景 */
  color: #1B4332; /* 深绿色文字 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 12px;
  box-shadow: 0 2px 6px rgba(27, 67, 50, 0.12); /* 轻微阴影 */
  border: 1px solid rgba(230, 242, 237, 0.8); /* 添加浅色边框 */
}

.stat-icon.warning {
  background: linear-gradient(to right, #FFE5E5, #FFCACA); /* 浅红色渐变 */
  color: #9A2617; /* 深红色文字 */
  border: 1px solid rgba(197, 70, 50, 0.3); /* 红色边框 */
}

.stat-data {
  flex: 1;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.chart-container {
  width: 100%;
  height: 300px;  /* 增加高度以适应左侧轴标签 */
  margin-bottom: 16px;
  padding: 10px;  /* 添加内边距确保标签完全显示 */
}

.report-summary {
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: var(--radius);
  background-color: var(--color-card-hover);
  margin-bottom: 8px;
}

.summary-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-right: 12px;
}

.summary-info {
  flex: 1;
}

.summary-title {
  font-weight: 500;
}

.summary-value {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.report-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.settings-list {
  margin-bottom: 12px;
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
}

.settings-item:last-child {
  border-bottom: none;
}

.settings-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-info i {
  color: var(--color-primary);
}

.settings-more {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  color: var(--color-primary);
  text-decoration: none;
}

.text-primary { color: var(--color-primary); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-danger); }
</style>
