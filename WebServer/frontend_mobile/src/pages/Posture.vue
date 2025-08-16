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
  
                <!-- 图像记录已移至下方与饼图同卡标签页 -->
                
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
                  <button class="tool-button-unified tool-analysis" @click="activeTab = 'analysis'">
                    <div class="tool-icon-unified">
                      <i class="bi bi-pie-chart"></i>
                    </div>
                    <div class="tool-text-unified">坐姿分析</div>
                  </button>
                  <button class="tool-button-unified tool-posture" @click="activeTab = 'analysis'">
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

      <!-- 坐姿时间占比（除图像记录外显示） -->
      <div v-show="activeTab!=='images'" class="mobile-card pie-card">
        <div class="mobile-card-header">
          <div class="mobile-card-title">坐姿时间占比</div>
          <div class="time-period-selector">
            <button class="period-btn" :class="{active: timePeriod==='today'}" @click="changeTimePeriod('today')">今日</button>
            <button class="period-btn" :class="{active: timePeriod==='week'}" @click="changeTimePeriod('week')">本周</button>
          </div>
        </div>
        <div class="mobile-card-content">
          <div class="chart-container-styled pie-wrap">
            <canvas ref="pieCanvas"></canvas>
          </div>
          <div class="pie-legend">
            <span><i class="legend-dot dot-good"></i>良好 {{ pieDataHours.good.toFixed(1) }}h</span>
            <span><i class="legend-dot dot-mild"></i>轻度不良 {{ pieDataHours.mild.toFixed(1) }}h</span>
            <span><i class="legend-dot dot-bad"></i>不良 {{ pieDataHours.bad.toFixed(1) }}h</span>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useMonitorStore } from '../stores'
import { showNotify } from 'vant'
import PostureStyle from './PostureStyle.vue'
import Chart from 'chart.js/auto'

// Store
const monitorStore = useMonitorStore()

// tab控制
const activeTab = ref('images')

// 时间范围控制（保留用于其他模块扩展）
const selectedTimeRange = ref('day')

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

// 饼图：时间段与图表实例
const timePeriod = ref('today') // today | week
const pieCanvas = ref(null)
let pieChart = null
const pieDataHours = ref({ good: 2.8, mild: 1.0, bad: 0.5 })

const toStoreRange = (p) => (p === 'today' ? 'day' : 'week')

const buildPieDataset = () => {
  const { good, mild, bad } = pieDataHours.value
  return {
    labels: ['良好坐姿', '轻度不良', '不良坐姿'],
    datasets: [{
      data: [good, mild, bad],
      backgroundColor: ['#34a853', '#ffc107', '#ea4335'],
      borderWidth: 0
    }]
  }
}

const renderPie = async () => {
  if (!pieCanvas.value) return
  await nextTick()
  const ctx = pieCanvas.value.getContext('2d')
  if (pieChart) { pieChart.destroy() }
  pieChart = new Chart(ctx, {
    type: 'pie',
    data: buildPieDataset(),
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'bottom', labels: { boxWidth: 12 } },
        tooltip: { enabled: true }
      }
    }
  })
}

const loadPieData = async () => {
  try {
    const range = toStoreRange(timePeriod.value)
    const data = await monitorStore.fetchPostureHistoryByTimeRange(range)
    // data 可能是字符串，做解析并容错
    const good = parseFloat(data?.goodTime ?? 0) || 0
    const mild = parseFloat(data?.mildTime ?? 0) || 0
    const bad = parseFloat(data?.badTime ?? 0) || 0
    // 保证非负
    pieDataHours.value = {
      good: Math.max(0, good),
      mild: Math.max(0, mild),
      bad: Math.max(0, bad)
    }
  } catch (e) {
    // 保留默认占位
    console.error('加载坐姿占比失败', e)
  } finally {
    if (activeTab.value !== 'images') await renderPie()
  }
}

const changeTimePeriod = async (p) => {
  if (timePeriod.value === p) return
  timePeriod.value = p
  await loadPieData()
}

// 视频URL
const videoUrl = ref('/api/video')

// 更改时间范围（保留占位）
const changeTimeRange = (range) => { selectedTimeRange.value = range }

// 本页不再包含占比饼图与柱状图

