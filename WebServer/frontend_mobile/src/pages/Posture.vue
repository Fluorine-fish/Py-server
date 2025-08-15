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
  
                <!-- 图像记录 tab -->
                <div v-if="activeTab==='images'" class="mobile-card">
                  <div class="mobile-card-header">
                    <div class="mobile-card-title">图像记录</div>
                  </div>
                  <div class="mobile-card-content">
                    <div v-if="loadingImages" style="text-align:center;padding:12px;color:#666">加载中...</div>
                    <div v-else class="image-grid">
                      <div v-for="img in postureImages" :key="img.id" class="image-item" @click="viewImage(img)">
                        <img :src="img.thumbnail" alt="posture" />
                        <div class="image-time">{{ new Date(img.timestamp).toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'}) }}</div>
                      </div>
                    </div>
                    <div v-if="!loadingImages && hasMoreImages" style="text-align:center;margin-top:8px">
                      <button class="load-more" @click="loadMoreImages">加载更多</button>
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
              
              <!-- 右侧：快捷工具区域 -->
              <div class="tools-section-unified">
                <div class="tools-header">
                  <h4 class="tools-title">快捷工具</h4>
                </div>
                <div class="tools-list">
                  <button class="tool-button-unified tool-analysis" @click="activeTab = 'proportion'">
                    <div class="tool-icon-unified">
                      <i class="bi bi-pie-chart"></i>
                    </div>
                    <div class="tool-text-unified">坐姿分析</div>
                  </button>
                  <button class="tool-button-unified tool-posture" @click="activeTab = 'distribution'">
                    <div class="tool-icon-unified">
                      <i class="bi bi-calendar-week"></i>
                    </div>
                    <div class="tool-text-unified">不良姿态</div>
                  </button>
                  <button class="tool-button-unified tool-gallery" @click="activeTab = 'images'">
                    <div class="tool-icon-unified">
                      <i class="bi bi-images"></i>
                    </div>
                    <div class="tool-text-unified">图像记录</div>
                  </button>
                  <button class="tool-button-unified tool-reminder reminder-btn" @click="setReminder">
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
      </div>

      <!-- 坐姿时间占比直接显示 -->
      <div class="mobile-card posture-tabs-card">
        <div class="posture-tab-panel">
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
                <canvas id="posturePieChart" ref="pieCanvas"></canvas>
              </div>
              
              <!-- 图例说明 - 包含数值的2x2布局 -->
              <div class="chart-legend-grid">
                <div class="legend-item-styled">
                  <span class="legend-dot good"></span>
                  <span class="legend-text-with-value">良好坐姿 {{ postureStats.goodTime }}h</span>
                </div>
                <div class="legend-item-styled">
                  <span class="legend-dot mild"></span>
                  <span class="legend-text-with-value">轻度不良 {{ mildHours }}h</span>
                </div>
                <div class="legend-item-styled">
                  <span class="legend-dot moderate"></span>
                  <span class="legend-text-with-value">中度不良 {{ moderateHours }}h</span>
                </div>
                <div class="legend-item-styled">
                  <span class="legend-dot severe"></span>
                  <span class="legend-text-with-value">严重不良 {{ severeHours }}h</span>
                </div>
              </div>
              
              <!-- 底部统计数据 - 按照截图的3个并排蓝色数字卡片 -->
              <div class="stats-cards-row">
                <div class="stat-card">
                  <div class="stat-number-blue">{{ postureStats.goodTime }}h</div>
                  <div class="stat-desc-gray">良好坐姿</div>
                </div>
                <div class="stat-card">
                  <div class="stat-number-blue">{{ postureStats.badTime }}h</div>
                  <div class="stat-desc-gray">不良坐姿</div>
                </div>
                <div class="stat-card">
                  <div class="stat-number-blue">{{ postureStats.goodRate }}%</div>
                  <div class="stat-desc-gray">良好率</div>
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
      :style="{ height: '40%' }"
    >
      <div class="reminder-popup">
        <div class="reminder-header">
          <h3>设置提醒间隔</h3>
          <van-icon name="cross" @click="showReminderPopup = false" class="close-btn" />
        </div>
        <div class="reminder-options">
          <div 
            class="reminder-option-card" 
            :class="{ 'active': selectedReminderInterval === 30 }"
            @click="selectReminderInterval(30)"
          >
            <div class="option-time">30分钟</div>
            <div class="option-desc">适合长时间工作</div>
            <van-icon name="success" class="check-icon" v-if="selectedReminderInterval === 30" />
          </div>
          <div 
            class="reminder-option-card" 
            :class="{ 'active': selectedReminderInterval === 60 }"
            @click="selectReminderInterval(60)"
          >
            <div class="option-time">1小时</div>
            <div class="option-desc">日常使用推荐</div>
            <van-icon name="success" class="check-icon" v-if="selectedReminderInterval === 60" />
          </div>
          <div 
            class="reminder-option-card" 
            :class="{ 'active': selectedReminderInterval === 90 }"
            @click="selectReminderInterval(90)"
          >
            <div class="option-time">1.5小时</div>
            <div class="option-desc">轻度使用模式</div>
            <van-icon name="success" class="check-icon" v-if="selectedReminderInterval === 90" />
          </div>
        </div>
        <div class="reminder-actions">
          <van-button 
            type="primary" 
            block 
            round
            @click="confirmReminderInterval"
            :disabled="!selectedReminderInterval"
            class="confirm-btn"
          >
            确认设置
          </van-button>
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
const pieCanvas = ref(null)
const handleResize = () => pieChartInstance?.resize()
let barChartInstance = null

// tab控制
const activeTab = ref('proportion')

// 时间范围控制
const selectedTimeRange = ref('day')
const timePeriod = ref('today') // 新增饼图时间段切换状态

// 基于时间段的坐姿数据（将由后端真实数据填充）
const postureDataByPeriod = ref({
  today: { labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'], data: [0, 0, 0, 0], rawSeconds: [0,0,0,0], totalSeconds: 0 },
  week: { labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'], data: [0, 0, 0, 0], rawSeconds: [0,0,0,0], totalSeconds: 0 }
})

// 坐姿数据相关状态
const postureStats = ref({
  goodTime: '0.0',
  mildTime: '0.0',
  badTime: '0.0',
  goodRate: '0'
})

const problemTimeSlot = ref('下午3-5点')
const improvementMessage = ref('本周坐姿改善效果明显，请继续保持良好习惯。')

// 提醒设置相关状态
const showReminderPopup = ref(false)
const selectedReminderInterval = ref(null) // 当前选中的提醒间隔
const currentReminderInterval = ref(60) // 当前生效的提醒间隔，默认1小时

// 图像记录相关状态
const postureImages = ref([])
const loadingImages = ref(false)
const currentPage = ref(1)
const hasMoreImages = ref(true)

// 坐姿状态相关
const postureStatusClass = computed(() => {
  const score = monitorStore.postureData.currentScore
  if (score === null) return ''
  if (score >= 80) return 'status-good'
  if (score >= 60) return 'status-warning'
  return 'status-bad'
})

const postureStatusText = computed(() => {
  const s = monitorStore.postureData.currentScore
  if (s === null) return '等待检测'
  if (s > 70) return '优秀'
  if (s > 62) return '及格'
  if (s >= 55) return '一般'
  return '需纠正'
})

// 动态计算当前时间段的数据百分比
const currentPeriodData = computed(() => {
  const data = postureDataByPeriod.value[timePeriod.value]
  if (!data) return { good: 0, mild: 0, moderate: 0, severe: 0 }
  return {
    good: data.data[0] || 0,
    mild: data.data[1] || 0, 
    moderate: data.data[2] || 0,
    severe: data.data[3] || 0
  }
})

// 各等级对应的时长（小时），来自后端 rawSeconds
const mildHours = computed(() => {
  const data = postureDataByPeriod.value[timePeriod.value]
  const s = data?.rawSeconds?.[1] || 0
  return (s/3600).toFixed(1)
})
const moderateHours = computed(() => {
  const data = postureDataByPeriod.value[timePeriod.value]
  const s = data?.rawSeconds?.[2] || 0
  return (s/3600).toFixed(1)
})
const severeHours = computed(() => {
  const data = postureDataByPeriod.value[timePeriod.value]
  const s = data?.rawSeconds?.[3] || 0
  return (s/3600).toFixed(1)
})

// 视频URL
const videoUrl = ref('/api/video')

// 更改时间范围
const changeTimeRange = (range) => {
  selectedTimeRange.value = range
  fetchPostureData(range)
}

// 新增：饼图时间段切换方法
const changeTimePeriod = async (period) => {
  timePeriod.value = period
  await fetchPostureData(period)
  updatePieChart(period)
}

// 更新饼图数据
const normKey = (p) => (p === 'day' ? 'today' : p)
const updatePieChart = (period) => {
  const key = normKey(period)
  if (pieChartInstance && postureDataByPeriod.value[key]) {
    const data = postureDataByPeriod.value[key]
    pieChartInstance.data.datasets[0].data = data.data
    pieChartInstance.update('active')
  }
}

// 获取坐姿数据（真实后端）
const fetchPostureData = async (range) => {
  try {
  const map = { today: 'day', week: 'week', day: 'day' }
  const timeRange = map[range] || 'day'
    const res = await fetch(`/api/monitor/posture/distribution?timeRange=${timeRange}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    // data: { labels, data:[%], rawSeconds:[good,mild,moderate,severe], totalSeconds }
    const labels = Array.isArray(data.labels) ? data.labels.map(l=>{
      // PC返回的中文短标签，映射为移动端显示
      if (l === '良好') return '良好坐姿'
      if (l === '轻度') return '轻度不良'
      if (l === '中度') return '中度不良'
      if (l === '重度') return '严重不良'
      return l
    }) : ['良好坐姿','轻度不良','中度不良','严重不良']
    const percents = Array.isArray(data.data) ? data.data : [0,0,0,0]
    const raw = Array.isArray(data.rawSeconds) ? data.rawSeconds : [0,0,0,0]
    const [goodS=0, mildS=0, moderateS=0, severeS=0] = raw
    const badS = mildS + moderateS + severeS
    const h = (s)=> (s/3600).toFixed(1)

  // 更新period缓存（统一键为today/week）
  const key = normKey(range)
  postureDataByPeriod.value[key] = {
      labels,
      data: percents,
      rawSeconds: raw,
      totalSeconds: data.totalSeconds || (goodS+badS)
    }

    // 更新饼图
  updatePieChart(key)

    // 更新底部统计
    postureStats.value = {
      goodTime: h(goodS),
      mildTime: h(mildS),
      badTime: h(badS),
      goodRate: String(percents[0] || 0)
    }
  } catch (error) {
    console.error('获取坐姿数据失败:', error)
    showNotify({ type: 'warning', message: '坐姿占比数据暂不可用' })
  }
}

// 初始化图表
const initCharts = async () => {
  // 初始化坐姿饼图 - 按照图示风格配置
  await nextTick()
  const canvasEl = pieCanvas.value || document.getElementById('posturePieChart')
  // 等待画布可见且有尺寸
  const waitForSize = async () => new Promise(resolve => {
    let attempts = 0
    const tick = () => {
      attempts++
      const el = canvasEl
      if (el && el.offsetWidth > 0 && el.offsetHeight > 0) return resolve()
      if (attempts > 20) return resolve()
      requestAnimationFrame(tick)
    }
    tick()
  })
  await waitForSize()

  if (canvasEl) {
    const currentData = postureDataByPeriod.value[timePeriod.value]
    // 如已存在则销毁，避免重复实例
    if (pieChartInstance) {
      try { pieChartInstance.destroy() } catch (e) {}
      pieChartInstance = null
    }
    const ctx = canvasEl.getContext('2d')
  pieChartInstance = new Chart(ctx, {
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
  maintainAspectRatio: false,
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
  // 初始后进行一次尺寸校正
  try { pieChartInstance.resize() } catch (e) {}
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
  selectedReminderInterval.value = currentReminderInterval.value
  showReminderPopup.value = true
}

const selectReminderInterval = (minutes) => {
  selectedReminderInterval.value = minutes
}

const confirmReminderInterval = () => {
  if (selectedReminderInterval.value) {
    currentReminderInterval.value = selectedReminderInterval.value
    showNotify({ 
      type: 'success', 
      message: `已设置${selectedReminderInterval.value}分钟提醒间隔` 
    })
    showReminderPopup.value = false
    
    // 这里可以调用API保存设置
    // await saveReminderSettings(selectedReminderInterval.value)
  }
}

const setReminderInterval = (minutes) => {
  showNotify({ type: 'success', message: `已设置${minutes}分钟提醒间隔` })
  showReminderPopup.value = false
}

// 图像相关方法（真实后端）
const fetchImages = async () => {
  try{
    loadingImages.value = true
    const res = await fetch(`/api/monitor/posture/images?page=${currentPage.value}&limit=8`)
    const json = await res.json()
    const arr = Array.isArray(json) ? json : (json.data || [])
    if(currentPage.value===1) postureImages.value = []
    postureImages.value.push(...arr.map(it=>({
      id: it.id,
      url: it.url,
      thumbnail: it.thumbnail || it.url,
      timestamp: it.timestamp
    })))
    hasMoreImages.value = arr.length === 8
  }catch(e){
    console.error('加载图像失败', e)
  }finally{
    loadingImages.value = false
  }
}
const loadMoreImages = async () => { currentPage.value++; await fetchImages() }
const viewImage = (image) => { window.open(image.url, '_blank') }

// 生命周期
onMounted(async () => {
  await monitorStore.fetchPostureData()
  // 预拉取“今日”和“本周”的真实数据
  await fetchPostureData('today')
  await fetchPostureData('week')
  await initCharts()
  // 预加载图像列表
  await fetchImages()
  // 监听窗口尺寸变化，保持自适应
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  if (pieChartInstance) {
    pieChartInstance.destroy()
  }
  if (barChartInstance) {
    barChartInstance.destroy()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* 简易图片网格 */
.image-grid{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }
.image-item{ position:relative; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.06); }
.image-item img{ width:100%; height:120px; object-fit:cover; display:block; }
.image-item .image-time{ position:absolute; right:6px; bottom:6px; background:rgba(0,0,0,.55); color:#fff; font-size:12px; padding:2px 6px; border-radius:4px; }
.load-more{ background:#fff; border:1px solid #e0e0e0; padding:6px 12px; border-radius:6px; }
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

/* 统一的工具按钮样式 */
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
  /* 重置button默认样式 */
  outline: none;
  font-family: inherit;
  box-sizing: border-box !important; /* 确保盒模型一致 */
  flex-shrink: 0 !important; /* 防止按钮被压缩 */
  gap: 12px; /* 图标和文字之间的间距 */
  text-decoration: none;
  color: inherit;
}

.tool-button-unified:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 250, 252, 0.9) 100%);
}

.tool-button-unified:active {
  transform: translateY(0);
}

.tool-button-unified:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(116, 198, 157, 0.3);
}

.tool-icon-unified {
  /* 使用圆角矩形，避免变形问题 */
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

/* 不同功能按钮的背景色区分 */
.tool-analysis {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.05) 0%, rgba(156, 39, 176, 0.1) 100%);
  border: 1px solid rgba(156, 39, 176, 0.2);
}

.tool-posture {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.05) 0%, rgba(52, 152, 219, 0.1) 100%);
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.tool-gallery {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.05) 0%, rgba(46, 204, 113, 0.1) 100%);
  border: 1px solid rgba(46, 204, 113, 0.2);
}

.tool-reminder {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05) 0%, rgba(255, 193, 7, 0.1) 100%);
  border: 1px solid rgba(255, 193, 7, 0.2);
}

/* 对应的图标颜色 */
.tool-analysis .tool-icon-unified {
  background: rgba(156, 39, 176, 0.1) !important;
  color: #9c27b0 !important;
}

.tool-posture .tool-icon-unified {
  background: rgba(52, 152, 219, 0.1) !important;
  color: #3498db !important;
}

.tool-gallery .tool-icon-unified {
  background: rgba(46, 204, 113, 0.1) !important;
  color: #2ecc71 !important;
}

.tool-reminder .tool-icon-unified {
  background: rgba(255, 193, 7, 0.1) !important;
  color: #ffc107 !important;
}

/* 饼图容器样式 - 按照图示风格 */
.chart-container-styled {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 280px;
  margin: 20px 0;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
}

#posturePieChart {
  width: 100% !important;
  height: 100% !important;
  display: block;
  max-width: 240px;
  max-height: 240px;
}

/* 图例网格布局 - 2行2列，完全按照截图 */
.chart-legend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
  margin: 20px 0;
  padding: 0 10px;
}

.legend-item-styled {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #3A8469 0%, #4a9c7a 100%);
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(58, 132, 105, 0.2);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-dot.good {
  background: #4CAF50;
}

.legend-dot.mild {
  background: #FFC107;
}

.legend-dot.moderate {
  background: #FF9800;
}

.legend-dot.severe {
  background: #F44336;
}

.legend-text-styled, .legend-text-with-value {
  font-size: 13px;
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 底部数据卡片 - 3个并排的蓝色数字卡片 */
.stats-cards-row {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding: 0 10px;
}

.stat-card {
  flex: 1;
  padding: 16px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-number-blue {
  font-size: 20px;
  font-weight: 700;
  color: #3A8469;
  margin-bottom: 6px;
  line-height: 1;
}

.stat-desc-gray {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* 时间段切换按钮组 */
.time-period-selector {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.period-btn {
  padding: 6px 12px;
  border: 1px solid rgba(116, 198, 157, 0.3);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
  color: #404F48;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}

.period-btn:hover {
  background: rgba(116, 198, 157, 0.1);
  border-color: #74c69d;
  transform: translateY(-1px);
}

.period-btn.active {
  background: linear-gradient(135deg, #3A8469 0%, #4a9c7a 100%);
  border-color: #3A8469;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(58, 132, 105, 0.3);
}

/* 提醒设置弹窗样式 */
.reminder-popup {
  padding: 20px;
  background: #ffffff;
}

.reminder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.reminder-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 4px;
}

.reminder-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.reminder-option-card {
  position: relative;
  padding: 16px 20px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reminder-option-card:hover {
  background: #f0f8f5;
  border-color: #74c69d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 132, 105, 0.15);
}

.reminder-option-card.active {
  background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f5 100%);
  border-color: #3A8469;
  box-shadow: 0 4px 16px rgba(58, 132, 105, 0.2);
}

.option-time {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.option-desc {
  font-size: 13px;
  color: #666;
  font-weight: 400;
}

.check-icon {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  color: #3A8469;
  font-size: 18px;
}

.reminder-actions {
  padding-top: 8px;
}

.confirm-btn {
  background: linear-gradient(135deg, #3A8469 0%, #4a9c7a 100%) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(58, 132, 105, 0.3) !important;
  font-weight: 600 !important;
  height: 44px !important;
}

.confirm-btn:disabled {
  background: #e9ecef !important;
  box-shadow: none !important;
  color: #adb5bd !important;
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

<!-- 引入样式组件 -->
<PostureStyle />
