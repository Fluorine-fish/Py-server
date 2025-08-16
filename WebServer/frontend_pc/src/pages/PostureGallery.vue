<template>
  <div class="posture-gallery-container">
    <van-nav-bar 
      title="坐姿记录库" 
      left-text="返回"
      left-arrow
      fixed
      @click-left="goBack"
    />
    
    <div class="gallery-header">
      <div class="title-section">
        <h1 class="main-title">坐姿图像记录库</h1>
        <p class="subtitle">查看并分析孩子的坐姿记录历史</p>
      </div>
      
      <div class="filter-section">
        <div class="time-filter">
          <van-dropdown-menu>
            <van-dropdown-item v-model="timeRange" :options="timeRangeOptions" />
          </van-dropdown-menu>
        </div>
        
        <div class="type-filter">
          <van-dropdown-menu>
            <van-dropdown-item v-model="filterType" :options="filterTypeOptions" />
          </van-dropdown-menu>
        </div>
      </div>
    </div>
    
    <!-- 统计摘要 -->
    <div class="statistics-summary">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_records }}</div>
        <div class="stat-label">总记录数</div>
      </div>
      <div class="stat-card" :class="{'positive': statistics.improvement.is_better}">
        <div class="stat-value">{{ statistics.improvement.rate }}</div>
        <div class="stat-label">较{{ statistics.improvement.compared_to }}{{ statistics.improvement.is_better ? '提升' : '下降' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ (statistics.distribution.good / statistics.total_records * 100).toFixed(0) }}%</div>
        <div class="stat-label">良好坐姿率</div>
      </div>
    </div>
    
    <!-- 图像网格 -->
    <div v-if="loading" class="loading-container">
      <van-loading type="spinner" color="#4285f4" />
      <p>加载中...</p>
    </div>
    
    <div v-else class="gallery-grid">
      <div 
        v-for="image in images" 
        :key="image.id" 
        class="gallery-item"
        @click="openImageDetail(image)"
      >
        <div class="image-container">
          <img :src="image.thumbnail" :alt="image.posture_type">
          <div :class="['posture-badge', image.is_good_posture ? 'good' : 'bad']">
            {{ image.posture_type }}
          </div>
        </div>
        <div class="image-info">
          <div class="image-time">{{ formatTime(image.timestamp) }}</div>
          <div class="image-score">{{ image.score }}分</div>
        </div>
      </div>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="!loading && images.length === 0" class="no-data">
      <van-empty description="暂无坐姿记录" />
    </div>
    
    <!-- 加载更多 -->
    <div v-if="!loading && hasMore" class="load-more">
      <van-button size="small" type="primary" plain @click="loadMore">加载更多</van-button>
    </div>
    
    <!-- 图像详情弹窗 -->
    <van-popup
      v-model:show="showDetail"
      position="bottom"
      round
      closeable
      class="detail-popup"
    >
      <div v-if="currentImage" class="image-detail">
        <h2 class="detail-title">
          {{ currentImage.posture_type }}
          <span :class="['detail-score', getScoreClass(currentImage.score)]">{{ currentImage.score }}分</span>
        </h2>
        
        <div class="detail-time">记录时间: {{ formatDateTime(currentImage.timestamp) }}</div>
        
        <div class="detail-image-container">
          <img :src="currentImage.url" :alt="currentImage.posture_type" class="detail-image">
        </div>
        
        <div class="detail-analysis">
          <h3>坐姿分析</h3>
          
          <div class="angle-data">
            <div class="angle-item">
              <div class="angle-label">颈部角度</div>
              <div class="angle-value">{{ currentImage.analysis.angles.neck }}°</div>
              <div class="angle-bar">
                <div 
                  class="angle-fill" 
                  :style="{width: `${Math.min(currentImage.analysis.angles.neck/40*100, 100)}%`, backgroundColor: getAngleColor(currentImage.analysis.angles.neck, 20)}"
                ></div>
              </div>
            </div>
            
            <div class="angle-item">
              <div class="angle-label">肩部角度</div>
              <div class="angle-value">{{ currentImage.analysis.angles.shoulder }}°</div>
              <div class="angle-bar">
                <div 
                  class="angle-fill" 
                  :style="{width: `${Math.min(currentImage.analysis.angles.shoulder/25*100, 100)}%`, backgroundColor: getAngleColor(currentImage.analysis.angles.shoulder, 15)}"
                ></div>
              </div>
            </div>
            
            <div class="angle-item">
              <div class="angle-label">背部曲率</div>
              <div class="angle-value">{{ currentImage.analysis.angles.back }}°</div>
              <div class="angle-bar">
                <div 
                  class="angle-fill" 
                  :style="{width: `${Math.min(currentImage.analysis.angles.back/30*100, 100)}%`, backgroundColor: getAngleColor(currentImage.analysis.angles.back, 15)}"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="detail-suggestions">
          <h3>改善建议</h3>
          <ul>
            <li v-for="(suggestion, index) in currentImage.suggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
        
        <div class="detail-environment">
          <h3>环境信息</h3>
          <div class="environment-data">
            <div class="env-item">
              <van-icon name="bulb-o" />
              <span>光照: {{ currentImage.environment.lighting }}</span>
            </div>
            <div class="env-item">
              <van-icon name="desktop-o" />
              <span>屏幕距离: {{ currentImage.environment.screen_distance }}</span>
            </div>
            <div class="env-item">
              <van-icon name="bar-chart-o" />
              <span>桌面高度: {{ currentImage.environment.desk_height }}</span>
            </div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script>
