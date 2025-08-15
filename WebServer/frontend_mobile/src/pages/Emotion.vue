<template>
  <div class="mobile-page">
    <div class="page-heading">情绪监护</div>
    
    <!-- 标签页导航 -->
    <div class="emotion-tabs">
      <div class="tab-nav">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'trends' }"
          @click="activeTab = 'trends'"
        >
          <i class="bi bi-graph-up"></i>
          情绪趋势
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'radar' }"
          @click="activeTab = 'radar'"
        >
          <i class="bi bi-radar"></i>
          情绪雷达
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'distribution' }"
          @click="activeTab = 'distribution'"
        >
          <i class="bi bi-bar-chart"></i>
          情绪分布
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'heatmap' }"
          @click="activeTab = 'heatmap'"
        >
          <i class="bi bi-grid-3x3-gap"></i>
          情绪热力图
        </button>
      </div>
    </div>

    <!-- 情绪趋势标签页 -->
    <div v-show="activeTab === 'trends'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📈 全天情绪波动趋势</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <div ref="trendChart" class="chart-canvas"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 情绪雷达标签页 -->
    <div v-show="activeTab === 'radar'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📊 今日情绪多维分析</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <div ref="radarChart" class="chart-canvas"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 情绪分布标签页 -->
    <div v-show="activeTab === 'distribution'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📊 情绪时段分布</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <div ref="barChart" class="chart-canvas"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 情绪热力图标签页 -->
    <div v-show="activeTab === 'heatmap'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">🔥 周情绪热力图</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <div ref="heatmapChart" class="chart-canvas"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时监控标签页 -->
    <div v-show="activeTab === 'data'" class="tab-content-panel">
      <!-- 实时画面 -->
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">� 情绪数据</div>
        </div>
        <div class="mobile-card-content">
          <div class="emotion-data-container">
            <div class="video-container">
              <img :src="videoUrl" class="video-feed" />
            </div>
            
            <div class="emotion-stats">
              <div class="emotion-stat-item">
                <i class="bi bi-emoji-smile"></i>
                <div>
                  <div class="stat-value">{{ emotionData.happiness || '-' }}%</div>
                  <div class="stat-label">高兴指数</div>
                </div>
              </div>
              
              <div class="emotion-stat-item">
                <i class="bi bi-emoji-frown"></i>
                <div>
                  <div class="stat-value">{{ emotionData.sadness || '-' }}%</div>
                  <div class="stat-label">悲伤指数</div>
                </div>
              </div>
              
              <div class="emotion-stat-item">
                <i class="bi bi-emoji-surprised"></i>
                <div>
                  <div class="stat-value">{{ emotionData.surprise || '-' }}%</div>
                  <div class="stat-label">惊讶指数</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 每日情绪反馈卡片 -->
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📝 每日反馈</div>
        </div>
        <div class="mobile-card-content">
          <div class="feedback-list">
            <div class="feedback-item good">
              <span class="feedback-icon">✅</span>
              <div class="feedback-content">
                <div class="feedback-title">今日主导情绪</div>
                <div class="feedback-value">快乐</div>
              </div>
            </div>
            <div class="feedback-item good">
              <span class="feedback-icon">🌈</span>
              <div class="feedback-content">
                <div class="feedback-title">情绪稳定度</div>
                <div class="feedback-value">良好</div>
              </div>
            </div>
            <div class="feedback-item good">
              <span class="feedback-icon">⭐</span>
              <div class="feedback-content">
                <div class="feedback-title">情绪评分</div>
                <div class="feedback-value">85分</div>
              </div>
            </div>
            <div class="feedback-item warning">
              <span class="feedback-icon">⚠️</span>
              <div class="feedback-content">
                <div class="feedback-title">下午情绪波动</div>
                <div class="feedback-value">需关注</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 情绪建议提醒卡片 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">💡 情绪建议</div>
      </div>
      <div class="mobile-card-content">
        <div class="emotion-tips">
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>与孩子进行一次轻松的谈话</span>
          </div>
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>询问今天在学校或幼儿园的情况</span>
          </div>
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>给予更多的关注和鼓励</span>
          </div>
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>创造积极正面的家庭氛围</span>
          </div>
        </div>
        
        <van-button block type="primary" class="reminder-button">
          <i class="bi bi-bell"></i>
          <span>设置情绪提醒</span>
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import * as echarts from 'echarts';
import { monitorApi } from '../api';

// 活动标签页
const activeTab = ref('trends');

// 图表组件引用
const trendChart = ref(null);
const radarChart = ref(null);
const barChart = ref(null);
const heatmapChart = ref(null);

// 图表实例
let charts = {};

// 情绪数据 - 移除不需要的属性
const emotionData = reactive({
  // 移除实时监控相关数据
});

