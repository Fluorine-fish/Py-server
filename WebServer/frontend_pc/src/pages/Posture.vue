<template>
  <div class="posture-container">
    <van-nav-bar title="坐姿检测" fixed />
    
    <div class="dashboard-title">孩子坐姿监测面板</div>
    
    <!-- 时间范围选择器 -->
    <div class="time-range-selector">
      <button 
        v-for="range in timeRanges" 
        :key="range.value" 
        :class="['time-range-btn', currentTimeRange === range.value ? 'active' : '']"
        @click="changeTimeRange(range.value)"
      >
        {{ range.label }}
      </button>
    </div>
    
    <!-- 提醒信息 -->
    <div class="alert alert-warning">
      <div class="alert-icon">⚠️</div>
      <div class="alert-content">
        <h3>坐姿改善建议</h3>
        <p>根据数据分析，您孩子在下午3-5点时段坐姿不良率较高，建议加强这个时段的监督或调整学习环境。</p>
      </div>
    </div>
    
    <!-- 数据仪表盘 -->
    <div class="dashboard">
      <!-- 坐姿时间占比卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">坐姿时间占比</div>
          <div class="card-icon">📊</div>
        </div>
        <div class="chart-container">
          <canvas id="posturePieChart"></canvas>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">3.2h</div>
            <div class="stat-label">良好坐姿</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">1.8h</div>
            <div class="stat-label">不良坐姿</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">64%</div>
            <div class="stat-label">良好率</div>
          </div>
        </div>
      </div>
      
      <!-- 坐姿评分趋势卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">坐姿评分趋势</div>
          <div class="card-icon">📈</div>
        </div>
        <div class="chart-container">
          <canvas id="scoreTrendChart"></canvas>
        </div>
        <div style="text-align: center; margin-top: 10px;">
          <span class="badge badge-success">本周提升 +12%</span>
        </div>
      </div>
      
      <!-- 不良坐姿时段分布卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">不良坐姿时段分布</div>
          <div class="card-icon">⏰</div>
        </div>
        <div class="chart-container">
          <canvas id="heatmapChart"></canvas>
        </div>
      </div>
      
      <!-- 提醒响应情况卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">提醒响应情况</div>
          <div class="card-icon">�</div>
        </div>
        <div class="chart-container">
          <canvas id="radarChart"></canvas>
        </div>
        <div style="text-align: center; margin-top: 10px;">
          <span class="badge badge-warning">响应率可提升</span>
        </div>
      </div>
      
      <!-- 脊柱健康风险评估卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">脊柱健康风险评估</div>
          <div class="card-icon">🏥</div>
        </div>
        <div class="chart-container">
          <canvas id="riskChart"></canvas>
        </div>
        <div style="text-align: center; margin-top: 10px;">
          <span class="badge badge-success">低风险</span>
        </div>
      </div>
      
      <!-- 坐姿图像记录卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">坐姿图像记录</div>
          <div class="card-icon">🧍‍♂️</div>
        </div>
        <div class="image-gallery">
          <div v-for="image in postureImages" :key="image.id" class="gallery-item" @click="viewPostureImage(image)">
            <img :src="image.image_path" :alt="image.posture_status" />
            <div class="time">{{ formatTime(image.timestamp) }}</div>
          </div>
        </div>
        <div style="text-align: center; margin-top: 15px;">
          <van-button plain size="small" @click="openPostureGallery">查看更多记录</van-button>
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="actions">
      <van-button type="primary" size="large" @click="generatePDF">
        <span>📄 导出周报</span>
      </van-button>
      <van-button plain type="primary" size="large" @click="openPostureGallery">
        <span>📷 查看更多记录</span>
      </van-button>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

