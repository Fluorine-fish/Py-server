<template>
  <div class="mobile-page">
    <div class="page-heading">监护设置</div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">坐姿检测设置</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="启用坐姿检测">
            <template #right-icon>
              <van-switch v-model="settings.posture.enabled" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="检测灵敏度">
            <template #right-icon>
              <div class="sensitivity-selector">
                <div 
                  v-for="level in sensitivityLevels" 
                  :key="level.value"
                  :class="['sensitivity-option', settings.posture.sensitivity === level.value ? 'active' : '']"
                  @click="settings.posture.sensitivity = level.value"
                >
                  {{ level.label }}
                </div>
              </div>
            </template>
          </van-cell>
          
          <van-cell title="不良姿势提醒" is-link @click="showTimeIntervalPicker('posture')">
            <template #value>
              <span>{{ formatTimeInterval(settings.posture.warningInterval) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="AI校正辅助">
            <template #right-icon>
              <van-switch v-model="settings.posture.aiAssist" size="24" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">用眼监护设置</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="启用用眼监护">
            <template #right-icon>
              <van-switch v-model="settings.eye.enabled" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="屏幕距离监测">
            <template #right-icon>
              <van-switch v-model="settings.eye.distanceDetection" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="最小安全距离" is-link @click="showDistancePicker">
            <template #value>
              <span>{{ settings.eye.minDistance }}厘米</span>
            </template>
          </van-cell>
          
          <van-cell title="用眼休息提醒" is-link @click="goToReminderInterval">
            <template #value>
              <span>{{ formatTimeInterval(settings.eye.breakInterval) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="休息时长" is-link @click="showBreakDurationPicker">
            <template #value>
              <span>{{ settings.eye.breakDuration }}分钟</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">情绪检测设置</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="启用情绪检测">
            <template #right-icon>
              <van-switch v-model="settings.emotion.enabled" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="检测频率" is-link @click="showTimeIntervalPicker('emotion')">
            <template #value>
              <span>{{ formatTimeInterval(settings.emotion.detectionInterval) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="负面情绪提醒">
            <template #right-icon>
              <van-switch v-model="settings.emotion.negativeAlert" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="AI情绪分析">
            <template #right-icon>
              <van-switch v-model="settings.emotion.aiAnalysis" size="24" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="action-buttons">
      <van-button block type="primary" @click="saveSettings">保存设置</van-button>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { showToast, showDialog } from 'vant';
import { useRouter } from 'vue-router';

const router = useRouter();

// 敏感度级别选项
const sensitivityLevels = [
  { value: 'low', label: '低' },
  { value: 'medium', label: '中' },
  { value: 'high', label: '高' }
];

// 监护设置
const settings = reactive({
  posture: {
    enabled: true,
    sensitivity: 'medium',
    warningInterval: 15, // 秒
    aiAssist: true
  },
  eye: {
    enabled: true,
    distanceDetection: true,
    minDistance: 40, // 厘米
    breakInterval: 30, // 分钟
    breakDuration: 5 // 分钟
  },
  emotion: {
    enabled: true,
    detectionInterval: 5, // 分钟
    negativeAlert: true,
    aiAnalysis: true
  }
});

// 格式化时间间隔
const formatTimeInterval = (value) => {
  if (value < 60) {
    return `${value}秒`;
  } else if (value < 3600) {
    return `${Math.floor(value / 60)}分钟`;
  } else {
    const hours = Math.floor(value / 3600);
    const minutes = Math.floor((value % 3600) / 60);
    return `${hours}小时${minutes > 0 ? `${minutes}分钟` : ''}`;
  }
};

// 显示时间间隔选择器
const showTimeIntervalPicker = (type) => {
  let title = '';
  let options = [];
  let currentValue = 0;
  
  switch (type) {
    case 'posture':
      title = '不良姿势提醒间隔';
      options = [5, 10, 15, 30, 60].map(value => ({ text: `${value}秒`, value }));
      currentValue = settings.posture.warningInterval;
      break;
    case 'eye':
      title = '用眼休息提醒间隔';
      options = [20, 30, 45, 60, 90].map(value => ({ text: `${value}分钟`, value }));
      currentValue = settings.eye.breakInterval;
      break;
    case 'emotion':
      title = '情绪检测频率';
      options = [1, 3, 5, 10, 15].map(value => ({ text: `${value}分钟`, value }));
      currentValue = settings.emotion.detectionInterval;
      break;
  }
  
  showDialog({
    title,
    message: '请选择时间间隔：',
    showCancelButton: true
  }).then(() => {
    showToast('设置已更新');
  });
};

// 显示距离选择器
const showDistancePicker = () => {
  showDialog({
    title: '最小安全距离',
    message: '请选择最小安全距离（厘米）：',
    showCancelButton: true
  }).then(() => {
    showToast('设置已更新');
  });
};

// 显示休息时长选择器
const showBreakDurationPicker = () => {
  showDialog({
    title: '休息时长',
    message: '请选择休息时长（分钟）：',
    showCancelButton: true
  }).then(() => {
    showToast('设置已更新');
  });
};

// 跳转到提醒间隔设置页面
const goToReminderInterval = () => {
  router.push('/settings/reminder-interval')
};

// 保存设置
const saveSettings = () => {
  // 实际应用中应该调用API保存设置
  showToast('设置已保存');
};
</script>

<style scoped>
.sensitivity-selector {
  display: flex;
  gap: 8px;
}

.sensitivity-option {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  background-color: var(--border-color);
  color: var(--text-color);
  cursor: pointer;
}

.sensitivity-option.active {
  background-color: var(--primary-color);
  color: white;
}

.action-buttons {
  margin-top: 24px;
}
</style>