// 初始化图表
const initCharts = async () => {
  await nextTick();
  
  // 情绪趋势图
  if (trendChart.value && !charts.trend) {
    charts.trend = echarts.init(trendChart.value);
    charts.trend.setOption({
      title: {
        text: '全天情绪波动趋势',
        subtext: '情绪值(-3到3分)',
        left: 'center',
        top: 0,
        textStyle: { color: '#333', fontSize: 14, fontWeight: 'normal' },
        subtextStyle: { color: '#666', fontSize: 12 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: {
        left: '3%', right: '4%', bottom: '3%', containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#666' },
        splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.05)' } }
      },
      series: [{
        name: '情绪值',
        type: 'line',
        smooth: true,
        data: [1, 0, 2, 1, -2, 0, 1],
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(58, 132, 105, 0.5)' },
              { offset: 1, color: 'rgba(58, 132, 105, 0.1)' }
            ]
          }
        },
        lineStyle: { width: 3, color: '#3A8469' },
        itemStyle: { color: '#3A8469' },
        symbolSize: 8
      }]
    });
  }

  // 情绪雷达图
  if (radarChart.value && !charts.radar) {
    charts.radar = echarts.init(radarChart.value);
    charts.radar.setOption({
      title: {
        text: '今日情绪多维分析',
        subtext: '各项情绪指标评分(1-5分)',
        left: 'center',
        top: 0,
        textStyle: { color: '#333', fontSize: 14, fontWeight: 'normal' },
        subtextStyle: { color: '#666', fontSize: 12 }
      },
      tooltip: { trigger: 'item' },
      legend: { data: ['今日情绪'], bottom: 0 },
      radar: {
        indicator: [
          { name: '高兴', max: 5 },
          { name: '悲伤', max: 5 },
          { name: '愤怒', max: 5 },
          { name: '惊讶', max: 5 },
          { name: '平静', max: 5 }
        ],
        radius: '65%',
        splitNumber: 4,
        axisName: { color: '#666' },
        splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.1)' } },
        splitArea: { show: false },
        axisLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.1)' } }
      },
      series: [{
        name: '情绪雷达图',
        type: 'radar',
        data: [{
          value: [4, 2, 1, 3, 4],
          name: '今日情绪',
          areaStyle: { color: 'rgba(58, 132, 105, 0.4)' },
          lineStyle: { width: 2, color: '#3A8469' },
          symbolSize: 6,
          itemStyle: { color: '#3A8469' }
        }]
      }]
    });
  }

  // 情绪分布柱状图
  if (barChart.value && !charts.bar) {
    charts.bar = echarts.init(barChart.value);
    charts.bar.setOption({
      title: {
        text: '情绪时段分布',
        subtext: '不同时段主导情绪分析',
        left: 'center',
        top: 0,
        textStyle: { color: '#333', fontSize: 14, fontWeight: 'normal' },
        subtextStyle: { color: '#666', fontSize: 12 }
      },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['高兴', '平静', '悲伤', '愤怒', '惊讶', '专注'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '18%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['上午', '中午', '下午', '晚上'],
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#666' },
        splitLine: { lineStyle: { color: 'rgba(0, 0, 0, 0.05)' } }
      },
      series: []
    });
    await refreshEmotionDistribution();
  }

  // 情绪热力图
  if (heatmapChart.value && !charts.heatmap) {
    charts.heatmap = echarts.init(heatmapChart.value);
    
    // 生成热力图数据
    const heatmapData = [
      [0, 0, 2], [1, 0, 1], [2, 0, -1], [3, 0, 2], [4, 0, 1], [5, 0, 0], [6, 0, 1],
      [0, 1, 1], [1, 1, 2], [2, 1, 0], [3, 1, 1], [4, 1, 2], [5, 1, 1], [6, 1, 0],
      [0, 2, 0], [1, 2, 1], [2, 2, -2], [3, 2, -1], [4, 2, 0], [5, 2, 1], [6, 2, 2],
      [0, 3, -1], [1, 3, 0], [2, 3, 1], [3, 3, 0], [4, 3, -1], [5, 3, 2], [6, 3, 1],
      [0, 4, 0], [1, 4, 1], [2, 4, 0], [3, 4, -1], [4, 4, 0], [5, 4, 1], [6, 4, 0]
    ];
    
    charts.heatmap.setOption({
      title: {
        text: '周情绪热力图',
        subtext: '情绪值(-2到2分)',
        left: 'center',
        top: 0,
        textStyle: { color: '#333', fontSize: 14, fontWeight: 'normal' },
        subtextStyle: { color: '#666', fontSize: 12 }
      },
      tooltip: {
        position: 'top',
        formatter: function (params) {
          const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
          const times = ['早晨', '上午', '中午', '下午', '晚上'];
          return `${days[params.data[0]]} ${times[params.data[1]]}<br>情绪值: ${params.data[2]}`;
        }
      },
      grid: { top: '15%', left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        splitArea: { show: true },
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' }
      },
      yAxis: {
        type: 'category',
        data: ['早晨', '上午', '中午', '下午', '晚上'],
        splitArea: { show: true },
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' }
      },
      visualMap: {
        min: -2, max: 2, calculable: true, orient: 'horizontal',
        left: 'center', bottom: '0%',
        inRange: { color: ['#F44336', '#FF9800', '#f8f9fa', '#74c69d', '#3A8469'] }
      },
      series: [{
        name: '情绪值', type: 'heatmap', data: heatmapData,
        label: { show: false },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
      }]
    });
  }
};

