<template>
  <div class="mobile-page">
    <div class="page-heading">远程控制</div>
    
    <!-- 亮度控制卡片 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">亮度控制</div>
      </div>
      <div class="mobile-card-content">
        <div class="brightness-control">
          <div class="brightness-level">
            <i class="bi bi-brightness-low"></i>
            <van-slider
              v-model="brightness"
              :min="1"
              :max="100"
              @change="updateBrightness"
            />
            <i class="bi bi-brightness-high"></i>
          </div>
          <div class="brightness-value">{{ brightness }}%</div>
        </div>
        
        <div class="brightness-presets">
          <div class="preset-button" @click="setBrightness(25)">
            <i class="bi bi-moon"></i>
            <span>夜间</span>
          </div>
          <div class="preset-button" @click="setBrightness(50)">
            <i class="bi bi-cloud-sun"></i>
            <span>舒适</span>
          </div>
          <div class="preset-button" @click="setBrightness(75)">
            <i class="bi bi-sun"></i>
            <span>标准</span>
          </div>
          <div class="preset-button" @click="setBrightness(100)">
            <i class="bi bi-lightbulb"></i>
            <span>明亮</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 色温控制卡片 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">色温控制</div>
      </div>
      <div class="mobile-card-content">
        <div class="temperature-control">
          <div class="temperature-level">
            <i class="bi bi-thermometer-low"></i>
            <van-slider
              v-model="colorTemperature"
              :min="2700"
              :max="6500"
              :step="100"
              @change="updateColorTemperature"
            />
            <i class="bi bi-thermometer-high"></i>
          </div>
          <div class="temperature-value">{{ colorTemperature }}K</div>
        </div>
        
        <div class="temperature-display" :style="temperatureColorStyle"></div>
        
        <div class="temperature-presets">
          <div class="preset-button" @click="setColorTemperature(2700)">
            <span>暖光</span>
            <span class="temp-value">2700K</span>
          </div>
          <div class="preset-button" @click="setColorTemperature(4000)">
            <span>中性光</span>
            <span class="temp-value">4000K</span>
          </div>
          <div class="preset-button" @click="setColorTemperature(6500)">
            <span>冷光</span>
            <span class="temp-value">6500K</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 功能控制卡片 -->
    <div class="mobile-card">
      <div class="mobile-card-header green-gradient">
        <div class="mobile-card-title">功能控制</div>
      </div>
      <div class="mobile-card-content">
        <div class="control-grid">
          <div class="control-button" @click="togglePower">
            <i class="bi" :class="isOn ? 'bi-power' : 'bi-power text-danger'"></i>
            <span>{{ isOn ? '关闭' : '开启' }}</span>
          </div>
          <div class="control-button" @click="toggleAutoAdjust">
            <i class="bi" :class="autoAdjust ? 'bi-magic text-primary' : 'bi-magic'"></i>
            <span>{{ autoAdjust ? '自动调节已开启' : '自动调节' }}</span>
          </div>
          <div class="control-button" @click="toggleStudyMode">
            <i class="bi" :class="studyMode ? 'bi-book-half text-primary' : 'bi-book-half'"></i>
            <span>{{ studyMode ? '学习模式已开启' : '学习模式' }}</span>
          </div>
          <div class="control-button" @click="toggleTimerMode">
            <i class="bi" :class="timerMode ? 'bi-alarm text-primary' : 'bi-alarm'"></i>
            <span>{{ timerMode ? '定时已开启' : '定时设置' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 定时设置弹窗 -->
    <van-dialog
      v-model:show="showTimerDialog"
      title="定时设置"
      show-cancel-button
      @confirm="confirmTimer"
    >
      <div class="timer-settings">
        <div class="timer-item">
          <span>开灯时间:</span>
          <input type="time" v-model="timerOn" />
        </div>
        <div class="timer-item">
          <span>关灯时间:</span>
          <input type="time" v-model="timerOff" />
        </div>
        <div class="timer-days">
          <div class="day-item" 
               v-for="(day, index) in days" :key="index"
               :class="{ active: selectedDays.includes(day) }"
               @click="toggleDay(day)">
            {{ day }}
          </div>
        </div>
      </div>
    </van-dialog>
    
    <!-- 操作反馈 -->
    <van-toast id="toast" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { Toast } from 'vant';
import { useDeviceStore } from '../stores';
import { controlApi } from '../api';

const deviceStore = useDeviceStore();

// 灯光状态
const isOn = ref(true);
const brightness = ref(70);
const colorTemperature = ref(4000);
const autoAdjust = ref(true);
const studyMode = ref(false);
const timerMode = ref(false);

// 定时设置
const showTimerDialog = ref(false);
const timerOn = ref('08:00');
const timerOff = ref('22:00');
const days = ['一', '二', '三', '四', '五', '六', '日'];
const selectedDays = ref(['一', '二', '三', '四', '五']);



// 色温显示样式
const temperatureColorStyle = computed(() => {
  // 将开尔文色温转换为近似的RGB
  const temp = colorTemperature.value;
  let r, g, b;
  
  if (temp <= 4000) {
    // 暖色调
    r = 255;
    g = Math.round(160 + (temp - 2700) * 0.08);
    b = Math.round(109 + (temp - 2700) * 0.12);
  } else {
    // 冷色调
    r = Math.round(255 - (temp - 4000) * 0.03);
    g = Math.round(240 - (temp - 4000) * 0.015);
    b = Math.round(200 + (temp - 4000) * 0.022);
  }
  
  return {
    backgroundColor: `rgb(${r}, ${g}, ${b})`,
    boxShadow: `0 0 15px rgba(${r}, ${g}, ${b}, 0.7)`
  };
});

// 刷新色温显示条
const refreshColorTemperatureDisplay = async () => {
  await nextTick();
  
  // 强制触发色温显示样式的重新计算
  const currentTemp = colorTemperature.value;
  
  // 临时改变值触发重新渲染
  colorTemperature.value = currentTemp + 1;
  
  await nextTick();
  
  // 恢复原值
  colorTemperature.value = currentTemp;
  
  // 强制DOM更新
  await nextTick();
};

// 监听色温变化，自动刷新显示
watch(colorTemperature, () => {
  nextTick(() => {
    // 确保色温显示条正确渲染
    const temperatureDisplay = document.querySelector('.temperature-display');
    if (temperatureDisplay) {
      // 强制重新应用样式
      temperatureDisplay.style.transition = 'none';
      setTimeout(() => {
        temperatureDisplay.style.transition = 'background-color 0.5s ease';
      }, 10);
    }
  });
});

// 同步设备设置
const syncDeviceSettings = async () => {
  await deviceStore.fetchDeviceSettings();
  
  // 同步设备设置到当前界面
  if (deviceStore.deviceSettings) {
    brightness.value = deviceStore.deviceSettings.brightness;
    colorTemperature.value = deviceStore.deviceSettings.colorTemperature;
    autoAdjust.value = deviceStore.deviceSettings.autoAdjust;
    
    // 刷新色温显示条
    setTimeout(() => {
      refreshColorTemperatureDisplay();
    }, 150);
  }
};

// 更新亮度
const updateBrightness = async () => {
  try {
    await controlApi.setLightBrightness(brightness.value);
    Toast.success('亮度已更新');
  } catch (error) {
    Toast.fail('操作失败');
    console.error(error);
  }
};

// 设置预设亮度
const setBrightness = (value) => {
  brightness.value = value;
  updateBrightness();
};

// 更新色温
const updateColorTemperature = async () => {
  try {
    await controlApi.setLightColor({ temperature: colorTemperature.value });
    Toast.success('色温已更新');
  } catch (error) {
    Toast.fail('操作失败');
    console.error(error);
  }
};

// 设置预设色温
const setColorTemperature = (value) => {
  colorTemperature.value = value;
  updateColorTemperature();
};

// 开关控制
const togglePower = async () => {
  isOn.value = !isOn.value;
  
  try {
    await controlApi.setLightPower(isOn.value);
    Toast.success(isOn.value ? '已开启' : '已关闭');
  } catch (error) {
    Toast.fail('操作失败');
    console.error(error);
    isOn.value = !isOn.value; // 恢复状态
  }
};

// 自动调节开关
const toggleAutoAdjust = async () => {
  autoAdjust.value = !autoAdjust.value;
  
  try {
    await deviceStore.updateDeviceSettings({ autoAdjust: autoAdjust.value });
    Toast.success(autoAdjust.value ? '自动调节已开启' : '自动调节已关闭');
  } catch (error) {
    Toast.fail('操作失败');
    console.error(error);
    autoAdjust.value = !autoAdjust.value; // 恢复状态
  }
};

// 学习模式开关
const toggleStudyMode = () => {
  studyMode.value = !studyMode.value;
  
  if (studyMode.value) {
    // 设置学习模式参数
    brightness.value = 85;
    colorTemperature.value = 5500;
    updateBrightness();
    updateColorTemperature();
    Toast.success('学习模式已开启');
  } else {
    Toast.success('学习模式已关闭');
  }
};

// 定时模式开关
const toggleTimerMode = () => {
  if (timerMode.value) {
    timerMode.value = false;
    Toast.success('定时模式已关闭');
  } else {
    showTimerDialog.value = true;
  }
};

// 切换日期选择
const toggleDay = (day) => {
  if (selectedDays.value.includes(day)) {
    selectedDays.value = selectedDays.value.filter(d => d !== day);
  } else {
    selectedDays.value.push(day);
  }
};

// 确认定时设置
const confirmTimer = () => {
  timerMode.value = true;
  Toast.success('定时设置已保存');
};

// 加载设备数据
onMounted(async () => {
  await deviceStore.fetchDeviceStatus();
  await syncDeviceSettings();
  
  // 页面加载完成后多次刷新色温显示条，确保正确渲染
  setTimeout(() => {
    refreshColorTemperatureDisplay();
  }, 300);
  
  setTimeout(() => {
    refreshColorTemperatureDisplay();
  }, 600);
  
  setTimeout(() => {
    refreshColorTemperatureDisplay();
  }, 1000);
});
</script>

<style scoped>
.page-heading {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.refresh-button {
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
}



.brightness-control,
.temperature-control {
  margin-bottom: 20px;
}

.brightness-level,
.temperature-level {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.brightness-level i,
.temperature-level i {
  font-size: 20px;
  color: var(--color-text-secondary);
  margin: 0 12px;
}

.brightness-value,
.temperature-value {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.brightness-presets,
.temperature-presets {
  display: flex;
  justify-content: space-between;
}

.preset-button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--gradient-light); /* 使用浅色渐变背景 */
  color: #1B4332; /* 深绿色文字 */
  padding: 10px 5px;
  border-radius: var(--radius);
  cursor: pointer;
  margin: 0 4px;
  box-shadow: 0 2px 6px rgba(27, 67, 50, 0.12); /* 添加轻微阴影 */
  border: 1px solid rgba(230, 242, 237, 0.8); /* 添加浅色边框 */
}

.preset-button:first-child {
  margin-left: 0;
}

.preset-button:last-child {
  margin-right: 0;
}

.preset-button i {
  font-size: 20px;
  margin-bottom: 4px;
}

.preset-button span {
  font-size: 12px;
  color: #1B4332; /* 深绿色文字 */
}

.preset-button .temp-value {
  font-size: 10px;
  color: rgba(27, 67, 50, 0.8); /* 深绿色半透明 */
  margin-top: 2px;
}

.temperature-display {
  height: 30px;
  border-radius: var(--radius);
  margin: 16px 0;
  transition: background-color 0.5s ease;
  position: relative;
  /* 添加深色渐变背景作为基础 */
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #2980b9 100%);
  /* 添加内阴影效果 */
  box-shadow: 
    inset 0 2px 4px rgba(0, 0, 0, 0.2),
    0 2px 8px rgba(52, 152, 219, 0.3);
  /* 添加边框 */
  border: 1px solid rgba(52, 152, 219, 0.4);
  /* 确保色温颜色能够叠加在深色背景上 */
  background-blend-mode: overlay;
}

.control-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.control-button {
  background: var(--gradient-light); /* 使用浅色渐变背景 */
  color: #1B4332; /* 深绿色文字 */
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(27, 67, 50, 0.12); /* 轻微阴影 */
  border: 1px solid rgba(230, 242, 237, 0.8); /* 添加浅色边框 */
}

.control-button i {
  font-size: 24px;
  margin-bottom: 8px;
}

.timer-settings {
  padding: 16px;
}

.timer-item {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.timer-item input {
  background: var(--color-card-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 8px;
  border-radius: 4px;
}

.timer-days {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.day-item {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-card-hover);
  cursor: pointer;
}

.day-item.active {
  background-color: var(--color-primary);
  color: white;
}

.text-primary { color: var(--color-primary); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-danger); }
</style>
