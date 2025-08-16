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
            <div class="stat-value">{{ stats.goodPostureHours }}</div>
            <div class="stat-label">良好坐姿</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.badPostureHours }}</div>
            <div class="stat-label">不良坐姿</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.goodRate }}</div>
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
          <div class="card-icon">🔔</div>
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
import { markRaw } from 'vue';

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
      pieLegend: {
        labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'],
        percents: [100, 0, 0, 0]
      },
  postureImages: [],
      charts: {
        // 用 markRaw 包裹 Chart 实例，避免被 Vue 的响应式代理
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
  this.loadLatestImages();
      }, 300);
    });
    
    // 设置定时刷新
    this.refreshInterval = setInterval(() => {
      this.loadPostureData();
    }, 60000); // 每分钟更新一次
    
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', this.resizeCharts);
    // 页面可见性改变时，返回可见仅做一次轻量刷新
    this._onVisibilityChange = () => { 
      if (!document.hidden) {
        this.resizeCharts();
        // 仅更新一次饼图数据，避免递归
        this.loadPostureDistribution();
      }
    };
    document.addEventListener('visibilitychange', this._onVisibilityChange);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    window.removeEventListener('resize', this.resizeCharts);
    document.removeEventListener('visibilitychange', this._onVisibilityChange);
  },
  methods: {
    // 生成绝对 API URL，确保以站点根为基准，避免相对路径受 /pc/ 影响
    _apiUrl(path, params) {
      const url = new URL(path, window.location.origin);
      if (params && typeof params === 'object') {
        Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
      }
      return url.toString();
    },
    // 去除强制重建，避免在插件生命周期内递归触发更新
    forceReinitializeCharts() {
      // 保留空实现用于兼容旧调用
      this.resizeCharts();
    },
    
    // 刷新所有图表一次
    refreshChartsOnce() {
      try {
        // 先尝试更新，再在可见时 resize，避免把图表调整到 0 宽度
        for (const key in this.charts) {
          const chart = this.charts[key];
          if (!chart || typeof chart.update !== 'function') continue;
          try { chart.update(); } catch (_) {}
        }
        this.resizeCharts();
      } catch (e) { console.warn('refreshChartsOnce warn:', e); }
    },
    // 在短时间内刷新N次，提高初次可见时的稳定性
    refreshChartsNTimes() {
      // 已废弃，避免递归刷新导致堆栈溢出
    },
  async loadLatestImages(){
      try{
    const res = await fetch(this._apiUrl('/api/monitor/posture/images', { page: 1, limit: 4 }));
        const json = await res.json();
        // 兼容两种返回格式：{data: [...]} 或直接数组
        const arr = Array.isArray(json) ? json : (json.data || []);
        this.postureImages = arr.map(it=>({
          id: it.id,
          image_path: it.thumbnail || it.url,
          posture_status: it.posture_type || (it.is_good_posture===false? '不良坐姿':'坐姿记录'),
          timestamp: it.timestamp || new Date().toISOString(),
          is_bad_posture: it.is_good_posture===false
        }));
      }catch(e){
        console.error('加载坐姿图像失败: ', e);
      }
    },
    initCharts() {
      if (this._chartsInitInProgress) {
        console.log('图表初始化进行中，跳过');
        return;
      }
      this._chartsInitInProgress = true;
      try {
        console.log('开始初始化坐姿页面图表...');
        
        // 初始化坐姿饼图（等待容器尺寸可用再创建）
        const el = document.getElementById('posturePieChart');
        const tryInitPie = (retries = 15) => {
          const node = document.getElementById('posturePieChart');
          if (!node) { 
            console.warn(`饼图容器未找到，剩余重试次数: ${retries}`);
            if (retries > 0) return setTimeout(() => tryInitPie(retries-1), 100); 
            console.error('坐姿饼图容器未找到，初始化失败');
            return; 
          }
          const parent = node.parentElement;
          const rect = parent && parent.getBoundingClientRect ? parent.getBoundingClientRect() : { width: 0, height: 0 };
          if (rect.width <= 10 || rect.height <= 10) {
            console.warn(`饼图容器尺寸异常: ${rect.width}x${rect.height}，剩余重试次数: ${retries}`);
            if (retries > 0) return setTimeout(() => tryInitPie(retries-1), 100);
            console.warn('坐姿饼图容器尺寸异常，但继续创建:', rect);
          }
          if (this.charts.posturePie) {
            console.log('坐姿饼图已存在，跳过重复创建');
            return; // 已创建
          }
          
          try {
            const pieCtx = node.getContext('2d');
            // 将 Chart 实例标记为非响应式，避免深层 Proxy 递归
            this.charts.posturePie = markRaw(new Chart(pieCtx, {
              // 与 main.html 保持一致，使用圆环图
              type: 'doughnut',
              data: {
                labels: ['良好坐姿', '轻度不良', '中度不良', '严重不良'],
                datasets: [{
                  // 初始占位：全部为良好，避免全0导致不可见
                  data: [100, 0, 0, 0],
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
                maintainAspectRatio: false,
                resizeDelay: 200,
                cutout: '70%',
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: { 
                      padding: 20, 
                      usePointStyle: true, 
                      pointStyle: 'circle',
                      font: { size: 12 }
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
                layout: { padding: 10 }
              }
            }));
            
            console.log('坐姿饼图初始化成功');
            
            // 当图表进入可视区时再次更新，避免初始不可见导致的空白
            try {
              const obs = new IntersectionObserver((entries) => {
                entries.forEach(e => {
                  if (e.isIntersecting && this.charts.posturePie) {
                    try { 
                      this.charts.posturePie.resize(); 
                      this.charts.posturePie.update(); 
                      console.log('坐姿饼图进入可视区域，已更新');
                    } catch(_) {}
                  }
                });
              }, { root: null, threshold: 0.1 });
              obs.observe(node);
            } catch(_) {}
            
            // 初始化后拉取一次后端数据以填充饼图与统计
            setTimeout(() => this.loadPostureDistribution(), 200);
            
          } catch (error) {
            console.error('创建坐姿饼图时出错:', error);
            if (retries > 0) {
              setTimeout(() => tryInitPie(retries-1), 200);
            }
          }
        };
        
        if (el) {
          tryInitPie();
        } else {
          setTimeout(() => tryInitPie(), 200);
        }
      
      // 初始化坐姿评分趋势图（若已存在则跳过）
      if (!this.charts.scoreTrend) {
        const trendCanvas = document.getElementById('scoreTrendChart');
        if (trendCanvas) {
          const trendCtx = trendCanvas.getContext('2d');
          this.charts.scoreTrend = markRaw(new Chart(trendCtx, {
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
          }));
        }
      }
      
      // 初始化不良坐姿时段分布图（若已存在则跳过）
      if (!this.charts.heatmap) {
        const heatCanvas = document.getElementById('heatmapChart');
        if (heatCanvas) {
          const heatmapCtx = heatCanvas.getContext('2d');
          this.charts.heatmap = markRaw(new Chart(heatmapCtx, {
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
          }));
        }
      }
      
      // 初始化雷达图（若已存在则跳过）
      if (!this.charts.radar) {
        const radarCanvas = document.getElementById('radarChart');
        if (radarCanvas) {
          const radarCtx = radarCanvas.getContext('2d');
          this.charts.radar = markRaw(new Chart(radarCtx, {
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
          }));
        }
      }
      
      // 脊柱健康风险图（若已存在则跳过）
      if (!this.charts.risk) {
        const riskCanvas = document.getElementById('riskChart');
        if (riskCanvas) {
          const riskCtx = riskCanvas.getContext('2d');
          this.charts.risk = markRaw(new Chart(riskCtx, {
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
          }));
        }
      }
      this._chartsInitInProgress = false;
      } catch (error) {
        console.error('图表初始化错误:', error);
        // 如果图表初始化失败，可以显示错误信息或使用备用方案
        this._chartsInitInProgress = false;
      }
    },
    
    resizeCharts() {
      const delayed = [];
      for (const key in this.charts) {
        const chart = this.charts[key];
        if (!chart) continue;
        const canvas = chart.canvas;
        const parent = canvas && canvas.parentNode;
        if (!parent || typeof parent.getBoundingClientRect !== 'function') continue;
        const rect = parent.getBoundingClientRect();
        if (rect.width > 10 && rect.height > 10) {
          try { chart.resize(); } catch(_) {}
        } else {
          delayed.push(chart);
        }
      }
      if (delayed.length) {
        // 容器还未完成布局，稍后再尝试一次
        setTimeout(() => {
          delayed.forEach(c => { try { c.resize(); c.update(); } catch(_) {} });
        }, 200);
      }
    },
    changeTimeRange(range) {
      this.currentTimeRange = range;
      // 饼图走后端，其它图表使用假数据更新
      this.loadPostureDistribution();
      this.updateMockCharts();
    },
    loadPostureData() {
      // 饼图走后端，其他图表保留模拟
      this.loadPostureDistribution();
      this.updateMockCharts();
    },
    // 其他四个图表使用假数据（按时间范围生成不同维度数据）
    updateMockCharts(){
      // 评分趋势
      const ranges = {
        day: { labels: Array.from({length: 12}, (_,i)=>`${8+i}:00`), min: 65, max: 90 },
        week: { labels: ['周一','周二','周三','周四','周五','周六','周日'], min: 65, max: 90 },
        month: { labels: ['第1周','第2周','第3周','第4周'], min: 60, max: 92 }
      };
      const r = ranges[this.currentTimeRange] || ranges.week;
      const rand = (a,b)=>Math.round(a + Math.random()*(b-a));
      const smooth = (arr)=>arr.map((v,i)=>{
        if (i===0||i===arr.length-1) return v;
        return Math.round((arr[i-1]+v+arr[i+1])/3);
      });
      const trendData = smooth(Array.from({length: r.labels.length}, ()=>rand(r.min, r.max)));
      if (this.charts.scoreTrend){
        this.charts.scoreTrend.data.labels = r.labels;
        this.charts.scoreTrend.data.datasets[0].data = trendData;
          this.charts.scoreTrend.update();
      }

      // 不良坐姿时段分布（柱状）
      const slotLabels = this.currentTimeRange === 'day' 
        ? ['8-10','10-12','12-14','14-16','16-18','18-20']
        : ['上午','中午','下午','傍晚','晚上'];
      const slotCounts = slotLabels.map(()=>rand(0, 9));
      if (this.charts.heatmap){
        this.charts.heatmap.data.labels = slotLabels;
        this.charts.heatmap.data.datasets[0].data = slotCounts;
  this.charts.heatmap.update();
      }

      // 雷达图（本周/上周）
      const mkRadar = ()=>[rand(40,85),rand(40,85),rand(40,85),rand(30,70),rand(35,80)];
      if (this.charts.radar){
        this.charts.radar.data.datasets[0].data = mkRadar();
        this.charts.radar.data.datasets[1].data = mkRadar();
  this.charts.radar.update();
      }

      // 脊柱健康风险
      if (this.charts.risk){
        this.charts.risk.data.datasets[0].data = [rand(20,40), rand(18,36), rand(15,35), rand(18,38)];
  this.charts.risk.update();
      }
    },
    async loadPostureDistribution() {
    // 统一的处理函数：从 FastAPI distribution 组装绘图数据
      const handleAndRender = (payload) => {
  // payload 来自 FastAPI 接口
        let labels = ['良好坐姿','轻度不良','中度不良','严重不良'];
        let goodS = 0, mildS = 0, moderateS = 0, severeS = 0;
        let percents = [0,0,0,0];

        if (payload && Array.isArray(payload.rawSeconds)) {
          // FastAPI /api/monitor/posture/distribution
          labels = Array.isArray(payload.labels) ? payload.labels.map(l => {
            // 文案统一
            if (l.includes('良好')) return '良好坐姿';
            if (l.includes('轻')) return '轻度不良';
            if (l.includes('中')) return '中度不良';
            if (l.includes('重')) return '严重不良';
            return l;
          }) : labels;
          const raw = payload.rawSeconds.map(v => Number(v) || 0);
          [goodS, mildS, moderateS, severeS] = raw;
          percents = Array.isArray(payload.data) ? payload.data.map(v => Number(v) || 0) : [0,0,0,0];
  }

        const secondsTotal = goodS + mildS + moderateS + severeS;
        // 若百分比不可用，用原始秒数计算
        const sumPerc = percents.reduce((a,b)=>a+b, 0);
        if (percents.length !== 4 || sumPerc <= 0) {
          if (secondsTotal > 0) {
            const tmp = [goodS, mildS, moderateS, severeS];
            percents = tmp.map(v => parseFloat(((v*100)/secondsTotal).toFixed(1)));
          } else {
            percents = [100,0,0,0];
          }
        }
        // 归一化
        const totalPerc = percents.reduce((a,b)=>a+b, 0);
        if (totalPerc > 0 && Math.abs(totalPerc - 100) > 0.5) {
          percents = percents.map(v => parseFloat((v * 100 / totalPerc).toFixed(1)));
        }
        // 占位与可视优化
        const badS = mildS + moderateS + severeS;
        if ((goodS + badS) === 0 || (percents.reduce((a,b)=>a+b,0) === 0)) {
          percents = [100,0,0,0];
        }
        // 更新统计卡片
        const fmtH = (sec) => `${(sec/3600).toFixed(1)}h`;
        this.updateChartData({
          goodPostureHours: fmtH(goodS),
          badPostureHours: fmtH(badS),
          goodRate: `${(percents[0] || 0)}%`
        });
        // 更新 legend
        this.pieLegend.labels = labels;
        this.pieLegend.percents = percents.map(v => typeof v === 'number' ? Number(v.toFixed(1)) : Number(v) || 0);
        // 更新图表
        if (this.charts.posturePie) {
          this.charts.posturePie.data.labels = labels;
          this.charts.posturePie.data.datasets[0].data = percents;
          try { this.charts.posturePie.update(); } catch (_) {}
        }
      };

      try {
  const url = this._apiUrl('/api/monitor/posture/distribution', { timeRange: this.currentTimeRange });
        const res = await fetch(url);
        if (!res.ok) throw new Error(`distribution HTTP ${res.status}`);
        const data = await res.json();
        handleAndRender(data);
      } catch (err) {
  console.error('加载坐姿时间占比失败：', err);
      }
    },
    updateChartData(stats) {
      try {
        this.stats = stats;
        
        // 饼图数据已由 loadPostureDistribution 进行更新
      } catch (error) {
        console.error('更新图表数据时出错:', error);
      }
    },
  // 移除统一动画强制更新，避免潜在递归更新
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
  min-height: 250px;
  overflow: hidden;
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
  max-width: 100%;
  max-height: 100%;
}

/* 确保饼图容器有足够的空间 */
.card .chart-container {
  margin: 10px 0;
  padding: 10px;
}

/* 自定义图例样式 */
.legend-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 16px;
  margin-top: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: var(--text-color);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.legend-dot.good { background-color: #34a853; }
.legend-dot.mild { background-color: #fbbc05; }
.legend-dot.moderate { background-color: #ff9800; }
.legend-dot.severe { background-color: #ea4335; }

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