// 刷新数据
const refreshData = () => {
  monitorStore.fetchPostureData()
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

// 图像相关方法（真实后端，分页）
const fetchImages = async () => {
  try{
    loadingImages.value = true
    const res = await fetch(`/api/monitor/posture/images?page=${currentPage.value}&limit=${pageSize.value}`)
    const json = await res.json()
    const arr = Array.isArray(json) ? json : (json.data || [])
    totalItems.value = Number(json.total || arr.length)
    totalPages.value = Math.max(1, Math.ceil(totalItems.value / pageSize.value))
    postureImages.value = arr.map(it => ({
      id: it.id,
      url: it.url,
      thumbnail: it.thumbnail || it.url,
      timestamp: it.timestamp,
      is_good_posture: typeof it.is_good_posture === 'boolean' ? it.is_good_posture : true
    }))
  }catch(e){
    console.error('加载图像失败', e)
  }finally{
    loadingImages.value = false
  }
}
const pageSize = ref(8)
const totalPages = ref(1)
const totalItems = ref(0)
const prevPage = async () => { if(currentPage.value>1){ currentPage.value--; await fetchImages() } }
const nextPage = async () => { if(currentPage.value<totalPages.value){ currentPage.value++; await fetchImages() } }
const viewImage = (image) => { window.open(image.url, '_blank') }

// 从文件名/ID提取时间（命名形如 posture_YYYYMMDD_HHMMSS_随机值.jpg）
const formatTimeFromFilename = (img) => {
  try {
    const filename = ((img && (img.url || img.thumbnail)) || '').split('/').pop() || ''
    const id = img?.id || ''
    const candidate = `${id} ${filename}`
    // 优先匹配 YYYYMMDD_HHMMSS（推荐命名），兼容无分隔 YYYYMMDDHHMMSS
    let m = candidate.match(/(\d{8})_(\d{6})(?:_|\.|$)/)
    if (!m) m = candidate.match(/(\d{8})(\d{6})(?:_|\.|$)/)
    if (m) {
      const hh = m[2].slice(0,2)
      const mm = m[2].slice(2,4)
      const ss = m[2].slice(4,6)
      return `${hh}:${mm}:${ss}`
    }
    // 回退到 timestamp（ISO）
    if (img && img.timestamp) {
      const d = new Date(img.timestamp)
      if (!isNaN(d)) return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  } catch (e) {}
  return '--:--'
}

// 生命周期
onMounted(async () => {
  await monitorStore.fetchPostureData()
  // 预加载图像列表
  await fetchImages()
  // 初始化饼图数据
  await loadPieData()
})

// 不再有图表实例，卸载钩子省略
watch(activeTab, async (v) => {
  if (v !== 'images') {
    await nextTick()
    await renderPie()
  }
})
</script>

<style scoped>
/* 图片网格优化 */
.image-grid{ display:grid; grid-template-columns:1fr; gap:12px; }
.image-item{ position:relative; border-radius:10px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,.08); background:#f6f7f9; }
.image-item img{ width:100%; aspect-ratio:4/3; object-fit:cover; display:block; }
.image-item .image-time{ position:absolute; right:8px; bottom:8px; background:rgba(0,0,0,.55); color:#fff; font-size:12px; padding:4px 8px; border-radius:6px; }
.image-item .image-badge{ position:absolute; left:8px; top:8px; font-size:12px; padding:2px 8px; border-radius:999px; color:#fff; box-shadow:0 1px 3px rgba(0,0,0,.2); }
.image-item .image-badge.good{ background:#34a853; }
.image-item .image-badge.bad{ background:#ea4335; }

/* 分页 */
.pagination{ display:flex; align-items:center; justify-content:center; gap:12px; margin-top:12px; }
.page-btn{ background:#fff; border:1px solid #e0e0e0; padding:6px 12px; border-radius:8px; color:#333; }
.page-btn:disabled{ opacity:.5; }
.page-info{ color:#666; font-size:13px; }
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

/* 与已移除的饼图与统计卡片相关的样式已清理 */

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

/* 坐姿时间占比 饼图样式（简洁版） */
.pie-card { margin-top: 12px; }
.pie-wrap { height: 260px; padding: 12px; }
.pie-legend { display:flex; justify-content:center; gap:12px; flex-wrap: wrap; margin-top:8px; font-size:12px; color:#495057; }
.legend-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; vertical-align:middle; }
.dot-good{ background:#34a853; }
.dot-mild{ background:#ffc107; }
.dot-bad{ background:#ea4335; }

@media (min-width: 520px) {
  .image-grid{ grid-template-columns:repeat(2,1fr); }
}

/* 饼图相关基础容器样式 */
.chart-container-styled { display:flex; justify-content:center; align-items:center; background:#fff; border-radius:12px; }

/* 时间段切换按钮组（简化版） */
.time-period-selector { display:flex; gap:8px; margin-left:auto; }
.period-btn { padding:6px 12px; border:1px solid #e0e0e0; border-radius:16px; background:#fff; color:#404F48; font-size:12px; cursor:pointer; }
.period-btn.active { background: linear-gradient(135deg, #3A8469 0%, #4a9c7a 100%); color:#fff; border-color:#3A8469; }
</style>

<!-- 引入样式组件 -->
<PostureStyle />
