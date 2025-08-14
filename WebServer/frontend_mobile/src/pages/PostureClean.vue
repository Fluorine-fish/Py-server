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
              <!-- 饼图容器 - 按照图示风格 -->
              <div class="chart-container-styled">
                <canvas id="posturePieChart"></canvas>
              </div>
              
              <!-- 图例说明 - 按照图示样式 -->
              <div class="chart-legend">
                <div class="legend-row">
                  <div class="legend-item">
                    <span class="legend-dot good"></span>
                    <span class="legend-text">良好坐姿</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-dot mild"></span>
                    <span class="legend-text">轻度不良</span>
                  </div>
                </div>
                <div class="legend-row">
                  <div class="legend-item">
                    <span class="legend-dot moderate"></span>
                    <span class="legend-text">中度不良</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-dot severe"></span>
                    <span class="legend-text">严重不良</span>
                  </div>
                </div>
              </div>
              
              <!-- 统计数据展示 - 按照图示的3个数据框风格 -->
              <div class="stats-summary">
                <div class="stat-box">
                  <div class="stat-number good-color">{{ postureStats.goodTime }}h</div>
                  <div class="stat-desc">良好坐姿</div>
                </div>
                <div class="stat-box">
                  <div class="stat-number warning-color">{{ postureStats.badTime }}h</div>
                  <div class="stat-desc">不良坐姿</div>
                </div>
                <div class="stat-box">
                  <div class="stat-number primary-color">{{ postureStats.goodRate }}%</div>
                  <div class="stat-desc">良好率</div>
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
              <div class="loading-state" v-if="loadingImages">
                <div class="spinner"></div>
                <p>加载中...</p>
              </div>
              
              <div class="image-gallery" v-else>
                <div v-if="postureImages.length === 0" class="empty-state">
                  <div class="empty-icon">
                    <i class="bi bi-camera"></i>
                  </div>
                  <p>暂无图像记录</p>
                  <p class="empty-desc">系统将在检测到不良坐姿时自动记录图像</p>
                </div>
                
                <div v-else class="image-grid">
                  <div 
                    v-for="image in postureImages" 
                    :key="image.id" 
                    class="image-item"
                    @click="viewImage(image)"
                  >
                    <img :src="image.thumbnail" :alt="image.title" />
                    <div class="image-info">
                      <div class="image-time">{{ image.time }}</div>
                      <div class="image-type" :class="image.typeClass">{{ image.type }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="load-more" v-if="postureImages.length > 0">
                  <button class="load-more-btn" @click="loadMoreImages">
                    加载更多
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 设置提醒弹窗 -->
    <van-popup 
      v-model:show="showReminderPopup" 
      position="bottom" 
      round 
      :style="{ height: '30%' }"
    >
      <div class="reminder-popup">
        <h3>设置提醒间隔</h3>
        <div class="reminder-options">
          <div class="reminder-option" @click="setReminderInterval(30)">30分钟</div>
          <div class="reminder-option" @click="setReminderInterval(60)">1小时</div>
          <div class="reminder-option" @click="setReminderInterval(90)">1.5小时</div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useMonitorStore } from '../stores'
import { showNotify } from 'vant'
import Chart from 'chart.js/auto'
import PostureStyle from './PostureStyle.vue'

// Store
const monitorStore = useMonitorStore()

// Chart实例
let pieChartInstance = null
let barChartInstance = null

// tab控制
const activeTab = ref('proportion')

// 时间范围控制
const selectedTimeRange = ref('day')
const timePeriod = ref('today') // 新增饼图时间段切换状态

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
})

// 坐姿数据相关状态
const postureStats = ref({
  goodTime: '3.2',
  mildTime: '1.2',
  badTime: '0.6',
  goodRate: '64'
})

const problemTimeSlot = ref('下午3-5点')
const improvementMessage = ref('本周坐姿改善效果明显，请继续保持良好习惯。')

// 图像记录相关状态
const postureImages = ref([])
const loadingImages = ref(false)
const currentPage = ref(1)

// 坐姿状态相关
const postureStatusClass = computed(() => {
  const score = monitorStore.postureData.currentScore
  if (score === null) return ''
  if (score >= 80) return 'status-good'
  if (score >= 60) return 'status-warning'
  return 'status-bad'
})

const postureStatusText = computed(() => {
  const score = monitorStore.postureData.currentScore
  if (score === null) return '等待检测'
  if (score >= 80) return '坐姿良好'
  if (score >= 60) return '姿势稍差'
  return '姿势不佳'
})

