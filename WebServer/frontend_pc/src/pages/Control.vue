<template>
  <div class="control-container">
    <van-nav-bar title="远程控制" fixed />
    
    <div class="dashboard-title">台灯远程控制面板</div>
    
    <div class="alert alert-info">
      <div class="alert-icon">ℹ️</div>
      <div class="alert-content">
        <h3>远程控制</h3>
        <p>您可以在这里远程控制孩子的台灯，调节亮度、色温和设置护眼模式</p>
      </div>
    </div>
    
    <div class="dashboard lamp-dashboard">
      <!-- 灯光状态卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">台灯状态</div>
          <div class="card-icon">💡</div>
        </div>
        <div class="lamp-status">
          <div class="status-item">
            <div class="status-icon">⚡</div>
            <div class="status-text">
              <div class="status-label">电源状态</div>
              <div class="status-value">{{ lampPowerOn ? '已开启' : '已关闭' }}</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon">🔆</div>
            <div class="status-text">
              <div class="status-label">灯光状态</div>
              <div class="status-value">{{ lampLightOn ? '已开启' : '已关闭' }}</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon">🌡️</div>
            <div class="status-text">
              <div class="status-label">设备温度</div>
              <div class="status-value">38°C (正常)</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon">🌐</div>
            <div class="status-text">
              <div class="status-label">网络连接</div>
              <div class="status-value">已连接</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon">🕒</div>
            <div class="status-text">
              <div class="status-label">最后更新</div>
              <div class="status-value">{{ lastUpdateTime }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 亮度仪表卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">亮度控制</div>
          <div class="card-icon">🔆</div>
        </div>
        <div class="gauge-wrapper">
          <div class="gauge-title">当前亮度</div>
          <div class="gauge">
            <div class="gauge-inner">
              <div class="gauge-needle" id="brightness-needle" :style="{ transform: `translate(-50%, -100%) rotate(${getBrightnessRotation()}deg)` }"></div>
              <div class="gauge-center"></div>
            </div>
          </div>
          <div class="gauge-value">{{ currentBrightness }}</div>
          <div class="gauge-unit">Lux</div>
          <div class="gauge-range">范围: 100-1000 Lux</div>
        </div>
      </div>
      
      <!-- 色温仪表卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">色温控制</div>
          <div class="card-icon">🌈</div>
        </div>
        <div class="gauge-wrapper">
          <div class="gauge-title">当前色温</div>
          <div class="gauge">
            <div class="gauge-inner">
              <div class="gauge-needle" id="temperature-needle" :style="{ transform: `translate(-50%, -100%) rotate(${getTemperatureRotation()}deg)` }"></div>
              <div class="gauge-center"></div>
            </div>
          </div>
          <div class="gauge-value">{{ currentTemperature }}</div>
          <div class="gauge-unit">K</div>
          <div class="gauge-range">范围: 2700-6500 K</div>
        </div>
      </div>
      
      <!-- 灯光控制卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">灯光控制</div>
          <div class="card-icon">🎛️</div>
        </div>
        <div class="light-controls">
          <!-- 电源开关 -->
          <div class="control-group">
            <div class="switch-container">
              <label class="switch">
                <input type="checkbox" v-model="lampPowerOn" @change="togglePower">
                <span class="slider"></span>
              </label>
              <span class="switch-text">电源{{ lampPowerOn ? '开' : '关' }}</span>
            </div>
          </div>
          
          <!-- 灯光开关 -->
          <div class="control-group">
            <div class="switch-container">
              <label class="switch">
                <input type="checkbox" v-model="lampLightOn" @change="toggleLight" :disabled="!lampPowerOn">
                <span class="slider"></span>
              </label>
              <span class="switch-text">灯光{{ lampLightOn ? '开' : '关' }}</span>
            </div>
          </div>
          
          <!-- 亮度滑块 -->
          <div class="control-group">
            <div class="control-label">
              亮度
              <span class="control-value">{{ currentBrightness }} Lux</span>
            </div>
            <div class="slider-container">
              <van-slider 
                v-model="currentBrightness" 
                :min="100" 
                :max="1000"
                :disabled="!lampPowerOn || !lampLightOn"
                @change="adjustBrightness"
              />
            </div>
            <div class="slider-marks">
              <span>100<small>柔和</small></span>
              <span>550<small>标准</small></span>
              <span>1000<small>明亮</small></span>
            </div>
            <div class="quick-buttons">
              <button 
                class="quick-btn" 
                @click="setBrightness(200)"
                :disabled="!lampPowerOn || !lampLightOn"
              >
                柔和
              </button>
              <button 
                class="quick-btn" 
                @click="setBrightness(500)"
                :disabled="!lampPowerOn || !lampLightOn"
              >
                标准
              </button>
              <button 
                class="quick-btn" 
                @click="setBrightness(800)"
                :disabled="!lampPowerOn || !lampLightOn"
              >
                明亮
              </button>
            </div>
          </div>
          
          <!-- 色温滑块 -->
          <div class="control-group">
            <div class="control-label">
              色温
              <span class="control-value">{{ currentTemperature }} K</span>
            </div>
            <div class="slider-container">
              <van-slider 
                v-model="currentTemperature" 
                :min="2700" 
                :max="6500"
                :disabled="!lampPowerOn || !lampLightOn"
                @change="adjustTemperature"
              />
            </div>
            <div class="slider-marks">
              <span>2700<small>暖光</small></span>
              <span>4600<small>自然光</small></span>
              <span>6500<small>冷光</small></span>
            </div>
            <div class="quick-buttons">
              <button 
                class="quick-btn" 
                @click="setTemperature(2700)"
                :disabled="!lampPowerOn || !lampLightOn"
              >
                暖光
              </button>
              <button 
                class="quick-btn" 
                @click="setTemperature(4600)"
                :disabled="!lampPowerOn || !lampLightOn"
              >
                自然光
              </button>
              <button 
                class="quick-btn" 
                @click="setTemperature(6500)"
                :disabled="!lampPowerOn || !lampLightOn"
              >
                冷光
              </button>
            </div>
          </div>
          
          <!-- 应用按钮 -->
          <van-button 
            type="primary" 
            block 
            class="apply-btn"
            @click="applyLightSettings"
            :disabled="!lampPowerOn || !lampLightOn"
          >
            应用设置
          </van-button>
        </div>
      </div>
      
      <!-- 护眼设置卡片 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">护眼设置</div>
          <div class="card-icon">👁️</div>
        </div>
        <div class="eye-care-settings">
          <!-- 远眺休息 -->
          <div class="setting-group">
            <div class="setting-title">远眺休息提醒</div>
            <div class="setting-desc">根据"20-20-20"护眼原则，每隔一段时间提醒孩子远眺休息</div>
            <div class="setting-control">
              <div class="input-group">
                <label for="rest-interval">提醒间隔：</label>
                <input type="number" id="rest-interval" class="setting-input" v-model="restInterval" min="10" max="60">
                <span class="input-unit">分钟</span>
              </div>
              <div class="preset-buttons">
                <button 
                  class="preset-btn" 
                  :class="{ active: restInterval === 20 }"
                  @click="setRestInterval(20)"
                >
                  20分钟
                </button>
                <button 
                  class="preset-btn" 
                  :class="{ active: restInterval === 30 }"
                  @click="setRestInterval(30)"
                >
                  30分钟
                </button>
                <button 
                  class="preset-btn" 
                  :class="{ active: restInterval === 45 }"
                  @click="setRestInterval(45)"
                >
                  45分钟
                </button>
              </div>
            </div>
          </div>
          
          <!-- 长时间用眼提醒 -->
          <div class="setting-group">
            <div class="setting-title">长时间用眼提醒</div>
            <div class="setting-desc">当连续用眼超过设定时间，提醒孩子起身活动</div>
            <div class="setting-control">
              <div class="input-group">
                <label for="eye-strain-limit">时间限制：</label>
                <input type="number" id="eye-strain-limit" class="setting-input" v-model="eyeStrainLimit" min="30" max="180">
                <span class="input-unit">分钟</span>
              </div>
              <div class="preset-buttons">
                <button 
                  class="preset-btn" 
                  :class="{ active: eyeStrainLimit === 60 }"
                  @click="setEyeStrainLimit(60)"
                >
                  1小时
                </button>
                <button 
                  class="preset-btn" 
                  :class="{ active: eyeStrainLimit === 90 }"
                  @click="setEyeStrainLimit(90)"
                >
                  1.5小时
                </button>
                <button 
                  class="preset-btn" 
                  :class="{ active: eyeStrainLimit === 120 }"
                  @click="setEyeStrainLimit(120)"
                >
                  2小时
                </button>
              </div>
            </div>
          </div>
          
          <!-- 提醒方式 -->
          <div class="setting-group">
            <div class="setting-title">提醒方式</div>
            <div class="reminder-options">
              <label class="option-item">
                <input type="checkbox" v-model="reminderOptions.voice">
                <span>语音提醒</span>
              </label>
              <label class="option-item">
                <input type="checkbox" v-model="reminderOptions.light">
                <span>灯光闪烁</span>
              </label>
              <label class="option-item">
                <input type="checkbox" v-model="reminderOptions.message">
                <span>APP消息提醒</span>
              </label>
            </div>
          </div>
          
          <van-button type="primary" block class="save-settings-btn" @click="saveEyeCareSettings">
            保存护眼设置
          </van-button>
        </div>
      </div>
      
      <!-- 小贴士卡片 -->
      <div class="card tips-card">
        <div class="card-header">
          <div class="card-title">护眼小贴士</div>
          <div class="card-icon">💡</div>
        </div>
        <div class="tips-content">
          <div class="tip-item">
            <div class="tip-icon">👁️</div>
            <div class="tip-text">
              <h5>20-20-20法则</h5>
              <p>每20分钟，看20英尺(约6米)外的物体20秒，有效缓解眼睛疲劳</p>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">📏</div>
            <div class="tip-text">
              <h5>保持阅读距离</h5>
              <p>阅读或使用电子设备时，眼睛与屏幕/书本的距离应保持在30-40厘米</p>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">🌞</div>
            <div class="tip-text">
              <h5>户外活动</h5>
              <p>每天至少进行2小时户外活动，自然光有助于减缓近视发展</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ControlPage',
  data() {
    return {
      lampPowerOn: true,
      lampLightOn: true,
      currentBrightness: 500,
      currentTemperature: 4600,
      lastUpdateTime: this.getCurrentTime(),
      restInterval: 20,
      eyeStrainLimit: 60,
      reminderOptions: {
        voice: true,
        light: true,
        message: false
      }
    }
  },
  mounted() {
    this.fetchLampStatus();
  },
  methods: {
    fetchLampStatus() {
      // 模拟从API获取台灯状态
      console.log('获取台灯状态...');
      
      // 假设已从API获取数据
      this.lastUpdateTime = this.getCurrentTime();
    },
    togglePower() {
      if (!this.lampPowerOn) {
        this.lampLightOn = false;
      }
      this.sendSerialCommand(this.lampPowerOn ? 'power_on' : 'power_off');
    },
    toggleLight() {
      this.sendSerialCommand(this.lampLightOn ? 'light_on' : 'light_off');
    },
    adjustBrightness(value) {
      console.log(`调节亮度: ${value}`);
    },
    setBrightness(value) {
      this.currentBrightness = value;
      this.adjustBrightness(value);
    },
    adjustTemperature(value) {
      console.log(`调节色温: ${value}`);
    },
    setTemperature(value) {
      this.currentTemperature = value;
      this.adjustTemperature(value);
    },
    applyLightSettings() {
      this.sendSerialCommand(`set_brightness=${this.currentBrightness}&set_temperature=${this.currentTemperature}`);
      alert(`已应用灯光设置: 亮度=${this.currentBrightness} Lux, 色温=${this.currentTemperature} K`);
    },
    sendSerialCommand(command) {
      console.log(`发送串口命令: ${command}`);
      // 实际应用中这里会发送API请求到后端
    },
    setRestInterval(minutes) {
      this.restInterval = minutes;
    },
    setEyeStrainLimit(minutes) {
      this.eyeStrainLimit = minutes;
    },
    saveEyeCareSettings() {
      const settings = {
        restInterval: this.restInterval,
        eyeStrainLimit: this.eyeStrainLimit,
        reminderOptions: this.reminderOptions
      };
      console.log('保存护眼设置:', settings);
      
      // 实际应用中这里会发送API请求到后端
      alert('护眼设置已保存');
    },
    getCurrentTime() {
      return new Date().toLocaleString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    getBrightnessRotation() {
      // 将亮度值(100-1000)映射到角度(0-180)
      return (this.currentBrightness - 100) / 900 * 180;
    },
    getTemperatureRotation() {
      // 将色温值(2700-6500)映射到角度(0-180)
      return (this.currentTemperature - 2700) / 3800 * 180;
    }
  }
}
</script>

<style scoped>
.control-container {
  padding-top: 46px; /* 为固定的NavBar留出空间 */
}

.lamp-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  align-items: start;
  padding: 10px 0;
}

