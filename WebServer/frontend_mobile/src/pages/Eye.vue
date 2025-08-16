<template>
  <div class="mobile-page">
    <div class="page-heading">用眼监护</div>
    
    <!-- 标签页导航 -->
    <div class="eye-tabs">
      <div class="tab-nav">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'trends' }"
          @click="activeTab = 'trends'"
        >
          <i class="bi bi-graph-up"></i>
          护眼趋势
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'environment' }"
          @click="activeTab = 'environment'"
        >
          <i class="bi bi-brightness-high"></i>
          光照环境
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'heatmap' }"
          @click="activeTab = 'heatmap'"
        >
          <i class="bi bi-grid-3x3-gap"></i>
          时间热力图
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'data' }"
          @click="activeTab = 'data'"
        >
          <i class="bi bi-bar-chart"></i>
          用眼数据
        </button>
      </div>
    </div>

    <!-- 护眼趋势标签页 -->
    <div v-show="activeTab === 'trends'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📈 护眼行为趋势图</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <canvas ref="trendsChart" class="chart-canvas"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 光照环境标签页 -->
    <div v-show="activeTab === 'environment'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">🔆 光照环境雷达图</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <div ref="radarChart" class="chart-canvas"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 时间热力图标签页 -->
    <div v-show="activeTab === 'heatmap'" class="tab-content-panel">
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">🕒 用眼时间热力图</div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container">
            <div ref="heatmapChart" class="chart-canvas"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用眼数据标签页 -->
    <div v-show="activeTab === 'data'" class="tab-content-panel">
      <!-- 用眼数据仪表盘 -->
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📊 用眼数据</div>
        </div>
        <div class="mobile-card-content">
          <div class="eye-data-container">
            <div class="eye-distance-wrapper">
              <div class="eye-distance-gauge">
                <div ref="gaugeChart" class="gauge-chart"></div>
              </div>
              <div class="eye-distance-label">当前距离</div>
            </div>
            
            <div class="eye-stats">
              <div class="eye-stat-item">
                <i class="bi bi-clock-history"></i>
                <div>
                  <div class="stat-value">{{ eyeData.focus_time || '-' }} 分钟</div>
                  <div class="stat-label">连续用眼时间</div>
                </div>
              </div>
              
              <div class="eye-stat-item">
                <i class="bi bi-eye-fill"></i>
                <div>
                  <div class="stat-value">{{ eyeData.blink_rate || '-' }} 次/分钟</div>
                  <div class="stat-label">眨眼频率</div>
                </div>
              </div>
              
              <div class="eye-stat-item">
                <i class="bi bi-rulers"></i>
                <div>
                  <div class="stat-value">{{ eyeData.distance || '-' }} cm</div>
                  <div class="stat-label">眼睛距离</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 每日反馈卡片 -->
      <div class="mobile-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">📝 每日反馈</div>
        </div>
        <div class="mobile-card-content">
          <div class="feedback-list">
            <div class="feedback-item good">
              <span class="feedback-icon">✅</span>
              <div class="feedback-content">
                <div class="feedback-title">本周平均远眺次数</div>
                <div class="feedback-value">4.3 次/天</div>
              </div>
            </div>
            <div class="feedback-item good">
              <span class="feedback-icon">🌤</span>
              <div class="feedback-content">
                <div class="feedback-title">当前环境光照</div>
                <div class="feedback-value">良好</div>
              </div>
            </div>
            <div class="feedback-item good">
              <span class="feedback-icon">🌡</span>
              <div class="feedback-content">
                <div class="feedback-title">色温状态</div>
                <div class="feedback-value">柔和</div>
              </div>
            </div>
            <div class="feedback-item warning">
              <span class="feedback-icon">⚠️</span>
              <div class="feedback-content">
                <div class="feedback-title">昨日连续用眼超时</div>
                <div class="feedback-value">72 分钟</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 用眼建议 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">💡 用眼建议</div>
      </div>
      <div class="mobile-card-content">
        <div class="eye-tips">
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>保持40-50cm的屏幕距离</span>
          </div>
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>每用眼30-40分钟，休息10分钟</span>
          </div>
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>避免在黑暗环境下长时间用眼</span>
          </div>
          <div class="tip-item">
            <i class="bi bi-check-circle-fill text-success"></i>
            <span>定期进行远眺放松眼部肌肉</span>
          </div>
        </div>
        
        <van-button block type="primary" class="reminder-button">
          <i class="bi bi-bell"></i>
          <span>设置休息提醒</span>
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue';
import Chart from 'chart.js/auto';
import * as echarts from 'echarts';
import { monitorApi } from '../api';

// 活动标签页
const activeTab = ref('trends');

// 图表组件引用
const trendsChart = ref(null);
const radarChart = ref(null);
const heatmapChart = ref(null);
const gaugeChart = ref(null);