import { reactive, ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'PostureGallery',
  setup() {
    const router = useRouter();
    
    // 状态
    const timeRange = ref('day');
    const filterType = ref('all');
    const currentPage = ref(1);
    const images = ref([]);
    const loading = ref(true);
    const hasMore = ref(true);
    const showDetail = ref(false);
    const currentImage = ref(null);
    const statistics = ref({
      total_records: 0,
      distribution: {
        good: 0,
        mild: 0,
        moderate: 0,
        severe: 0
      },
      improvement: {
        rate: '0%',
        compared_to: '昨天',
        is_better: true
      }
    });
    
    // 选项数据
    const timeRangeOptions = [
      { text: '今日记录', value: 'day' },
      { text: '本周记录', value: 'week' },
      { text: '本月记录', value: 'month' },
    ];
    
    const filterTypeOptions = [
      { text: '全部记录', value: 'all' },
      { text: '良好坐姿', value: 'good' },
      { text: '不良坐姿', value: 'bad' },
    ];
    
    // 监听过滤器变化
    const watchFilters = () => {
      // 监听时间范围变化
      watch(timeRange, (newValue) => {
        currentPage.value = 1;
        images.value = [];
        loadImages();
        loadStatistics();
      });
      
      // 监听筛选类型变化
      watch(filterType, (newValue) => {
        currentPage.value = 1;
        images.value = [];
        loadImages();
      });
    };
    
    // 加载图像数据
    const loadImages = async () => {
      try {
        loading.value = true;
        
        // 调用API获取数据
        const response = await fetch(`/api/monitor/posture/images?page=${currentPage.value}&limit=12&filter_type=${filterType.value}`);
        const json = await response.json();
        const arr = Array.isArray(json) ? json : (json.data || []);
        if (currentPage.value === 1) {
          images.value = arr;
        } else {
          images.value = [...images.value, ...arr];
        }
        // 依据分页信息或返回数量判断是否还有更多
        if (json && typeof json.total === 'number' && typeof json.page === 'number' && typeof json.limit === 'number') {
          const loaded = json.page * json.limit;
          hasMore.value = loaded < json.total;
        } else {
          hasMore.value = arr.length === 12;
        }
      } catch (error) {
        console.error('获取坐姿图像失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 加载统计数据
    const loadStatistics = async () => {
      try {
        const response = await fetch(`/api/monitor/posture/statistics?time_range=${timeRange.value}`);
        statistics.value = await response.json();
      } catch (error) {
        console.error('获取统计数据失败:', error);
      }
    };
    
    // 加载更多
    const loadMore = () => {
      currentPage.value++;
      loadImages();
    };
    
    // 打开图像详情
    const openImageDetail = async (image) => {
      try {
        loading.value = true;
        const response = await fetch(`/api/monitor/posture/images/${image.id}`);
        currentImage.value = await response.json();
        showDetail.value = true;
      } catch (error) {
        console.error('获取图像详情失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 返回上一页
    const goBack = () => {
      router.push('/posture');
    };
    
    // 格式化时间
    const formatTime = (timestamp) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    };
    
    // 格式化日期时间
    const formatDateTime = (timestamp) => {
      const date = new Date(timestamp);
      return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    };
    
    // 获取评分样式
    const getScoreClass = (score) => {
      if (score >= 85) return 'score-good';
      if (score >= 70) return 'score-medium';
      return 'score-bad';
    };
    
    // 获取角度颜色
    const getAngleColor = (angle, threshold) => {
      if (angle <= threshold) return '#34a853';
      if (angle <= threshold * 1.5) return '#fbbc05';
      return '#ea4335';
    };
    
    // 生命周期钩子
    onMounted(() => {
      loadImages();
      loadStatistics();
      watchFilters();
    });
    
    return {
      timeRange,
      filterType,
      timeRangeOptions,
      filterTypeOptions,
      images,
      loading,
      hasMore,
      statistics,
      showDetail,
      currentImage,
      loadMore,
      openImageDetail,
      goBack,
      formatTime,
      formatDateTime,
      getScoreClass,
      getAngleColor
    };
  }
}
</script>

<style scoped>
.posture-gallery-container {
  padding-top: 46px; /* 为固定的NavBar留出空间 */
  padding-bottom: 20px;
  background-color: #f9f9f9;
  min-height: 100vh;
}

.gallery-header {
  padding: 20px;
  background-color: white;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.title-section {
  text-align: center;
  margin-bottom: 20px;
}

.main-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
}

.filter-section {
  display: flex;
  justify-content: space-between;
}

.time-filter,
.type-filter {
  flex: 1;
}

.statistics-summary {
  display: flex;
  justify-content: space-between;
  margin: 0 15px 20px;
  gap: 10px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 15px;
  flex: 1;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
}

.stat-card.positive .stat-value {
  color: var(--secondary-color);
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 15px;
  padding: 0 15px;
}

.gallery-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gallery-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.image-container {
  position: relative;
  height: 120px;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.posture-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  color: white;
}

.posture-badge.good {
  background-color: var(--secondary-color);
}

.posture-badge.bad {
  background-color: var(--danger-color);
}

.image-info {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-time {
  font-size: 0.8rem;
  color: #666;
}

.image-score {
  font-size: 0.9rem;
  font-weight: bold;
  color: var(--primary-color);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
}

.loading-container p {
  margin-top: 10px;
  color: #666;
}

.no-data {
  padding: 40px 0;
}

.load-more {
  text-align: center;
  margin-top: 20px;
}

/* 详情弹窗样式 */
.detail-popup {
  height: 80vh;
  overflow-y: auto;
}

.image-detail {
  padding: 20px;
}

.detail-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-right: 30px; /* 为关闭按钮留出空间 */
}

.detail-score {
  font-size: 1rem;
  padding: 2px 8px;
  border-radius: 15px;
  color: white;
}

.score-good {
  background-color: var(--secondary-color);
}

.score-medium {
  background-color: var(--warning-color);
}

.score-bad {
  background-color: var(--danger-color);
}

.detail-time {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 15px;
}

.detail-image-container {
  width: 100%;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.detail-image {
  width: 100%;
  display: block;
}

.detail-analysis h3,
.detail-suggestions h3,
.detail-environment h3 {
  font-size: 1.1rem;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.angle-data {
  margin-bottom: 20px;
}

.angle-item {
  margin-bottom: 10px;
}

.angle-label {
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.angle-value {
  font-weight: bold;
  margin-bottom: 5px;
}

.angle-bar {
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.angle-fill {
  height: 100%;
  border-radius: 4px;
}

.detail-suggestions ul {
  padding-left: 20px;
  margin-bottom: 20px;
}

.detail-suggestions li {
  margin-bottom: 8px;
}

.environment-data {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.env-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 8px;
}

@media (max-width: 480px) {
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .statistics-summary {
    flex-direction: column;
  }
}
</style>