/* 仪表盘样式 */
.gauge-wrapper {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
}

.gauge-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--dark-gray);
}

.gauge {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 15px;
}

.gauge-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    #ea4335 0%,
    #fbbc05 33%,
    #4285f4 66%,
    #34a853 100%
  );
  position: relative;
  padding: 10px;
}

.gauge-inner::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  bottom: 10px;
  background: white;
  border-radius: 50%;
}

.gauge-needle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 60px;
  background: var(--dark-gray);
  transform-origin: bottom center;
  transform: translate(-50%, -100%) rotate(0deg);
  z-index: 10;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.gauge-center {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  background: var(--dark-gray);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 11;
}

.gauge-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 12px 0 4px 0;
  line-height: 1.2;
}

.gauge-unit {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
  margin-bottom: 12px;
  line-height: 1.2;
}

.gauge-range {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
  margin-top: 0;
  line-height: 1.2;
}

/* 状态指示器 */
.lamp-status {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px;
  background: var(--light-gray);
  border-radius: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-text {
  flex: 1;
}

.status-label {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
}

.status-value {
  font-weight: 600;
  color: var(--dark-gray);
}

/* 灯光控制样式 */
.light-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 15px 0;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-label {
  font-weight: 600;
  color: var(--dark-gray);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-value {
  font-weight: 400;
  color: var(--primary-color);
}

/* 开关样式 */
.switch-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary-color);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.switch-text {
  font-weight: 500;
  color: var(--text-color);
}

/* 滑块标记 */
.slider-marks {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.7;
}

.slider-marks span {
  text-align: center;
}

.slider-marks small {
  display: block;
  font-size: 0.7rem;
  margin-top: 2px;
}

/* 快捷按钮 */
.quick-buttons {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 6px 12px;
  border: 1px solid var(--primary-color);
  background: white;
  color: var(--primary-color);
  border-radius: 15px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
  transform: translateY(-1px);
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ccc;
  color: #999;
}

.apply-btn {
  margin-top: 15px;
}

/* 护眼设置样式 */
.eye-care-settings {
  display: flex;
  flex-direction: column;
  gap: 25px;
  padding: 15px 0;
}

.setting-group {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.setting-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--dark-gray);
  margin-bottom: 5px;
}

.setting-desc {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
  margin-bottom: 15px;
}

.setting-control {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-input {
  width: 80px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  text-align: center;
}

.input-unit {
  font-weight: 500;
  color: var(--text-color);
}

.preset-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  color: var(--text-color);
  border-radius: 15px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn.active {
  border-color: var(--primary-color);
  background: var(--primary-color);
  color: white;
}

.preset-btn:hover:not(.active) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.reminder-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 0;
}

.option-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.save-settings-btn {
  margin-top: 10px;
}

/* 小贴士样式 */
.tips-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.tips-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 15px 0;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tip-icon {
  font-size: 1.5rem;
  width: 40px;
  text-align: center;
  flex-shrink: 0;
}

.tip-text h5 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--dark-gray);
  margin-bottom: 5px;
}

.tip-text p {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
  margin: 0;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .lamp-dashboard {
    grid-template-columns: 1fr;
  }
  
  .quick-buttons, .preset-buttons {
    justify-content: space-between;
  }
}
</style>