// 刷新图表尺寸
const resizeCharts = () => {
  Object.values(charts).forEach(chart => {
    if (chart && chart.resize) {
      setTimeout(() => {
        chart.resize();
      }, 100);
    }
  });
};

// 监听标签切换，延迟初始化图表并刷新尺寸
const watchActiveTab = () => {
  nextTick(() => {
    if (activeTab.value === 'trends' && !charts.trend) initCharts();
    if (activeTab.value === 'radar' && !charts.radar) initCharts();
    if (activeTab.value === 'distribution' && !charts.bar) initCharts();
    if (activeTab.value === 'heatmap' && !charts.heatmap) initCharts();
    
    // 延迟刷新图表尺寸
    setTimeout(resizeCharts, 200);
  });
};

// 监听activeTab变化
watch(activeTab, () => {
  watchActiveTab();
});

onMounted(() => {
  initCharts();
  // 首次加载拉取情绪分布
  refreshEmotionDistribution();
  
  // 监听标签切换
  watchActiveTab();
  
  // 监听窗口大小变化，刷新图表
  window.addEventListener('resize', resizeCharts);
  
  // 页面加载后延迟刷新图表尺寸
  setTimeout(resizeCharts, 500);
});

// 组件卸载前清理
onBeforeUnmount(() => {
  // 移除事件监听器
  window.removeEventListener('resize', resizeCharts);
  
  // 销毁图表实例
  Object.values(charts).forEach(chart => {
    if (chart && chart.dispose) {
      chart.dispose();
    }
  });
});

// 拉取后端情绪时段分布并更新柱状图
async function refreshEmotionDistribution() {
  try {
    const resp = await monitorApi.getEmotionDistribution();
    const timeSlots = resp?.timeSlots || ['上午','中午','下午','晚上'];
    const emoData = resp?.emotions || {};
    const mapping = [
      { key: 'happy', name: '高兴', color: '#4CAF50' },
      { key: 'neutral', name: '平静', color: '#9E9E9E' },
      { key: 'sad', name: '悲伤', color: '#F44336' },
      { key: 'angry', name: '愤怒', color: '#FF9800' },
      { key: 'surprised', name: '惊讶', color: '#FFC107' },
      { key: 'focused', name: '专注', color: '#3A86FF' }
    ];
    const series = mapping.map(m => ({
      name: m.name,
      type: 'bar',
      stack: '情绪',
      data: (emoData[m.key] || new Array(timeSlots.length).fill(0)),
      itemStyle: { color: m.color }
    }));
    if (charts.bar) {
      charts.bar.setOption({ xAxis: { data: timeSlots }, series });
      setTimeout(() => charts.bar.resize(), 100);
    }
  } catch (e) {
    console.error('获取情绪分布失败:', e);
  }
}
</script>

<style scoped>
.page-heading {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

/* 标签页导航 */
.emotion-tabs {
  margin-bottom: 16px;
}

.tab-nav {
  display: flex;
  background: var(--color-card);
  border-radius: var(--radius);
  padding: 4px;
  box-shadow: var(--shadow);
}

.tab-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  border: none;
  background: transparent;
  border-radius: var(--radius-small);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: var(--transition);
  cursor: pointer;
  gap: 4px;
}

.tab-btn i {
  font-size: 16px;
  margin-bottom: 2px;
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(58, 132, 105, 0.3);
}

.tab-btn:hover:not(.active) {
  background: var(--color-card-hover);
  color: var(--color-text);
}

/* 标签页内容面板 */
.tab-content-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.emotion-data-container {
  display: flex;
  flex-direction: column;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 280px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

/* 每日反馈样式 */
.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feedback-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: var(--radius);
  background: var(--color-card-hover);
}

.feedback-item.good {
  border-left: 4px solid var(--color-success);
}

.feedback-item.warning {
  border-left: 4px solid var(--color-warning);
}

.feedback-icon {
  font-size: 18px;
  margin-right: 12px;
}

.feedback-content {
  flex: 1;
}

.feedback-title {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 2px;
}

.feedback-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.feedback-item.warning .feedback-value {
  color: var(--color-warning);
}

/* 情绪建议样式 */
.emotion-tips {
  margin-bottom: 16px;
}

.tip-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.tip-item i {
  margin-right: 10px;
}

.reminder-button {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .tab-nav {
    padding: 2px;
  }
  
  .tab-btn {
    padding: 8px 4px;
    font-size: 11px;
  }
  
  .tab-btn i {
    font-size: 14px;
  }
  
  .chart-container {
    padding: 5px;
    height: 240px;
  }
}

.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-danger); }
</style>