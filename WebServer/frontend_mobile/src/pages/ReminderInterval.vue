<template>
  <div class="mobile-page reminder-page">
    <div class="page-heading">设置提醒间隔</div>
    
    <div class="interval-list">
      <div 
        v-for="option in intervalOptions" 
        :key="option.value"
        :class="['interval-item', selectedInterval === option.value ? 'selected' : '']"
        @click="selectInterval(option.value)"
      >
        <div class="interval-label">{{ option.label }}</div>
        <div class="interval-check">
          <i v-if="selectedInterval === option.value" class="bi bi-check"></i>
        </div>
      </div>
      
      <!-- 自定义间隔选项 -->
      <div class="interval-item custom-item">
        <div class="custom-input-group">
          <input 
            v-model="customValue" 
            type="number" 
            min="5" 
            max="180" 
            class="custom-input"
            placeholder="自定义"
            @focus="selectInterval('custom')"
            @input="updateCustomInterval"
          >
          <span class="input-unit">分钟</span>
        </div>
        <div class="interval-check">
          <i v-if="selectedInterval === 'custom'" class="bi bi-check"></i>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="action-buttons">
      <button class="save-btn" @click="saveSettings">
        保存设置
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'

const router = useRouter()

// 选中的间隔
const selectedInterval = ref(30) // 默认30分钟
const customValue = ref('')

// 预设间隔选项
const intervalOptions = [
  { value: 30, label: '30分钟' },
  { value: 60, label: '1小时' },
  { value: 90, label: '1.5小时' }
]

// 选择间隔
const selectInterval = (value) => {
  selectedInterval.value = value
  if (value !== 'custom' && value !== selectedInterval.value) {
    customValue.value = ''
  }
}

// 更新自定义间隔
const updateCustomInterval = () => {
  if (customValue.value && customValue.value >= 5 && customValue.value <= 180) {
    selectedInterval.value = 'custom'
  }
}

// 保存设置
const saveSettings = async () => {
  let intervalValue = selectedInterval.value
  
  if (selectedInterval.value === 'custom') {
    if (!customValue.value || customValue.value < 5 || customValue.value > 180) {
      showToast('请输入5-180分钟之间的数值')
      return
    }
    intervalValue = parseInt(customValue.value)
  }
  
  try {
    // 这里应该调用API保存设置
    console.log('保存提醒间隔:', intervalValue)
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    showToast({
      message: '设置保存成功',
      type: 'success'
    })
    
    // 延迟返回上一页
    setTimeout(() => {
      router.go(-1)
    }, 1000)
    
  } catch (error) {
    showToast({
      message: '保存失败，请重试',
      type: 'fail'
    })
  }
}
</script>

<style scoped>
.reminder-page {
  background: #f5f5f5;
  min-height: 100vh;
}

.page-heading {
  background: white;
  padding: 20px 16px 16px;
  margin-bottom: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary-color);
  border-bottom: 1px solid #e5e5e5;
}

.interval-list {
  background: white;
  margin: 0;
  border-radius: 0;
}

.interval-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.interval-item:hover {
  background-color: #f8f8f8;
}

.interval-item:last-child {
  border-bottom: none;
}

.interval-label {
  font-size: 16px;
  color: var(--text-primary-color);
  font-weight: 400;
}

.interval-check {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #007AFF;
  font-weight: 600;
}

.interval-item:not(.selected) .interval-check {
  opacity: 0;
}

.custom-item {
  border-bottom: none;
}

.custom-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.custom-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  outline: none;
  width: 80px;
  text-align: center;
  transition: border-color 0.3s ease;
  background: #f9f9f9;
}

.custom-input:focus {
  border-color: #007AFF;
  background: white;
}

.input-unit {
  font-size: 16px;
  color: var(--text-secondary-color);
}

.action-buttons {
  padding: 20px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #e5e5e5;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.save-btn {
  width: 100%;
  padding: 14px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background: #0056CC;
}

.save-btn:active {
  transform: scale(0.98);
}

/* 为底部按钮预留空间 */
.reminder-page {
  padding-bottom: 100px;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .reminder-page {
    background: #1c1c1e;
  }
  
  .page-heading,
  .interval-list,
  .interval-item {
    background: #2c2c2e;
    border-color: #3a3a3c;
  }
  
  .action-buttons {
    background: #2c2c2e;
    border-top-color: #3a3a3c;
  }
  
  .custom-input {
    background: #3a3a3c;
    border-color: #48484a;
    color: white;
  }
  
  .custom-input:focus {
    background: #48484a;
    border-color: #007AFF;
  }
  
  .interval-item:hover {
    background-color: #3a3a3c;
  }
}
</style>
