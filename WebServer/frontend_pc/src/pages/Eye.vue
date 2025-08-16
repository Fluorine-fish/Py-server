<template>
  <div class="eye-page">
    <h1>用眼健康</h1>
    
    <div class="row">
      <div class="card col-md-6">
        <div class="card-header">
          <div class="card-title">眨眼频率</div>
          <div class="card-icon">👁️</div>
        </div>
        <div class="chart-container">
          <canvas id="blinkRateChart"></canvas>
        </div>
      </div>
      
      <div class="card col-md-6">
        <div class="card-header">
          <div class="card-title">用眼距离分布</div>
          <div class="card-icon">📏</div>
        </div>
        <div class="chart-container">
          <canvas id="eyeDistanceChart"></canvas>
        </div>
      </div>
    </div>
    
    <div class="row">
      <div class="card col-md-6">
        <div class="card-header">
          <div class="card-title">近视风险评估</div>
          <div class="card-icon">🔍</div>
        </div>
        <div class="chart-container" style="display: flex; flex-direction: column;">
          <div style="flex: 1; display: flex; align-items: flex-start; padding-left: 15px;">
            <div style="width: 45%; padding: 20px 0;">
              <div style="text-align: left;">
                <div class="risk-meter-label" style="margin-bottom: 8px;">风险指数</div>
                <div class="risk-meter-value" style="font-size: 2.5rem; font-weight: bold; color: #3488ff; margin-bottom: 8px;">35%</div>
                <div class="risk-meter-bar" style="margin: 10px 0; height: 10px; background-color: #e9ecef; border-radius: 5px; width: 90%;">
                  <div class="risk-meter-fill" style="height: 100%; width: 35%; background: linear-gradient(90deg, #5cb85c, #f0ad4e, #d9534f); border-radius: 5px;"></div>
                </div>
                <div class="risk-meter-labels" style="display: flex; justify-content: space-between; width: 90%;">
                  <span style="color: #5cb85c;">低风险</span>
                  <span style="color: #f0ad4e;">中风险</span>
                  <span style="color: #d9534f;">高风险</span>
                </div>
              </div>
            </div>
            <div style="width: 55%; padding: 20px;">
              <div class="risk-factors">
                <h4>风险因素分析</h4>
                <ul style="padding-left: 20px; list-style-type: none;">
                  <li><span class="factor-label">用眼时长:</span> <span class="factor-value good">2.5小时/天</span></li>
                  <li><span class="factor-label">户外活动:</span> <span class="factor-value warning">0.8小时/天</span></li>
                  <li><span class="factor-label">用眼距离:</span> <span class="factor-value good">33厘米</span></li>
                  <li><span class="factor-label">光照条件:</span> <span class="factor-value good">良好</span></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card col-md-6">
        <div class="card-header">
          <div class="card-title">休息提醒执行情况</div>
          <div class="card-icon">⏰</div>
        </div>
        <div class="chart-container">
          <canvas id="restReminderChart"></canvas>
        </div>
      </div>
    </div>
    
    <div class="row">
      <div class="card col-md-12">
        <div class="card-header">
          <div class="card-title">近视风险详细分析</div>
          <div class="card-icon">🔍</div>
        </div>
        <div class="risk-assessment">
          <div class="risk-factors" style="display: flex; flex-wrap: wrap; justify-content: space-between; padding: 15px;">
            <div style="width: 48%;">
              <h4>风险因素详情</h4>
              <ul>
                <li><span class="factor-label">用眼时长:</span> <span class="factor-value good">2.5小时/天</span> <span class="factor-comment">低于3小时/天标准，良好</span></li>
                <li><span class="factor-label">户外活动:</span> <span class="factor-value warning">0.8小时/天</span> <span class="factor-comment">低于推荐的2小时/天，建议增加</span></li>
                <li><span class="factor-label">日常距离变化:</span> <span class="factor-value good">稳定</span> <span class="factor-comment">距离波动较小，良好习惯</span></li>
              </ul>
            </div>
            <div style="width: 48%;">
              <h4>保护建议</h4>
              <ul>
                <li><span class="factor-comment">● 每30分钟休息5分钟，放松眼部肌肉</span></li>
                <li><span class="factor-comment">● 每天保证2小时户外活动时间</span></li>
                <li><span class="factor-comment">● 维持良好的读写姿势，保持30-40cm的用眼距离</span></li>
                <li><span class="factor-comment">● 在充足自然光下学习和阅读</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <van-button type="primary" size="large" @click="generateEyeReport">生成用眼健康报告</van-button>
      <van-button plain type="primary" size="large" @click="viewDetailedData">查看详细数据</van-button>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'EyePage',
  data() {
    return {
      charts: {}
    }
  },
  mounted() {
  this.initCharts();
  // 接入真实数据：加载用眼趋势并更新图表
  this.loadEyeTrends();
  },
  methods: {
    initCharts() {
      // 眨眼频率图表
      const blinkRateCtx = document.getElementById('blinkRateChart').getContext('2d');
      this.charts.blinkRate = new Chart(blinkRateCtx, {
        type: 'line',
        data: {
          labels: ['9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
          datasets: [{
            label: '每分钟眨眼次数',
            data: [15, 12, 14, 10, 16, 18, 15],
            fill: false,
            borderColor: 'rgba(75, 192, 192, 1)',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              suggestedMax: 25
            }
          },
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
      
      // 用眼距离分布图表
      const eyeDistanceCtx = document.getElementById('eyeDistanceChart').getContext('2d');
      this.charts.eyeDistance = new Chart(eyeDistanceCtx, {
        type: 'bar',
        data: {
          labels: ['<20cm', '20-30cm', '30-40cm', '40-50cm', '>50cm'],
          datasets: [{
            label: '时长占比',
            data: [5, 20, 45, 25, 5],
            backgroundColor: [
              'rgba(234, 67, 53, 0.6)',
              'rgba(251, 188, 5, 0.6)',
              'rgba(52, 168, 83, 0.6)',
              'rgba(66, 133, 244, 0.6)',
              'rgba(128, 128, 128, 0.6)'
            ],
            borderColor: [
              'rgba(234, 67, 53, 1)',
              'rgba(251, 188, 5, 1)',
              'rgba(52, 168, 83, 1)',
              'rgba(66, 133, 244, 1)',
              'rgba(128, 128, 128, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
      
      // 休息提醒执行情况图表
      const restReminderCtx = document.getElementById('restReminderChart').getContext('2d');
      this.charts.restReminder = new Chart(restReminderCtx, {
        type: 'bar',
        data: {
          labels: ['准时休息', '延迟休息', '忽略提醒'],
          datasets: [{
            label: '次数',
            data: [12, 5, 3],
            backgroundColor: [
              'rgba(52, 168, 83, 0.6)',
              'rgba(251, 188, 5, 0.6)',
              'rgba(234, 67, 53, 0.6)'
            ],
            borderColor: [
              'rgba(52, 168, 83, 1)',
              'rgba(251, 188, 5, 1)',
              'rgba(234, 67, 53, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    },

    // 从后端获取真实趋势数据并更新图表
    async loadEyeTrends() {
      try {
        const res = await fetch('/api/monitor/eye/trends');
        if (!res.ok) throw new Error('接口返回非 200');
        const json = await res.json();
        const { labels = [], datasets = [] } = json || {};

        // 更新眨眼频率折线图
        const blinkDataset = datasets.find(d => d.label === '眨眼频率') || datasets[0] || { data: [] };
        if (this.charts.blinkRate) {
          this.charts.blinkRate.data.labels = labels;
          this.charts.blinkRate.data.datasets[0].data = blinkDataset.data || [];
          this.charts.blinkRate.update();
        }

        // 由“用眼距离”趋势数据进行分布统计（单位：厘米）
        const distanceDataset = datasets.find(d => d.label && d.label.includes('用眼距离')) || datasets[1];
        const values = Array.isArray(distanceDataset?.data) ? distanceDataset.data : [];
        const bins = ['<20cm', '20-30cm', '30-40cm', '40-50cm', '>50cm'];
        const counts = [0, 0, 0, 0, 0];
        values.forEach(v => {
          const val = Number(v);
          if (isNaN(val)) return;
          if (val < 20) counts[0]++;
          else if (val < 30) counts[1]++;
          else if (val < 40) counts[2]++;
          else if (val < 50) counts[3]++;
          else counts[4]++;
        });
        const total = counts.reduce((a, b) => a + b, 0) || 1;
        const percents = counts.map(c => Math.round((c / total) * 100));
        if (this.charts.eyeDistance) {
          this.charts.eyeDistance.data.labels = bins;
          this.charts.eyeDistance.data.datasets[0].data = percents;
          this.charts.eyeDistance.update();
        }
      } catch (err) {
        console.warn('加载用眼趋势失败，使用占位数据:', err);
      }
    },
    
    generateEyeReport() {
      this.$toast('正在生成报告...');
      setTimeout(() => {
        this.$router.push('/report/eye');
      }, 1500);
    },
    
    viewDetailedData() {
      this.$router.push('/eye/detailed');
    }
  }
}
</script>

<style scoped>
.eye-page {
  padding: 20px;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 25px;
  color: var(--primary-text-color);
}

.row {
  display: flex;
  margin: 0 -15px 30px;
  flex-wrap: wrap;
}

.card {
  background-color: var(--card-bg-color);
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin: 0 15px 20px;
  overflow: hidden;
  position: relative;
  flex: 1;
  min-width: calc(50% - 30px);
}

.card.col-md-12 {
  min-width: calc(100% - 30px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
}

.card-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--primary-text-color);
}

.card-icon {
  font-size: 1.5rem;
  opacity: 0.8;
}

.chart-container {
  height: 300px;
  padding: 15px;
}

.risk-assessment {
  padding: 15px;
}

.risk-meter-container {
  padding: 15px;
}

.risk-meter {
  width: 100%;
}

.risk-meter-bar {
  width: 100%;
  height: 10px;
  background-color: var(--border-color);
  border-radius: 5px;
  margin: 10px 0;
  overflow: hidden;
}

.risk-meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #5cb85c, #f0ad4e, #d9534f);
  border-radius: 5px;
}

.risk-meter-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--secondary-text-color);
}

.risk-factors ul {
  padding-left: 0;
  list-style-type: none;
}

.risk-factors li {
  margin-bottom: 15px;
  display: flex;
  flex-wrap: wrap;
}

.factor-label {
  font-weight: 500;
  margin-right: 10px;
  min-width: 100px;
}

.factor-value.good {
  color: var(--secondary-color);
}

.factor-value.warning {
  color: var(--warning-color);
}

.factor-value.danger {
  color: var(--danger-color);
}

.factor-comment {
  font-size: 0.9rem;
  opacity: 0.8;
  flex: 1;
}

.actions {
  display: flex;
  justify-content: center;
  margin: 30px 0;
  gap: 15px;
}
</style>
