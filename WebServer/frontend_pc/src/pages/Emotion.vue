<template>
  <div class="emotion-container">
    <h1>情绪识别</h1>
    
    <div class="dashboard-title">孩子情绪动态反馈面板</div>
    
    <div class="alert-box">
      <div class="alert-icon">
        <span>⚠️</span>
      </div>
      <div class="alert-content">
        <h3 class="alert-title">情绪提醒</h3>
        <p class="alert-message">孩子今天出现了3次明显的焦虑情绪，建议关注并沟通了解原因</p>
      </div>
    </div>
    
    <div class="emotion-dashboard">
      <!-- 每日情绪趋势卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">每日情绪趋势</div>
          <div class="card-icon">
            <span>📊</span>
          </div>
        </div>
        <div class="chart-container">
          <div id="dailyEmotionChart" class="chart-inner"></div>
          <div class="chart-loading" v-if="!chartsReady">正在加载图表...</div>
        </div>
      </div>
      
      <!-- 情绪分布卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">情绪分布</div>
          <div class="card-icon">
            <span>🍩</span>
          </div>
        </div>
        <div class="chart-container">
          <div id="emotionDistributionChart" class="chart-inner"></div>
          <div class="chart-loading" v-if="!chartsReady">正在加载图表...</div>
        </div>
      </div>
      
      <!-- 异常情绪记录卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">异常情绪记录</div>
          <div class="card-icon">
            <span>📝</span>
          </div>
        </div>
        <div class="emotion-records">
          <div class="emotion-record" v-for="(record, index) in abnormalEmotions" :key="index">
            <div class="emotion-record-header">
              <div class="emotion-type" :class="record.type">{{ record.emotion }}</div>
              <div class="emotion-time">{{ record.time }}</div>
            </div>
            <div class="emotion-details">
              <div class="emotion-context">{{ record.context }}</div>
              <div class="emotion-duration">持续时间: {{ record.duration }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 情绪影响因素卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">情绪影响因素</div>
          <div class="card-icon">
            <span>🔍</span>
          </div>
        </div>
        <div class="chart-container">
          <div id="emotionFactorsChart" class="chart-inner"></div>
          <div class="chart-loading" v-if="!chartsReady">正在加载图表...</div>
        </div>
      </div>
    </div>
    
    <div class="bottom-actions">
      <button class="blue-btn" @click="generateEmotionReport">
        <span>📄 生成情绪分析报告</span>
      </button>
      <button class="white-btn" @click="viewEmotionHistory">
        <span>⏱️ 查看历史记录</span>
      </button>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'EmotionPage',
  data() {
    return {
      charts: {},
      chartsReady: false,
      abnormalEmotions: [
        {
          emotion: '焦虑',
          type: 'warning',
          time: '今天 10:25',
          context: '数学考试前',
          duration: '约15分钟'
        },
        {
          emotion: '沮丧',
          type: 'danger',
          time: '今天 14:36',
          context: '与同学交流后',
          duration: '约10分钟'
        },
        {
          emotion: '焦虑',
          type: 'warning',
          time: '今天 16:45',
          context: '写作业时',
          duration: '约12分钟'
        }
      ]
    }
  },
  mounted() {
    // 使用nextTick确保DOM已经渲染完成
    this.$nextTick(() => {
      this.initEmotionCharts();
      // 对接真实接口
      this.loadEmotionRealData();
      // 设置定时器，确保图表正确渲染并添加动画效果
      setTimeout(() => {
        this.resizeCharts();
        this.animateCharts();
        this.chartsReady = true;
      }, 500);
    });
    
    // 监听窗口大小变化，重新调整图表大小
    window.addEventListener('resize', this.resizeCharts);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeCharts);
  },
  methods: {
    // 真实数据装载
    async loadEmotionRealData() {
      try {
        // 1) 趋势与主导情绪
        const trendRes = await fetch('/api/monitor/emotion/trends');
        const trendJson = trendRes.ok ? await trendRes.json() : null;
        const labels = trendJson?.labels || [];
        const values = trendJson?.data || [];
        const dominant = trendJson?.emotions || [];

        // 2) 雷达数据
        const radarRes = await fetch('/api/monitor/emotion/radar');
        const radarJson = radarRes.ok ? await radarRes.json() : null;

        // 更新每日情绪趋势为“情绪指数”单线
        if (this.charts.dailyEmotion) {
          this.charts.dailyEmotion.setOption({
            legend: { data: ['情绪指数'] },
            xAxis: { data: labels },
            series: [
              {
                name: '情绪指数',
                type: 'line',
                data: values.map(v => Math.round(Number(v) * 100)),
                smooth: true,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: { width: 3, color: '#34a853' },
                itemStyle: { color: '#34a853', borderWidth: 2, borderColor: '#fff' },
                areaStyle: {
                  color: {
                    type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [{ offset: 0, color: 'rgba(52,168,83,0.3)' }, { offset: 1, color: 'rgba(52,168,83,0.05)' }]
                  }
                }
              }
            ]
          });
        }

        // 基于主导情绪数组统计分布，更新饼图
        const nameMap = { neutral: '平静', happy: '开心', focused: '专注', sad: '沮丧', angry: '生气', anxious: '焦虑' };
        const counter = {};
        dominant.forEach(k => {
          const cn = nameMap[k] || k;
          counter[cn] = (counter[cn] || 0) + 1;
        });
        const pieData = Object.keys(counter).map(name => ({ name, value: counter[name] }));
        if (this.charts.emotionDistribution && pieData.length) {
          this.charts.emotionDistribution.setOption({
            legend: { data: pieData.map(i => i.name) },
            series: [{ data: pieData }]
          });
        }

        // 雷达图：current/average/optimal
        if (this.charts.emotionFactors && radarJson) {
          const indicators = (radarJson.labels || []).map(n => ({ name: n, max: 100 }));
          this.charts.emotionFactors.setOption({
            radar: { indicator: indicators },
            series: [{
              data: [
                {
                  value: (radarJson.current || []).map(Number),
                  name: '当前',
                }
              ]
            }]
          });
        }
      } catch (e) {
        console.warn('加载情绪真实数据失败，使用占位:', e);
      }
    },
    
    initEmotionCharts() {
      // 基础占位数据，待 loadEmotionRealData 覆盖
      const emotionData = {
        dailyTrend: { times: ['8:00','10:00','12:00','14:00','16:00','18:00','20:00'], emotions: { happy:[70,72,74,76,78,80,82] } },
        distribution: [ { value: 45, name: '开心' }, { value: 30, name: '平静' }, { value: 15, name: '焦虑' }, { value: 7, name: '沮丧' }, { value: 3, name: '生气' } ],
        factors: [80,65,40,60,30]
      };
      
      // 每日情绪趋势图
      const dailyEmotionChart = echarts.init(document.getElementById('dailyEmotionChart'));
      dailyEmotionChart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'line'
          },
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 10,
          textStyle: {
            color: '#333'
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(param => {
              result += '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:' + param.color + '"></span> ';
              result += param.seriesName + ': ' + param.value + '<br/>';
            });
            return result;
          }
        },
        legend: {
          data: ['情绪指数'],
          bottom: 0,
          icon: 'circle',
          itemWidth: 10,
          itemHeight: 10,
          textStyle: {
            fontSize: 12
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '8%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: emotionData.dailyTrend.times,
          axisLine: {
            lineStyle: {
              color: '#ccc'
            }
          },
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          name: '情绪强度',
          nameTextStyle: {
            color: '#666'
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#eee'
            }
          },
          axisLabel: {
            color: '#666'
          }
        },
        series: [
          {
            name: '情绪指数',
            type: 'line',
            data: emotionData.dailyTrend.emotions.happy,
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              width: 3,
              color: '#34a853',
              shadowColor: 'rgba(52, 168, 83, 0.3)',
              shadowBlur: 10
            },
            itemStyle: {
              color: '#34a853',
              borderWidth: 2,
              borderColor: '#fff'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{ offset: 0, color: 'rgba(52, 168, 83, 0.3)' }, { offset: 1, color: 'rgba(52, 168, 83, 0.05)' }]
              }
            },
            emphasis: {
              itemStyle: {
                borderWidth: 3,
                borderColor: '#fff',
                shadowColor: 'rgba(52, 168, 83, 0.5)',
                shadowBlur: 10
              }
            }
          }
        ]
      });
      this.charts.dailyEmotion = dailyEmotionChart;
      
      // 情绪分布饼图
      const emotionDistributionChart = echarts.init(document.getElementById('emotionDistributionChart'));
      
      // 定义情绪颜色映射
      const emotionColors = {
        '开心': '#34a853',
        '平静': '#4285f4',
        '焦虑': '#fbbc05',
        '沮丧': '#9c27b0',
        '生气': '#ea4335'
      };
      
      // 处理数据，添加颜色
      const pieData = emotionData.distribution.map(item => ({
        ...item,
        itemStyle: {
          color: emotionColors[item.name] || '#888',
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        }
      }));
      
      emotionDistributionChart.setOption({
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 10,
          textStyle: {
            color: '#333'
          },
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          icon: 'circle',
          itemWidth: 10,
          itemHeight: 10,
          textStyle: {
            fontSize: 12,
            color: '#333'
          },
          formatter: name => {
            const item = emotionData.distribution.find(d => d.name === name);
            return name + ' ' + (item ? item.value + '%' : '');
          }
        },
        series: [
          {
            name: '情绪分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold',
                formatter: '{b}\n{c}%'
              },
              itemStyle: {
                shadowBlur: 15,
                shadowColor: 'rgba(0, 0, 0, 0.2)'
              }
            },
            labelLine: {
              show: false
            },
            data: pieData
          }
        ]
      });
      this.charts.emotionDistribution = emotionDistributionChart;
      
      // 情绪影响因素图
      const emotionFactorsChart = echarts.init(document.getElementById('emotionFactorsChart'));
      emotionFactorsChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 10,
          textStyle: {
            color: '#333'
          },
          formatter: function (params) {
            return params.name + '<br/>' + params.marker + params.value;
          }
        },
        radar: {
          indicator: [
            { name: '学习压力', max: 100 },
            { name: '社交关系', max: 100 },
            { name: '身体状况', max: 100 },
            { name: '睡眠质量', max: 100 },
            { name: '家庭氛围', max: 100 }
          ],
          shape: 'circle',
          splitNumber: 5,
          axisName: {
            color: '#333',
            fontSize: 12
          },
          splitLine: {
            lineStyle: {
              color: ['#ddd'],
              width: 1
            }
          },
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(250,250,250,0.3)', 'rgba(240,240,240,0.3)']
            }
          },
          axisLine: {
            lineStyle: {
              color: '#ddd',
              width: 1
            }
          }
        },
        series: [{
          name: '情绪影响因素',
          type: 'radar',
          data: [
            {
              value: emotionData.factors,
              name: '影响程度',
              symbol: 'circle',
              symbolSize: 8,
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 1,
                  y2: 1,
                  colorStops: [{
                    offset: 0,
                    color: 'rgba(66, 133, 244, 0.7)'
                  }, {
                    offset: 1,
                    color: 'rgba(66, 133, 244, 0.3)'
                  }]
                },
                shadowBlur: 15,
                shadowColor: 'rgba(66, 133, 244, 0.2)',
                opacity: 0.7
              },
              lineStyle: {
                width: 3,
                color: 'rgba(66, 133, 244, 0.8)',
                shadowBlur: 10,
                shadowColor: 'rgba(66, 133, 244, 0.5)'
              },
              itemStyle: {
                color: '#4285f4',
                borderWidth: 2,
                borderColor: '#fff',
                shadowBlur: 5,
                shadowColor: 'rgba(66, 133, 244, 0.5)'
              },
              emphasis: {
                lineStyle: {
                  width: 4,
                  shadowBlur: 15
                },
                itemStyle: {
                  shadowBlur: 10
                }
              }
            }
          ]
        }]
      });
      this.charts.emotionFactors = emotionFactorsChart;
    },
    
    // 添加动画效果
    animateCharts() {
      for (const key in this.charts) {
        if (this.charts[key]) {
          try {
            // 获取当前配置
            const currentOption = this.charts[key].getOption();
            
            // 根据图表类型添加不同的动画
            if (key === 'dailyEmotion') {
              // 针对折线图的动画
              this.charts[key].setOption({
                series: currentOption.series.map(series => ({
                  ...series,
                  animationDuration: 1500,
                  animationEasing: 'cubicInOut',
                  animationDelay: idx => idx * 120
                }))
              });
            } else if (key === 'emotionDistribution') {
              // 针对饼图的动画
              this.charts[key].setOption({
                series: currentOption.series.map(series => ({
                  ...series,
                  animationDuration: 1200,
                  animationEasing: 'cubicInOut',
                  animationDelay: idx => idx * 100
                }))
              });
            } else if (key === 'emotionFactors') {
              // 针对雷达图的动画
              this.charts[key].setOption({
                series: currentOption.series.map(series => ({
                  ...series,
                  animationDuration: 1500,
                  animationEasing: 'elasticOut',
                  animationDelay: 300
                }))
              });
            }
          } catch (e) {
            console.error('图表动画添加失败:', e);
          }
        }
      }
    },
    
    resizeCharts() {
      for (const key in this.charts) {
        if (this.charts[key]) {
          try {
            this.charts[key].resize();
          } catch (e) {
            console.error('图表调整大小失败:', e);
          }
        }
      }
    },
    generateEmotionReport() {
      // 直接显示报告生成成功
      alert('情绪分析报告已生成');
      // 可以在这里添加导航逻辑
    },
    viewEmotionHistory() {
      // 直接显示导航成功
      alert('正在查看历史记录');
      // 可以在这里添加导航逻辑
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

.emotion-container {
  padding: 20px;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 25px;
  color: var(--primary-text-color);
}

.dashboard-title {
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 20px;
  font-weight: 500;
}

.alert-box {
  display: flex;
  background-color: rgba(251, 188, 5, 0.2);
  border-left: 4px solid var(--warning-color, #F8B500);
  padding: 15px;
  margin-bottom: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.alert-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  align-self: center;
  height: 30px;
  width: 30px;
  font-size: 1.5rem;
  color: var(--warning-color, #F8B500);
}

.alert-icon span {
  display: block;
  line-height: 1;
  font-size: 24px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.alert-message {
  margin: 0;
  line-height: 1.5;
  color: #555;
}

.emotion-dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 25px;
  margin-bottom: 30px;
  min-height: 700px; /* 最小高度以确保2*2布局 */
}

@media (max-width: 1024px) {
  .emotion-dashboard {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 20px;
  }
  
  .card {
    min-height: 400px; /* 确保卡片在手机上有足够的高度 */
  }
}

.emotion-records {
  height: 100%;
  overflow-y: auto;
  padding: 10px;
}

.emotion-record {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
  border-left: 3px solid var(--primary-color);
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
}

.emotion-record:hover {
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}

.emotion-record-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.emotion-type {
  font-weight: 600;
  border-radius: 15px;
  padding: 4px 12px;
  font-size: 0.9rem;
  display: inline-block;
  transition: all 0.2s ease;
}

.emotion-type.warning {
  color: var(--warning-color);
  background: rgba(251, 188, 5, 0.1);
  border: 1px solid var(--warning-color);
}

.emotion-type.warning:hover {
  background: rgba(251, 188, 5, 0.2);
}

.emotion-type.danger {
  color: var(--danger-color);
  background: rgba(234, 67, 53, 0.1);
  border: 1px solid var(--danger-color);
}

.emotion-type.danger:hover {
  background: rgba(234, 67, 53, 0.2);
}

.emotion-time {
  font-size: 0.9rem;
  color: #666;
}

.emotion-details {
  font-size: 0.95rem;
}

.emotion-context {
  margin-bottom: 5px;
}

.emotion-duration {
  font-size: 0.85rem;
  color: #666;
}

.bottom-actions {
  display: flex;
  justify-content: center;
  margin: 30px 0;
  gap: 20px;
  width: 100%;
  padding: 0 20px;
}

.blue-btn {
  background-color: var(--primary-color, #4285f4);
  color: white;
  border: none;
  border-radius: 30px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  width: 45%;
  max-width: 300px;
  box-shadow: 0 2px 4px rgba(52, 136, 255, 0.25);
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.blue-btn:hover {
  background-color: #3367d6;
  box-shadow: 0 4px 8px rgba(52, 136, 255, 0.3);
  transform: translateY(-2px);
}

.white-btn {
  background-color: white;
  color: var(--primary-color, #4285f4);
  border: 1px solid var(--primary-color, #4285f4);
  border-radius: 30px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  width: 45%;
  max-width: 300px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.white-btn:hover {
  background-color: var(--light-gray, #f5f5f5);
  color: #3367d6;
  border-color: #3367d6;
  transform: translateY(-2px);
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.card-title {
  font-weight: 600;
  font-size: 1.2rem;
  color: var(--dark-gray, #333);
}

.card-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--light-gray, #f5f5f5);
  border-radius: 50%;
  color: var(--primary-color, #4285f4);
  transition: all 0.3s ease;
  font-size: 18px;
}

.card-icon span {
  display: block;
  line-height: 1;
}

.card-icon:hover {
  opacity: 1;
  transform: scale(1.05);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.chart-container {
  flex: 1;
  padding: 15px;
  min-height: 250px;
  height: 300px;
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-inner {
  width: 100%;
  height: 100%;
  z-index: 1;
}

.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.7);
  z-index: 2;
  font-size: 14px;
  color: var(--primary-color);
  animation: pulse 1.5s infinite;
}
</style>