// 图表实例
let charts = {};

const eyeData = reactive({
  blink_rate: '-',
  distance: '-',
  focus_time: '-'
});

// 初始化图表
const initCharts = async () => {
  await nextTick();
  
  // 护眼趋势图 - Chart.js 折线图（对接后端 /monitor/eye/trends）
  if (trendsChart.value) {
    const ctx = trendsChart.value.getContext('2d');
    charts.trends = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { beginAtZero: true } }
      }
    });
    try {
      const trend = await monitorApi.getEyeTrends();
      const labels = trend?.labels || ['00:00','04:00','08:00','12:00','16:00','20:00'];
      const ds = trend?.datasets || [
        { label: '眨眼频率', data: [15,18,22,19,16,20], borderColor: '#3b82f6' },
        { label: '用眼距离', data: [45,42,38,41,44,46], borderColor: '#10b981' }
      ];
      charts.trends.data.labels = labels;
      charts.trends.data.datasets = ds.map(d => ({
        ...d,
        backgroundColor: (d.borderColor || '#3b82f6') + '22',
        fill: true,
        tension: 0.35
      }));
      charts.trends.update('active');
    } catch(e) {
      // fallback 保留空图或默认数据
    }
  }
};

// 延迟初始化ECharts图表，避免在隐藏状态下初始化导致尺寸问题
const initEChartsLazy = async () => {
  await nextTick();
  
  // 光照环境雷达图 - ECharts（对接 /monitor/eye/environment）
  if (radarChart.value && !charts.radar) {
    charts.radar = echarts.init(radarChart.value);
    try {
      const env = await monitorApi.getEyeEnvironment();
      const indicators = (env?.labels || ['环境光','屏幕亮度','对比度','色温','反射','眩光']).map(n => ({ name: n, max: 100 }));
      const current = env?.data || [80,75,85,90,70,65];
      const optimal = env?.optimal || [85,80,80,85,75,70];
      charts.radar.setOption({
        radar: { indicator: indicators, radius: '60%' },
        legend: { bottom: 0 },
        series: [{
          type: 'radar',
          data: [
            { value: current, name: '当前环境', areaStyle: { color: 'rgba(59,130,246,0.3)' }, lineStyle: { color: '#3b82f6' } },
            { value: optimal, name: '推荐值', areaStyle: { color: 'rgba(16,185,129,0.2)' }, lineStyle: { color: '#10b981' } }
          ]
        }]
      });
    } catch(e) {
      charts.radar.setOption({ radar: { indicator: [ { name: '亮度', max: 100 }, { name: '对比度', max: 100 }, { name: '色温', max: 100 }, { name: '蓝光', max: 100 }, { name: '闪烁', max: 100 } ] } });
    }
  }

  // 用眼时间热力图 - ECharts（对接 /monitor/eye/heatmap）
  if (heatmapChart.value && !charts.heatmap) {
    charts.heatmap = echarts.init(heatmapChart.value);
    try {
      const hm = await monitorApi.getEyeHeatmap();
      const hours = hm?.hours || ['6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22'];
      const days = hm?.days || ['周一','周二','周三','周四','周五','周六','周日'];
      // 将二维矩阵 data 转换为 [x,y,val] 三元组
      const matrix = Array.isArray(hm?.data) ? hm.data : [];
      const data = [];
      for (let r = 0; r < matrix.length; r++) {
        for (let c = 0; c < (matrix[r] || []).length; c++) {
          data.push([c, r, matrix[r][c]]);
        }
      }
      charts.heatmap.setOption({
      tooltip: {
        position: 'top',
        formatter: function (params) {
          return `${days[params.value[1]]} ${hours[params.value[0]]}<br/>用眼强度: ${params.value[2]}`;
        }
      },
      grid: {
        height: '50%',
        top: '10%'
      },
      xAxis: {
        type: 'category',
        data: hours,
        splitArea: {
          show: true
        },
        axisLabel: {
          interval: 2
        }
      },
      yAxis: {
        type: 'category',
        data: days,
        splitArea: {
          show: true
        }
      },
      visualMap: {
        min: 0,
        max: 10,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '15%',
        inRange: {
          color: ['#e3f2fd', '#90caf9', '#42a5f5', '#1976d2', '#0d47a1']
        }
      },
      series: [{
        name: '用眼强度',
        type: 'heatmap',
          data,
        label: {
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
      });
    } catch(e) {
      // 保留默认空热力图
      charts.heatmap.setOption({ series: [{ type: 'heatmap', data: [] }] });
    }
  }

  // 眼睛距离仪表盘 - ECharts（保留静态外观，数值来自 /monitor/eye 和 /monitor/eye/data）
  if (gaugeChart.value && !charts.gauge) {
    charts.gauge = echarts.init(gaugeChart.value);
    charts.gauge.setOption({
      series: [
        {
          type: 'gauge',
          startAngle: 180,
          endAngle: 0,
          center: ['50%', '75%'],
          radius: '90%',
          min: 0,
          max: 100,
          splitNumber: 5,
          axisLine: {
            lineStyle: {
              width: 6,
              color: [
                [0.3, '#e74c3c'],
                [0.7, '#f39c12'],
                [1, '#27ae60']
              ]
            }
          },
          pointer: {
            icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
            length: '12%',
            width: 20,
            offsetCenter: [0, '-60%'],
            itemStyle: {
              color: 'auto'
            }
          },
          axisTick: {
            length: 12,
            lineStyle: {
              color: 'auto',
              width: 2
            }
          },
          splitLine: {
            length: 20,
            lineStyle: {
              color: 'auto',
              width: 3
            }
          },
          axisLabel: {
            color: '#464646',
            fontSize: 12,
            distance: -60,
            formatter: function (value) {
              if (value === 0) {
                return '近';
              } else if (value === 50) {
                return '适中';
              } else if (value === 100) {
                return '远';
              }
              return '';
            }
          },
          title: {
            offsetCenter: [0, '-20%'],
            fontSize: 14,
            color: '#666'
          },
          detail: {
            fontSize: 20,
            offsetCenter: [0, '-35%'],
            valueAnimation: true,
            formatter: function (value) {
              return Math.round(value * 0.8 + 20) + ' cm';
            },
            color: 'auto'
          },
          data: [ { value: 70, name: '距离监测' } ]
        }
      ]
    });
    // 拉取实时用眼数据，填充小卡与仪表盘读数
    try {
      const detail = await monitorApi.getEyeDetailData();
      if (detail) {
        eyeData.blink_rate = String(detail.blink_rate || '-');
        eyeData.distance = String(detail.distance || '-');
        eyeData.focus_time = String(detail.focus_time || '-');
      }
    } catch(e) { /* 保底显示 */ }
    try {
      const realtime = await monitorApi.getEyeData();
      const dist = Number(realtime?.eyeDistance ?? 50);
      charts.gauge.setOption({ series: [{ detail: { formatter: (v)=> Math.round(v*0.8+20) + ' cm' }, data: [{ value: Math.max(0, Math.min(100, dist)), name: '距离监测' }] }] });
    } catch(e) { /* ignore */ }
  }
};

// 窗口大小改变时重新调整图表
const resizeCharts = () => {
  Object.values(charts).forEach(chart => {
    if (chart && chart.resize) {
      chart.resize();
    }
  });
};

// 刷新特定图表
const resizeChart = (chartName) => {
  if (charts[chartName] && charts[chartName].resize) {
    setTimeout(() => {
      charts[chartName].resize();
    }, 100); // 延迟一点时间确保DOM已经渲染
  }
};

// 监听标签页切换，刷新对应图表
watch(activeTab, async (newTab) => {
  await nextTick();
  
  switch (newTab) {
    case 'trends':
      // Chart.js 图表通常不需要手动 resize
      if (charts.trends) {
        charts.trends.update();
      }
      break;
    case 'environment':
      // 如果雷达图还没初始化，先初始化
      if (!charts.radar) {
        await initEChartsLazy();
      }
      resizeChart('radar');
      break;
    case 'heatmap':
      // 如果热力图还没初始化，先初始化
      if (!charts.heatmap) {
        await initEChartsLazy();
      }
      resizeChart('heatmap');
      break;
    case 'data':
      // 如果仪表盘还没初始化，先初始化
      if (!charts.gauge) {
        await initEChartsLazy();
      }
      resizeChart('gauge');
      break;
  }
});

// 加载数据
onMounted(async () => {
  // 初始化 Chart.js 图表（护眼趋势图，默认可见）并对接真实接口
  await initCharts();
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeCharts);
});
</script>

<style scoped>
.page-heading {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

/* 标签页导航 */
.eye-tabs {
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
  transition: all 0.3s ease;
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
  box-shadow: 0 2px 8px rgba(var(--color-primary-rgb), 0.3);
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

.eye-data-container {
  display: flex;
  flex-direction: column;
}

.eye-distance-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
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

.gauge-chart {
  width: 100%;
  height: 200px;
}

.eye-distance-gauge {
  width: 100%;
  height: auto;
  margin: 0 auto;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.eye-distance-label {
  margin-top: -25px;
  font-size: 14px;
  color: var(--color-text-secondary);
  text-align: center;
}

.eye-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.eye-stat-item {
  background-color: var(--color-card-hover);
  padding: 12px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
}

.eye-stat-item i {
  font-size: 24px;
  margin-right: 12px;
  color: var(--color-primary);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
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
  
  .gauge-chart {
    height: 180px;
  }
}

.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-danger); }

/* 用眼建议样式 */
.eye-tips {
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
</style>