// 动态计算当前时间段的数据百分比
const currentPeriodData = computed(() => {
  const data = postureDataByPeriod.value[timePeriod.value]
  if (!data) return { good: 0, mild: 0, moderate: 0, severe: 0 }
  return {
    good: data.data[0],
    mild: data.data[1], 
    moderate: data.data[2],
    severe: data.data[3]
  }
})

// 视频URL
const videoUrl = ref('/api/video')

// 弹窗控制
const showReminderPopup = ref(false)

// 更改时间范围
const changeTimeRange = (range) => {
  selectedTimeRange.value = range
  fetchPostureData(range)
}

// 新增：饼图时间段切换方法
const changeTimePeriod = (period) => {
  timePeriod.value = period
  updatePieChart(period)
}

// 更新饼图数据
const updatePieChart = (period) => {
  if (pieChartInstance && postureDataByPeriod.value[period]) {
    const data = postureDataByPeriod.value[period]
    pieChartInstance.data.datasets[0].data = data.data
    pieChartInstance.update('active')
  }
}

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
        goodRate: '64'
      },
      week: {
        goodTime: '22.4',
        mildTime: '8.4',
        badTime: '4.2', 
        goodRate: '68'
      },
      month: {
        goodTime: '89.6',
        mildTime: '33.6',
        badTime: '16.8',
        goodRate: '66'
      }
    }
    
    postureStats.value = mockData[range]
  } catch (error) {
    console.error('获取坐姿数据失败:', error)
    showNotify({ type: 'danger', message: '数据加载失败' })
  }
}

// 初始化图表
const initCharts = () => {
  // 初始化坐姿饼图 - 按照图示风格配置
  const pieCtx = document.getElementById('posturePieChart')
  if (pieCtx) {
    const currentData = postureDataByPeriod.value[timePeriod.value]
    pieChartInstance = new Chart(pieCtx, {
      type: 'doughnut',
      data: {
        labels: currentData.labels,
        datasets: [{
          data: currentData.data,
          backgroundColor: [
            '#4CAF50',  // 绿色 - 良好坐姿
            '#FFC107',  // 黄色 - 轻度不良  
            '#FF9800',  // 橙色 - 中度不良
            '#F44336'   // 红色 - 严重不良
          ],
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6,
          hoverBorderWidth: 3
        }]
      },
      options: {
        cutout: '65%',
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: false  // 隐藏默认图例，使用自定义图例
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.label}: ${context.raw}%`
              }
            },
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            titleColor: '#fff',
            bodyColor: '#fff',
            cornerRadius: 8,
            titleFont: {
              size: 14,
              weight: '600'
            },
            bodyFont: {
              size: 13,
              weight: '500'
            },
            padding: 12,
            displayColors: true,
            usePointStyle: true
          }
        },
        interaction: {
          intersect: false,
          mode: 'nearest'
        },
        animation: {
          animateRotate: true,
          animateScale: true,
          duration: 1200,
          easing: 'easeOutQuart'
        }
      }
    })
  }
  
  // 初始化柱状图
  const barCtx = document.getElementById('postureBarChart')
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
                return `${context.raw}次不良姿势`
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
    })
  }
}

// 刷新数据
const refreshData = () => {
  monitorStore.fetchPostureData()
  fetchPostureData(selectedTimeRange.value)
  showNotify({ type: 'success', message: '数据已刷新' })
}

// 设置提醒
const setReminder = () => {
  showReminderPopup.value = true
}

const setReminderInterval = (minutes) => {
  showNotify({ type: 'success', message: `已设置${minutes}分钟提醒间隔` })
  showReminderPopup.value = false
}

// 图像相关方法
const loadMoreImages = () => {
  currentPage.value++
  // 这里应该加载更多图像
}

const viewImage = (image) => {
  // 查看大图
  console.log('查看图像:', image)
}

// 生命周期
onMounted(async () => {
  await monitorStore.fetchPostureData()
  await fetchPostureData(selectedTimeRange.value)
  
  await nextTick()
  initCharts()
})

onBeforeUnmount(() => {
  if (pieChartInstance) {
    pieChartInstance.destroy()
  }
  if (barChartInstance) {
    barChartInstance.destroy()
  }
})
</script>

<!-- 引入样式组件 -->
<PostureStyle />