export default {
  name: 'PosturePage',
  data() {
    return {
      currentTimeRange: 'day',
      timeRanges: [
        { label: '今日', value: 'day' },
        { label: '本周', value: 'week' },
        { label: '本月', value: 'month' }
      ],
      stats: {
        goodPostureHours: '3.2h',
        badPostureHours: '1.8h',
        goodRate: '64%'
      },
      postureImages: [
        {
          id: 1,
          image_path: 'https://placehold.co/150x120/4285f4/ffffff?text=良好坐姿',
          posture_status: '良好坐姿',
          timestamp: new Date().toISOString(),
          is_bad_posture: false
        },
        {
          id: 2,
          image_path: 'https://placehold.co/150x120/ea4335/ffffff?text=不良坐姿',
          posture_status: '不良坐姿',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          is_bad_posture: true
        },
        {
          id: 3,
          image_path: 'https://placehold.co/150x120/4285f4/ffffff?text=良好坐姿',
          posture_status: '良好坐姿',
          timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
          is_bad_posture: false
        },
        {
          id: 4,
          image_path: 'https://placehold.co/150x120/fbbc05/ffffff?text=需改进',
          posture_status: '需改进坐姿',
          timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
          is_bad_posture: true
        }
      ],
      charts: {
        posturePie: null,
        scoreTrend: null,
        heatmap: null,
        radar: null,
        risk: null
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      setTimeout(() => {
        this.initCharts();
        this.loadPostureData();
      }, 300);
    });
    
    // 设置定时刷新
    this.refreshInterval = setInterval(() => {
      this.loadPostureData();
    }, 60000); // 每分钟更新一次
    
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', this.resizeCharts);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    window.removeEventListener('resize', this.resizeCharts);
  },
  methods: {
    initCharts() {
      try {
        // 初始化坐姿饼图
        const pieCtx = document.getElementById('posturePieChart').getContext('2d');
        this.charts.posturePie = new Chart(pieCtx, {
          type: 'doughnut',
          data: {
            labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'],
            datasets: [{
              data: [64, 18, 12, 6],
              backgroundColor: [
                '#34a853',
                '#fbbc05',
                '#ff9800',
                '#ea4335'
              ],
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            cutout: '70%',
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  padding: 20,
                  usePointStyle: true,
                  pointStyle: 'circle'
                }
              },
              tooltip: {
                callbacks: {
                label: function (context) {
                  return `${context.label}: ${context.raw}%`;
                }
              }
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
      
      // 初始化坐姿评分趋势图
      const trendCtx = document.getElementById('scoreTrendChart').getContext('2d');
      this.charts.scoreTrend = new Chart(trendCtx, {
        type: 'line',
        data: {
          labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
          datasets: [{
            label: '坐姿评分',
            data: [72, 68, 75, 80, 78, 82, 85],
            borderColor: '#4285f4',
            backgroundColor: 'rgba(66, 133, 244, 0.1)',
            borderWidth: 3,
            tension: 0.3,
            fill: true,
            pointBackgroundColor: '#4285f4',
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: false,
              min: 60,
              max: 100,
              ticks: {
                callback: function (value) {
                  return value + '分';
                }
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `评分: ${context.raw}分`;
                }
              }
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
      
      // 初始化不良坐姿时段分布图
      const heatmapCtx = document.getElementById('heatmapChart').getContext('2d');
      this.charts.heatmap = new Chart(heatmapCtx, {
        type: 'bar',
        data: {
          labels: ['8-10', '10-12', '12-14', '14-16', '16-18', '18-20'],
          datasets: [{
            label: '不良坐姿次数',
            data: [5, 3, 2, 8, 6, 4],
            backgroundColor: function (context) {
              const value = context.dataset.data[context.dataIndex];
              if (value >= 7) return '#ea4335';
              if (value >= 5) return '#ff9800';
              if (value >= 3) return '#fbbc05';
              return '#34a853';
            },
            borderWidth: 0,
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: '不良次数'
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
      
      // 初始化雷达图
      const radarCtx = document.getElementById('radarChart').getContext('2d');
      this.charts.radar = new Chart(radarCtx, {
        type: 'radar',
        data: {
          labels: ['即时纠正率', '提醒响应速度', '持续坐姿时间', '重复提醒次数', '自主调整率'],
          datasets: [{
            label: '本周',
            data: [75, 60, 65, 40, 55],
            backgroundColor: 'rgba(66, 133, 244, 0.2)',
            borderColor: '#4285f4',
            borderWidth: 2,
            pointBackgroundColor: '#4285f4',
            pointRadius: 4
          }, {
            label: '上周',
            data: [65, 50, 55, 60, 45],
            backgroundColor: 'rgba(234, 67, 53, 0.2)',
            borderColor: '#ea4335',
            borderWidth: 2,
            pointBackgroundColor: '#ea4335',
            pointRadius: 4,
            borderDash: [5, 5]
          }]
        },
        options: {
          scales: {
            r: {
              angleLines: {
                display: true
              },
              suggestedMin: 0,
              suggestedMax: 100,
              ticks: {
                stepSize: 20
              }
            }
          },
          plugins: {
            legend: {
              position: 'bottom'
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
      
      // 脊柱健康风险图
      const riskCtx = document.getElementById('riskChart').getContext('2d');
      this.charts.risk = new Chart(riskCtx, {
        type: 'bar',
        data: {
          labels: ['颈椎风险', '腰椎风险', '胸椎风险', '整体风险'],
          datasets: [{
            label: '风险指数',
            data: [32, 28, 25, 30],
            backgroundColor: [
              'rgba(66, 133, 244, 0.7)',
              'rgba(52, 168, 83, 0.7)',
              'rgba(251, 188, 5, 0.7)',
              'rgba(234, 67, 53, 0.7)'
            ],
            borderColor: [
              '#4285f4',
              '#34a853',
              '#fbbc05',
              '#ea4335'
            ],
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function (value) {
                  return value + '%';
                }
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `风险指数: ${context.raw}%`;
                }
              }
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
      } catch (error) {
        console.error('图表初始化错误:', error);
        // 如果图表初始化失败，可以显示错误信息或使用备用方案
      }
    },
    
    resizeCharts() {
      for (const key in this.charts) {
        if (this.charts[key]) {
          this.charts[key].resize();
        }
      }
    },
    changeTimeRange(range) {
      this.currentTimeRange = range;
      this.loadPostureData();
      
      // 更新图表数据显示
      this.animateCharts();
    },
    loadPostureData() {
      // 此处应调用API获取数据，这里模拟数据
      console.log(`加载${this.currentTimeRange}时间范围的坐姿数据`);
      
      // 根据选择的时间范围更新统计数据
      if (this.currentTimeRange === 'week') {
        this.updateChartData({
          goodPostureHours: '22.5h',
          badPostureHours: '12.3h',
          goodRate: '65%'
        });
      } else if (this.currentTimeRange === 'month') {
        this.updateChartData({
          goodPostureHours: '89.6h',
          badPostureHours: '42.8h',
          goodRate: '67%'
        });
      } else {
        // 今日数据
        this.updateChartData({
          goodPostureHours: '3.2h',
          badPostureHours: '1.8h',
          goodRate: '64%'
        });
      }
    },
    updateChartData(stats) {
      try {
        this.stats = stats;
        
        // 更新饼图数据 - 实际应用中需要从API获取详细数据
        // 这里简单模拟一下数据变化
        if (this.charts.posturePie) {
          // 保持总和为100%
          const goodRate = parseInt(stats.goodRate);
          const badRateTotal = 100 - goodRate;
          const badRateDistribution = [
            Math.round(badRateTotal * 0.5), // 轻度不良
            Math.round(badRateTotal * 0.3), // 中度不良
            badRateTotal - Math.round(badRateTotal * 0.5) - Math.round(badRateTotal * 0.3) // 严重不良
          ];
          
          this.charts.posturePie.data.datasets[0].data = [
            goodRate,
            badRateDistribution[0],
            badRateDistribution[1],
            badRateDistribution[2]
          ];
          this.charts.posturePie.update();
        }
      } catch (error) {
        console.error('更新图表数据时出错:', error);
      }
    },
    animateCharts() {
      try {
        // 为图表添加动画效果，使数据更新更加生动
        for (const key in this.charts) {
          if (this.charts[key] && typeof this.charts[key].update === 'function') {
            this.charts[key].update('normal');
          }
        }
      } catch (error) {
        console.error('图表动画更新时出错:', error);
      }
    },
    viewPostureImage(image) {
      // 在实际应用中，这里可以打开一个模态框显示大图
      alert(`查看坐姿图像: ${image.posture_status}, 时间: ${this.formatTime(image.timestamp)}`);
    },
    generatePDF() {
      alert('正在生成坐姿监测周报...');
      // 此处实现PDF生成逻辑，可以参考提供的HTML模板中的generatePDF函数
    },
    openPostureGallery() {
      this.$router.push('/posture/gallery');
    },
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
    }
  }
}
</script>

<style scoped>
:root {
  --primary-color: #4285f4;
  --secondary-color: #34a853;
  --warning-color: #fbbc05;
  --danger-color: #ea4335;
  --light-gray: #f5f5f5;
  --dark-gray: #333;
  --text-color: #444;
}

.posture-container {
  padding-top: 46px; /* 为固定的NavBar留出空间 */
  background-color: #f9f9f9;
  min-height: 100vh;
}

.dashboard-title {
  font-size: 32px;
  font-weight: bold;
  margin-top: 15px;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.time-range-selector {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.time-range-btn {
  padding: 8px 16px;
  margin: 0 5px;
  border: none;
  background-color: var(--light-gray);
  color: var(--text-color);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.time-range-btn.active {
  background-color: var(--primary-color);
  color: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.alert {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.alert-warning {
  background-color: rgba(251, 188, 5, 0.2);
  border-left: 4px solid var(--warning-color);
}

.alert-icon {
  margin-right: 10px;
  font-size: 1.5rem;
  color: var(--warning-color);
}

.alert-content h3 {
  margin-bottom: 5px;
  color: var(--dark-gray);
}

.alert-content p {
  font-size: 0.9rem;
  color: var(--text-color);
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--dark-gray);
}

.card-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--light-gray);
  border-radius: 50%;
  color: var(--primary-color);
  font-size: 1rem;
}

.chart-container {
  position: relative;
  height: 250px;
  width: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: var(--light-gray);
  border-radius: 8px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge-success {
  background-color: rgba(52, 168, 83, 0.2);
  color: var(--secondary-color);
}

.badge-warning {
  background-color: rgba(251, 188, 5, 0.2);
  color: var(--warning-color);
}

.badge-danger {
  background-color: rgba(234, 67, 53, 0.2);
  color: var(--danger-color);
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.gallery-item {
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.gallery-item img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.gallery-item .time {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 5px;
  font-size: 0.7rem;
  text-align: center;
}

.actions {
  display: flex;
  justify-content: center;
  margin: 30px 0;
  gap: 15px;
}

@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
