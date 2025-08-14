<template>
  <div class="mobile-page">
    <div class="page-heading">系统设置</div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">系统信息</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="当前版本">
            <template #value>
              <span>v{{ systemInfo.version }}</span>
            </template>
          </van-cell>
          
          <van-cell title="系统类型">
            <template #value>
              <span>{{ systemInfo.platform }}</span>
            </template>
          </van-cell>
          
          <van-cell title="存储空间">
            <template #value>
              <span>{{ formatStorage(systemInfo.storage) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="设备ID">
            <template #value>
              <span>{{ systemInfo.deviceId }}</span>
            </template>
          </van-cell>
          
          <van-cell title="最近更新">
            <template #value>
              <span>{{ systemInfo.lastUpdate }}</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">系统偏好</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="显示主题">
            <template #right-icon>
              <div class="theme-selector">
                <div 
                  v-for="theme in themes" 
                  :key="theme.value"
                  :class="['theme-option', settings.theme === theme.value ? 'active' : '']"
                  @click="changeTheme(theme.value)"
                >
                  {{ theme.label }}
                </div>
              </div>
            </template>
          </van-cell>
          
          <van-cell title="语言" is-link @click="showLanguagePicker">
            <template #value>
              <span>{{ getLanguageName(settings.language) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="字体大小" is-link @click="showFontSizePicker">
            <template #value>
              <span>{{ getFontSizeName(settings.fontSize) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="音效">
            <template #right-icon>
              <van-switch v-model="settings.soundEffects" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="震动">
            <template #right-icon>
              <van-switch v-model="settings.vibration" size="24" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">网络设置</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="使用Wi-Fi下自动更新">
            <template #right-icon>
              <van-switch v-model="settings.network.autoUpdateOnWifi" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="使用低流量模式">
            <template #right-icon>
              <van-switch v-model="settings.network.lowDataMode" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="更新检查频率" is-link @click="showUpdateFrequencyPicker">
            <template #value>
              <span>{{ getUpdateFrequencyName(settings.network.updateFrequency) }}</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">高级选项</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="调试模式">
            <template #right-icon>
              <van-switch v-model="settings.advanced.debugMode" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="数据导出" is-link @click="exportData" />
          <van-cell title="重置所有设置" is-link @click="showResetConfirm" />
          <van-cell title="检查更新" is-link @click="checkForUpdates" />
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">关于</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="用户协议" is-link @click="openPage('terms')" />
          <van-cell title="隐私政策" is-link @click="openPage('privacy')" />
          <van-cell title="开源许可" is-link @click="openPage('licenses')" />
          <van-cell title="反馈问题" is-link @click="openPage('feedback')" />
          <van-cell title="联系我们" is-link @click="openPage('contact')" />
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

// 系统信息
const systemInfo = reactive({
  version: '1.2.3',
  platform: 'Android',
  storage: 512 * 1024 * 1024, // 512MB
  deviceId: 'ML-2023-001-XYZ',
  lastUpdate: '2023-06-15'
});

// 主题选项
const themes = [
  { value: 'light', label: '浅色' },
  { value: 'dark', label: '深色' },
  { value: 'auto', label: '自动' }
];

// 系统设置
const settings = reactive({
  theme: 'dark',
  language: 'zh_CN',
  fontSize: 'medium',
  soundEffects: true,
  vibration: true,
  network: {
    autoUpdateOnWifi: true,
    lowDataMode: false,
    updateFrequency: 'weekly'
  },
  advanced: {
    debugMode: false
  }
});

// 格式化存储空间
const formatStorage = (bytes) => {
  if (bytes < 1024) {
    return `${bytes}B`;
  } else if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(2)}KB`;
  } else if (bytes < 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
  } else {
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`;
  }
};

// 获取语言名称
const getLanguageName = (code) => {
  const languages = {
    zh_CN: '简体中文',
    en_US: 'English',
    zh_TW: '繁体中文',
    ja_JP: '日本語'
  };
  
  return languages[code] || code;
};

// 获取字体大小名称
const getFontSizeName = (size) => {
  const sizes = {
    small: '小',
    medium: '中',
    large: '大',
    xlarge: '超大'
  };
  
  return sizes[size] || size;
};

// 获取更新频率名称
const getUpdateFrequencyName = (frequency) => {
  const frequencies = {
    daily: '每天',
    weekly: '每周',
    monthly: '每月',
    never: '从不'
  };
  
  return frequencies[frequency] || frequency;
};

// 切换主题
const changeTheme = (theme) => {
  settings.theme = theme;
  showToast(`已切换至${themes.find(t => t.value === theme).label}主题`);
  // 实际应用中应该调用主题切换函数
};

// 显示语言选择器
const showLanguagePicker = () => {
  showDialog({
    title: '选择语言',
    message: '请选择您的语言：',
    showCancelButton: true
  }).then(() => {
    showToast('语言已更新');
  });
};

// 显示字体大小选择器
const showFontSizePicker = () => {
  showDialog({
    title: '选择字体大小',
    message: '请选择您喜欢的字体大小：',
    showCancelButton: true
  }).then(() => {
    showToast('字体大小已更新');
  });
};

// 显示更新频率选择器
const showUpdateFrequencyPicker = () => {
  showDialog({
    title: '选择更新频率',
    message: '请选择应用更新检查频率：',
    showCancelButton: true
  }).then(() => {
    showToast('更新频率已更新');
  });
};

// 导出数据
const exportData = () => {
  showDialog({
    title: '导出数据',
    message: '您想导出哪些数据？',
    showCancelButton: true
  }).then(() => {
    showToast('导出功能即将上线');
  });
};

// 显示重置确认
const showResetConfirm = () => {
  showDialog({
    title: '重置所有设置',
    message: '确定要将所有设置恢复为默认值吗？此操作无法撤销。',
    showCancelButton: true
  }).then(() => {
    // 实际应用中应该重置所有设置
    showToast('所有设置已重置为默认值');
  });
};

// 检查更新
const checkForUpdates = () => {
  showToast({
    message: '正在检查更新...',
    duration: 1000,
    onClose: () => {
      showToast('当前已是最新版本');
    }
  });
};

// 打开页面
const openPage = (page) => {
  const pages = {
    terms: '用户协议',
    privacy: '隐私政策',
    licenses: '开源许可',
    feedback: '反馈问题',
    contact: '联系我们'
  };
  
  showToast(`${pages[page]}功能即将上线`);
};

// 保存设置
const saveSettings = () => {
  // 实际应用中应该调用API保存设置
  showToast('系统设置已保存');
};
</script>

<style scoped>
.theme-selector {
  display: flex;
  gap: 8px;
}

.theme-option {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  background-color: var(--border-color);
  color: var(--text-color);
  cursor: pointer;
}

.theme-option.active {
  background-color: var(--primary-color);
  color: white;
}

.action-buttons {
  margin-top: 24px;
  margin-bottom: 32px;
}
</style>
