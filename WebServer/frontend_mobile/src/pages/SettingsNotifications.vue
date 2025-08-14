<template>
  <div class="mobile-page">
    <div class="page-heading">通知设置</div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">通知渠道</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="应用内通知">
            <template #right-icon>
              <van-switch v-model="settings.channels.app" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="短信通知">
            <template #right-icon>
              <van-switch v-model="settings.channels.sms" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="电子邮件通知">
            <template #right-icon>
              <van-switch v-model="settings.channels.email" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="语音提醒">
            <template #right-icon>
              <van-switch v-model="settings.channels.voice" size="24" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">通知类型</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="坐姿异常">
            <template #right-icon>
              <van-switch v-model="settings.types.posture" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="用眼距离不足">
            <template #right-icon>
              <van-switch v-model="settings.types.eyeDistance" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="用眼休息提醒">
            <template #right-icon>
              <van-switch v-model="settings.types.eyeBreak" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="负面情绪提醒">
            <template #right-icon>
              <van-switch v-model="settings.types.negativeEmotion" size="24" />
            </template>
          </van-cell>
          
          <van-cell title="设备状态变化">
            <template #right-icon>
              <van-switch v-model="settings.types.deviceStatus" size="24" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">通知频率</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="勿扰时段">
            <template #right-icon>
              <van-switch v-model="settings.frequency.doNotDisturb.enabled" size="24" />
            </template>
          </van-cell>
          
          <van-cell v-if="settings.frequency.doNotDisturb.enabled" title="开始时间" is-link @click="showTimePicker('start')">
            <template #value>
              <span>{{ settings.frequency.doNotDisturb.start }}</span>
            </template>
          </van-cell>
          
          <van-cell v-if="settings.frequency.doNotDisturb.enabled" title="结束时间" is-link @click="showTimePicker('end')">
            <template #value>
              <span>{{ settings.frequency.doNotDisturb.end }}</span>
            </template>
          </van-cell>
          
          <van-cell title="最小通知间隔" is-link @click="showIntervalPicker">
            <template #value>
              <span>{{ formatMinutes(settings.frequency.minInterval) }}</span>
            </template>
          </van-cell>
          
          <van-cell title="同类型通知限制" is-link @click="showLimitPicker">
            <template #value>
              <span>每{{ formatHours(settings.frequency.sameTypeLimit.hours) }}不超过{{ settings.frequency.sameTypeLimit.count }}次</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">紧急联系人</div>
      </div>
      <div class="mobile-card-content">
        <div class="contact-list">
          <div v-for="(contact, index) in settings.emergencyContacts" :key="index" class="contact-item">
            <div class="contact-icon">
              <i class="bi bi-person"></i>
            </div>
            <div class="contact-info">
              <div class="contact-name">{{ contact.name }}</div>
              <div class="contact-relation">{{ contact.relation }}</div>
              <div class="contact-phone">{{ contact.phone }}</div>
            </div>
            <div class="contact-actions">
              <i class="bi bi-pencil-square" @click="editContact(index)"></i>
              <i class="bi bi-trash" @click="deleteContact(index)"></i>
            </div>
          </div>
          
          <van-button block plain type="primary" @click="showAddContactDialog">
            <i class="bi bi-plus"></i>
            <span>添加紧急联系人</span>
          </van-button>
        </div>
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

// 通知设置
const settings = reactive({
  channels: {
    app: true,
    sms: true,
    email: false,
    voice: false
  },
  types: {
    posture: true,
    eyeDistance: true,
    eyeBreak: true,
    negativeEmotion: true,
    deviceStatus: false
  },
  frequency: {
    doNotDisturb: {
      enabled: false,
      start: '22:00',
      end: '07:00'
    },
    minInterval: 15, // 分钟
    sameTypeLimit: {
      hours: 3,
      count: 5
    }
  },
  emergencyContacts: [
    {
      name: '张三',
      relation: '父亲',
      phone: '13812345678'
    },
    {
      name: '李四',
      relation: '母亲',
      phone: '13987654321'
    }
  ]
});

// 格式化分钟数
const formatMinutes = (minutes) => {
  if (minutes < 60) {
    return `${minutes}分钟`;
  } else {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}小时${mins > 0 ? `${mins}分钟` : ''}`;
  }
};

// 格式化小时数
const formatHours = (hours) => {
  return `${hours}小时`;
};

// 显示时间选择器
const showTimePicker = (type) => {
  showDialog({
    title: type === 'start' ? '设置开始时间' : '设置结束时间',
    message: '请选择时间：',
    showCancelButton: true
  }).then(() => {
    showToast('时间已更新');
  });
};

// 显示间隔选择器
const showIntervalPicker = () => {
  showDialog({
    title: '最小通知间隔',
    message: '请选择最小通知间隔：',
    showCancelButton: true
  }).then(() => {
    showToast('间隔已更新');
  });
};

// 显示限制选择器
const showLimitPicker = () => {
  showDialog({
    title: '同类型通知限制',
    message: '请设置同类型通知限制：',
    showCancelButton: true
  }).then(() => {
    showToast('限制已更新');
  });
};

// 编辑联系人
const editContact = (index) => {
  showDialog({
    title: '编辑联系人',
    message: '请修改联系人信息：',
    showCancelButton: true
  }).then(() => {
    showToast('联系人已更新');
  });
};

// 删除联系人
const deleteContact = (index) => {
  showDialog({
    title: '删除联系人',
    message: '确定要删除此联系人吗？',
    showCancelButton: true
  }).then(() => {
    settings.emergencyContacts.splice(index, 1);
    showToast('联系人已删除');
  });
};

// 显示添加联系人对话框
const showAddContactDialog = () => {
  showDialog({
    title: '添加紧急联系人',
    message: '请输入联系人信息：',
    showCancelButton: true
  }).then(() => {
    showToast('联系人已添加');
  });
};

// 保存设置
const saveSettings = () => {
  // 实际应用中应该调用API保存设置
  showToast('通知设置已保存');
};
</script>

<style scoped>
.contact-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.contact-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.contact-icon i {
  font-size: 20px;
  color: white;
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-size: 16px;
  font-weight: 500;
}

.contact-relation {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.contact-phone {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.contact-actions {
  display: flex;
  gap: 16px;
}

.contact-actions i {
  cursor: pointer;
  padding: 8px;
}

.action-buttons {
  margin-top: 24px;
}
</style>
