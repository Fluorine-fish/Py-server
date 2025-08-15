<template>
  <div class="mobile-page">
    <div class="mobile-dashboard">
      <!-- 主要内容区域：统一背景卡片 -->
      <div class="main-content-card">
        <div class="mobile-card">
          <div class="mobile-card-header green-gradient">
            <div class="mobile-card-title main-title-large">坐姿检测</div>
            <div class="refresh-button" @click="refreshData">
              <i class="bi bi-arrow-clockwise"></i>
            </div>
          </div>
          <div class="mobile-card-content">
            <div class="unified-layout">
              <!-- 左侧：视频 + 数据 -->
              <div class="video-stats-section">
                <!-- 视频区域 -->
                <div class="video-container-unified">
                  <img :src="videoUrl" class="video-stream" alt="实时坐姿监测" />
                  <div class="video-overlay">
                    <div class="video-status">
                      <i class="bi bi-circle-fill text-danger"></i> 实时
                    </div>
                    <div class="posture-indicator" :class="postureStatusClass">
                      {{ postureStatusText }}
                    </div>
                  </div>
                </div>
                
                <!-- 坐姿数据区域（在视频下方） -->
                <div class="stats-horizontal-unified">
                  <div class="stat-item-unified">
                    <div class="stat-label">当前得分</div>
                    <div class="stat-value">{{ monitorStore.postureData.currentScore || '-' }}</div>
                  </div>
                  <div class="stat-item-unified">
                    <div class="stat-label">今日提醒</div>
                    <div class="stat-value">{{ monitorStore.postureData.warnCount }}</div>
                  </div>
                  <div class="stat-item-unified">
                    <div class="stat-label">平均得分</div>
                    <div class="stat-value">{{ monitorStore.postureData.averageScore || '-' }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 右侧：快捷按钮 -->
              <div class="tools-section-unified">
                <button class="tool-button-unified" @click="activeTab = 'proportion'">
                  <div class="tool-icon-unified">
                    <i class="bi bi-pie-chart"></i>
                  </div>
                  <div class="tool-text-unified">坐姿分析</div>
                </button>
                <button class="tool-button-unified" @click="activeTab = 'distribution'">
                  <div class="tool-icon-unified">
                    <i class="bi bi-calendar-week"></i>
                  </div>
                  <div class="tool-text-unified">不良姿态</div>
                </button>
                <button class="tool-button-unified" @click="activeTab = 'images'">
                  <div class="tool-icon-unified">
                    <i class="bi bi-images"></i>
                  </div>
                  <div class="tool-text-unified">图像记录</div>
                </button>
                <button class="tool-button-unified reminder-btn" @click="setReminder">
                  <div class="tool-icon-unified">
                    <i class="bi bi-bell"></i>
                  </div>
                  <div class="tool-text-unified">设置提醒</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 时间范围选择器 -->
      <div class="time-range-selector">
        <div 
          class="time-range-btn" 
          :class="{ active: selectedTimeRange === 'day' }" 
          @click="changeTimeRange('day')"
        >今日</div>
        <div 
          class="time-range-btn" 
          :class="{ active: selectedTimeRange === 'week' }" 
          @click="changeTimeRange('week')"
        >本周</div>
        <div 
          class="time-range-btn" 
          :class="{ active: selectedTimeRange === 'month' }" 
          @click="changeTimeRange('month')"
        >本月</div>
      </div>

      <!-- 坐姿分析Tab卡片 -->
      <div class="mobile-card posture-tabs-card">
        <div class="posture-tabs-nav">
          <div 
            class="posture-tab-btn" 
            :class="{ active: activeTab === 'proportion' }" 
            @click="activeTab = 'proportion'"
          >坐姿分析</div>
          <div 
            class="posture-tab-btn" 
            :class="{ active: activeTab === 'distribution' }" 
            @click="activeTab = 'distribution'"
          >不良姿态</div>
          <div 
            class="posture-tab-btn" 
            :class="{ active: activeTab === 'images' }" 
            @click="activeTab = 'images'"
          >图像记录</div>
        </div>
        <div class="posture-tabs-content">
          <!-- 坐姿时间占比tab面板 -->
          <div v-show="activeTab === 'proportion'" class="posture-tab-panel">
            <div class="mobile-card-header">
              <div class="mobile-card-title">坐姿时间占比</div>
              <!-- 时间段切换按钮组 -->
              <div class="time-period-selector">
                <button 
                  class="period-btn" 
                  :class="{ 'active': timePeriod === 'today' }"
                  @click="changeTimePeriod('today')"
                >
                  今日
                </button>
                <button 
                  class="period-btn" 
                  :class="{ 'active': timePeriod === 'week' }"
                  @click="changeTimePeriod('week')"
                >
                  本周
                </button>
              </div>
            </div>
            <div class="mobile-card-content">
              <div class="chart-container">
                <canvas id="posturePieChart" ref="pieCanvas"></canvas>
              </div>
              
              <!-- 统计标签 - 带背景和加粗字体 -->
              <div class="stats-labels-enhanced">
                <div class="stat-label-enhanced good">
                  <span class="stat-indicator good-bg"></span>
                  <span class="stat-text-bold">良好坐姿</span>
                  <span class="stat-percentage-bold">{{ currentPeriodData.good }}%</span>
                </div>
                <div class="stat-label-enhanced warning">
                  <span class="stat-indicator warning-bg"></span>
                  <span class="stat-text-bold">轻度不良</span>
                  <span class="stat-percentage-bold">{{ currentPeriodData.mild }}%</span>
                </div>
                <div class="stat-label-enhanced moderate">
                  <span class="stat-indicator moderate-bg"></span>
                  <span class="stat-text-bold">中度不良</span>
                  <span class="stat-percentage-bold">{{ currentPeriodData.moderate }}%</span>
                </div>
                <div class="stat-label-enhanced severe">
                  <span class="stat-indicator severe-bg"></span>
                  <span class="stat-text-bold">严重不良</span>
                  <span class="stat-percentage-bold">{{ currentPeriodData.severe }}%</span>
                </div>
              </div>
              
              <!-- 传统网格统计信息保持不变 -->
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value" id="goodPostureTime">{{ postureStats.goodTime }}h</div>
                  <div class="stat-label">良好坐姿</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value" id="mildBadPostureTime">{{ postureStats.mildTime }}h</div>
                  <div class="stat-label">轻度不良坐姿</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value" id="badPostureTime">{{ postureStats.badTime }}h</div>
                  <div class="stat-label">不良坐姿</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value" id="postureRate">{{ postureStats.goodRate }}%</div>
                  <div class="stat-label">良好率</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 不良姿态时间分布tab面板 -->
          <div v-show="activeTab === 'distribution'" class="posture-tab-panel">
            <div class="mobile-card-header">
              <div class="mobile-card-title">不良姿态时间分布</div>
              <div class="distribution-icon">
                <i class="bi bi-calendar-week"></i>
              </div>
            </div>
            <div class="mobile-card-content">
              <div class="chart-container">
                <canvas id="postureBarChart"></canvas>
              </div>
              <div class="heatmap-legend">
                <div class="legend-item">
                  <div class="legend-color low"></div>
                  <span>良好</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color medium"></div>
                  <span>一般</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color high"></div>
                  <span>较差</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 坐姿图像记录tab面板 -->
          <div v-show="activeTab === 'images'" class="posture-tab-panel">
            <div class="mobile-card-header">
              <div class="mobile-card-title">坐姿图像记录</div>
              <div class="images-icon">
                <i class="bi bi-images"></i>
              </div>
            </div>
            <div class="mobile-card-content">
              <div class="mobile-image-gallery">
                <div v-if="loadingImages" class="loading-indicator">
                  <i class="bi bi-arrow-clockwise"></i>
                  <span>加载中...</span>
                </div>
                <div v-else-if="postureImages.length === 0" class="no-records">
                  <i class="bi bi-images"></i>
                  <span>暂无图像记录</span>
                </div>
                <div v-else class="image-grid">
                  <div v-for="(image, index) in postureImages" :key="index" class="image-item" @click="previewImage(image)">
                    <img :src="image.url" :alt="`坐姿记录 ${index + 1}`" class="posture-image" />
                    <div class="image-info">
                      <span class="image-time">{{ formatImageTime(image.timestamp) }}</span>
                      <span :class="'image-status ' + getImageStatusClass(image.score)">{{ getImageStatusText(image.score) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="image-actions">
                <van-button class="secondary" @click="loadMoreImages">查看更多</van-button>
                <van-button class="primary" @click="exportImages">导出记录</van-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 坐姿改善建议卡片 -->
      <div class="mobile-card improvement-suggestion">
        <div class="mobile-card-header green-gradient">
          <div class="mobile-card-title">坐姿改善建议</div>
          <div class="suggestion-icon">
            <i class="bi bi-lightbulb"></i>
          </div>
        </div>
        <div class="mobile-card-content">
          <div class="suggestion-content">
            <div class="suggestion-item">
              <div class="suggestion-indicator warning"></div>
              <div class="suggestion-text">
                根据数据分析，坐姿不良率在{{ problemTimeSlot }}时段较高，建议加强这个时段的监督或调整学习环境。
              </div>
            </div>
            <div class="suggestion-item">
              <div class="suggestion-indicator info"></div>
              <div class="suggestion-text">
                {{ improvementMessage }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 坐姿提醒 -->
      <div class="mobile-card">
        <div class="mobile-card-header green-gradient">
          <div class="mobile-card-title">坐姿提醒</div>
        </div>
        <div class="mobile-card-content">
          <div class="posture-tips">
            <div class="tip-item">
              <i class="bi bi-check-circle-fill text-success"></i>
              <span>保持脊柱挺直，肩膀放松</span>
            </div>
            <div class="tip-item">
              <i class="bi bi-check-circle-fill text-success"></i>
              <span>双脚平放在地面上</span>
            </div>
            <div class="tip-item">
              <i class="bi bi-check-circle-fill text-success"></i>
              <span>保持屏幕在视线略低的位置</span>
            </div>
            <div class="tip-item">
              <i class="bi bi-check-circle-fill text-success"></i>
              <span>每隔45-60分钟起身活动</span>
            </div>
          </div>
          
          <van-button block type="primary" class="reminder-button">
            <i class="bi bi-bell"></i>
            <span>设置坐姿提醒</span>
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useMonitorStore } from '../stores';
import Chart from 'chart.js/auto';
import { showToast, showImagePreview } from 'vant';
import './PostureStyle.vue'; // 导入样式

const monitorStore = useMonitorStore();
let pieChartInstance = null;
const pieCanvas = ref(null);
let barChartInstance = null;

// 添加视频地址和刷新功能
const videoUrl = computed(() => '/api/video'); // 改为实时视频流
const refreshData = () => {
  monitorStore.fetchPostureData();
  fetchPostureData(selectedTimeRange.value);
};

// 设置提醒功能
const setReminder = () => {
  showToast('坐姿提醒设置功能即将上线');
};

// tab控制
const activeTab = ref('proportion');

// 时间范围控制
const selectedTimeRange = ref('day');
const timePeriod = ref('today'); // 新增饼图时间段切换状态

// 基于时间段的坐姿数据
const postureDataByPeriod = ref({
  today: {
    labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'],
    data: [64, 18, 12, 6]
  },
  week: {
    labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'], 
    data: [71, 16, 9, 4]
  }
});

// 坐姿数据相关状态
const postureStats = ref({
  goodTime: '3.2',
  mildTime: '1.2',
  badTime: '0.6',
  goodRate: '64'
});

const problemTimeSlot = ref('下午3-5点');
const improvementMessage = ref('本周坐姿改善效果明显，请继续保持良好习惯。');

// 图像记录相关状态
const postureImages = ref([]);
const loadingImages = ref(false);
const currentPage = ref(1);

// 坐姿状态相关
const postureStatusClass = computed(() => {
  const score = monitorStore.postureData.currentScore;
  if (score === null) return '';
  if (score >= 80) return 'status-good';
  if (score >= 60) return 'status-warning';
  return 'status-bad';
});

const postureStatusText = computed(() => {
  const s = monitorStore.postureData.currentScore;
  if (s === null) return '未检测';
  if (s > 70) return '优秀';
  if (s > 62) return '及格';
  if (s >= 55) return '一般';
  return '需纠正';
});

const postureScoreClass = computed(() => {
  const score = monitorStore.postureData.currentScore;
  if (score === null) return '';
  if (score >= 80) return 'score-good';
  if (score >= 60) return 'score-warning';
  return 'score-bad';
});

// 格式化最后检测时间
const lastDetectedTime = computed(() => {
  const lastDetected = monitorStore.postureData.lastDetected;
  if (!lastDetected) return '未知';
  
  try {
    const lastDate = new Date(lastDetected);
    const now = new Date();
    const diffMinutes = Math.floor((now - lastDate) / (1000 * 60));
    
    if (diffMinutes < 1) return '刚刚';
    if (diffMinutes < 60) return `${diffMinutes}分钟前`;
    
    const hours = Math.floor(diffMinutes / 60);
    if (hours < 24) return `${hours}小时前`;
    
    return lastDate.toLocaleDateString();
  } catch (e) {
    return '未知';
  }
});

// 更改时间范围
const changeTimeRange = (range) => {
  selectedTimeRange.value = range;
  fetchPostureData(range);
};

// 新增：饼图时间段切换方法
const changeTimePeriod = (period) => {
  timePeriod.value = period;
  updatePieChart(period);
};

// 更新饼图数据
const updatePieChart = (period) => {
  if (pieChartInstance && postureDataByPeriod.value[period]) {
    const data = postureDataByPeriod.value[period];
    pieChartInstance.data.datasets[0].data = data.data;
    pieChartInstance.update('active');
  }
};

// 获取坐姿数据
const fetchPostureData = async (range) => {
  try {
    // 这里应该调用API获取不同时间范围的数据
    // 先使用模拟数据
    const mockData = {
      day: {
        goodTime: '3.2',
        mildTime: '1.2',
        badTime: '0.6',
        goodRate: '64',
        problemTimeSlot: '下午3-5点',
        improvementMessage: '今天坐姿良好，请继续保持。',
        pieData: [
          { value: 75, name: '良好' },
          { value: 18, name: '轻度不良' },
          { value: 7, name: '不良' }
        ],
        barData: [2, 1, 0, 3, 4, 2, 1, 0, 5, 3, 1, 0]
      },
      week: {
        goodTime: '18.5',
        mildTime: '7.3',
        badTime: '4.2',
        goodRate: '62',
        problemTimeSlot: '周四下午',
        improvementMessage: '本周坐姿改善效果明显，请继续保持良好习惯。',
        pieData: [
          { value: 62, name: '良好' },
          { value: 24, name: '轻度不良' },
          { value: 14, name: '不良' }
        ],
        barData: [3, 2, 1, 5, 7, 4, 2, 1, 8, 6, 3, 1]
      },
      month: {
        goodTime: '72.4',
        mildTime: '31.6',
        badTime: '16.0',
        goodRate: '60',
        problemTimeSlot: '下午时段',
        improvementMessage: '本月总体坐姿较好，但下午时段仍需注意。',
        pieData: [
          { value: 60, name: '良好' },
          { value: 26, name: '轻度不良' },
          { value: 14, name: '不良' }
        ],
        barData: [4, 3, 2, 6, 8, 5, 3, 2, 9, 7, 4, 2]
      }
    };
    
    const data = mockData[range];
    postureStats.value = {
      goodTime: data.goodTime,
      mildTime: data.mildTime,
      badTime: data.badTime,
      goodRate: data.goodRate
    };
    
    problemTimeSlot.value = data.problemTimeSlot;
    improvementMessage.value = data.improvementMessage;
    
    // 更新图表
    updateCharts(data.pieData, data.barData);
  } catch (error) {
    console.error('获取坐姿数据失败', error);
    showToast('获取数据失败，请稍后再试');
  }
};

// 加载坐姿图像记录
const loadPostureImages = async () => {
  loadingImages.value = true;
  try {
    // 这里应该调用API获取图像记录
    // 先使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 800)); // 模拟请求延迟
    
    // 模拟图像数据
    const mockImages = Array.from({ length: 6 }, (_, i) => ({
      id: `img_${currentPage.value}_${i}`,
      url: '/static/mobile/placeholder.jpg', // 使用占位图
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      score: Math.floor(Math.random() * 100)
    }));
    
    if (currentPage.value === 1) {
      postureImages.value = mockImages;
    } else {
      postureImages.value = [...postureImages.value, ...mockImages];
    }
  } catch (error) {
    console.error('加载图像记录失败', error);
    showToast('加载图像记录失败，请稍后再试');
  } finally {
    loadingImages.value = false;
  }
};

// 加载更多图像记录
const loadMoreImages = () => {
  currentPage.value++;
  loadPostureImages();
};

// 预览图像
const previewImage = (image) => {
  showImagePreview({
    images: [image.url],
    closeable: true,
    showIndex: false
  });
};

// 导出图像记录
const exportImages = () => {
  showToast('图像记录导出功能即将上线');
};

// 格式化图像时间
const formatImageTime = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  } catch (e) {
    return '未知时间';
  }
};

// 获取图像状态样式类
const getImageStatusClass = (score) => {
  if (score >= 80) return 'status-good';
  if (score >= 60) return 'status-warning';
  return 'status-bad';
};

// 获取图像状态文本
const getImageStatusText = (score) => {
  if (score >= 80) return '良好';
  if (score >= 60) return '一般';
  return '不良';
};

// 初始化图表
const initCharts = async () => {
  // 初始化坐姿饼图 - 完全照搬HTML中的实现，使用响应式数据
  await nextTick();
  const canvasEl = pieCanvas.value || document.getElementById('posturePieChart');
  // 等待 canvas 可见且有尺寸
  const waitForSize = async () => new Promise(resolve => {
    let attempts = 0;
    const tick = () => {
      attempts++;
      const el = canvasEl;
      if (el && el.offsetWidth > 0 && el.offsetHeight > 0) return resolve();
      if (attempts > 20) return resolve();
      requestAnimationFrame(tick);
    };
    tick();
  });
  await waitForSize();

  if (canvasEl) {
    const currentData = postureDataByPeriod.value[timePeriod.value];
    // 防重复
    if (pieChartInstance) {
      try { pieChartInstance.destroy(); } catch (e) {}
      pieChartInstance = null;
    }
    const ctx = canvasEl.getContext('2d');
    pieChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: currentData.labels,
        datasets: [{
          data: currentData.data,
          backgroundColor: [
            '#34a853',  // 绿色 - 良好坐姿
            '#fbbc05',  // 黄色 - 轻度不良
            '#ff9800',  // 橙色 - 中度不良
            '#ea4335'   // 红色 - 严重不良
          ],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              pointStyle: 'circle',
              color: '#404F48',
              font: {
                size: 14,
                weight: '600'
              }
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.label}: ${context.raw}%`;
              }
            },
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            cornerRadius: 8,
            titleFont: {
              weight: '600'
            },
            bodyFont: {
              weight: '500'
            }
          }
        },
  maintainAspectRatio: false,
        responsive: true,
        interaction: {
          intersect: false
        },
        animation: {
          animateRotate: true,
          animateScale: true,
          duration: 1000
        }
      }
  });
  try { pieChartInstance.resize(); } catch (e) {}
  }
  
  // 初始化柱状图
  const barCtx = document.getElementById('postureBarChart');
  if (barCtx) {
    barChartInstance = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: Array.from({ length: 12 }, (_, i) => `${i*2}-${i*2+2}h`),
        datasets: [{
          label: '不良坐姿次数',
          data: [2, 1, 0, 3, 4, 2, 1, 0, 5, 3, 1, 0],
          backgroundColor: '#3b82f6',
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            cornerRadius: 8,
            titleFont: {
              weight: '600'
            },
            bodyFont: {
              weight: '500'
            },
            callbacks: {
              label: function(context) {
                return `${context.raw}次不良姿势`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#9ca3af',
              font: {
                size: 11,
                weight: '500'
              },
              maxRotation: 45
            }
          },
          y: {
            grid: {
              color: 'rgba(156, 163, 175, 0.2)'
            },
            ticks: {
              color: '#9ca3af',
              font: {
                size: 11,
                weight: '500'
              }
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeOutQuart'
        }
      }
    });
  }
};

// 更新图表数据
const updateCharts = (pieData, barData) => {
  if (pieChartInstance) {
    pieChartInstance.data.datasets[0].data = pieData.map(item => item.value);
    pieChartInstance.update();
  }
  
  if (barChartInstance) {
    barChartInstance.data.datasets[0].data = barData;
    barChartInstance.update();
  }
};

// 处理窗口调整
const handleResize = () => {
  pieChartInstance?.resize();
  barChartInstance?.resize();
};

// 加载数据并初始化图表
onMounted(async () => {
  await monitorStore.fetchPostureData();
  initCharts();
  fetchPostureData('day'); // 默认加载"今日"数据
  loadPostureImages(); // 加载图像记录
  window.addEventListener('resize', handleResize);
});

// 清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  pieChartInstance?.destroy();
  barChartInstance?.destroy();
});
</script>