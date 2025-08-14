<template>
  <div class="mobile-page">
    <div class="page-heading">账户设置</div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">账户信息</div>
      </div>
      <div class="mobile-card-content">
        <div class="account-info">
          <div class="avatar-section">
            <div class="avatar">
              <i class="bi bi-person-circle"></i>
            </div>
            <div class="user-info">
              <div class="username">{{ userInfo.username }}</div>
              <div class="user-role">{{ userInfo.role }}</div>
            </div>
          </div>
          
          <div class="account-actions">
            <van-button size="small" plain>修改头像</van-button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">个人信息</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="用户名" :value="userInfo.username" is-link @click="showEditDialog('username')" />
          <van-cell title="手机号码" :value="formatPhone(userInfo.phone)" is-link @click="showEditDialog('phone')" />
          <van-cell title="邮箱地址" :value="userInfo.email" is-link @click="showEditDialog('email')" />
          <van-cell title="修改密码" is-link @click="showEditDialog('password')" />
        </van-cell-group>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">关联设备</div>
      </div>
      <div class="mobile-card-content">
        <div class="device-list">
          <div v-for="(device, index) in userInfo.devices" :key="index" class="device-item">
            <div class="device-icon">
              <i class="bi bi-lamp"></i>
            </div>
            <div class="device-info">
              <div class="device-name">{{ device.name }}</div>
              <div class="device-id">ID: {{ device.id }}</div>
            </div>
            <div class="device-actions">
              <i class="bi bi-three-dots-vertical" @click="showDeviceOptions(device)"></i>
            </div>
          </div>
          
          <van-button block type="primary" @click="showAddDeviceDialog">
            <i class="bi bi-plus-circle"></i>
            <span>添加设备</span>
          </van-button>
        </div>
      </div>
    </div>
    
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">账户安全</div>
      </div>
      <div class="mobile-card-content">
        <van-cell-group inset>
          <van-cell title="双因素认证" is-link>
            <template #right-icon>
              <van-switch v-model="userInfo.twoFactorAuth" size="24" />
            </template>
          </van-cell>
          <van-cell title="隐私设置" is-link @click="navigateTo('privacy')" />
          <van-cell title="清除缓存" is-link @click="clearCache" />
        </van-cell-group>
      </div>
    </div>
    
    <div class="action-buttons">
      <van-button block type="danger" @click="showLogoutConfirm">退出登录</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { showToast, showDialog } from 'vant';
import { useRouter } from 'vue-router';

const router = useRouter();

// 用户信息
const userInfo = reactive({
  username: '家长用户',
  role: '管理员',
  phone: '13800138000',
  email: 'parent@example.com',
  twoFactorAuth: false,
  devices: [
    { id: 'DL001', name: '曈灵台灯-主卧', status: 'online' },
    { id: 'DL002', name: '曈灵台灯-书房', status: 'offline' }
  ]
});

// 格式化手机号
const formatPhone = (phone) => {
  if (!phone) return '';
  return `${phone.substring(0, 3)}****${phone.substring(7)}`;
};

// 显示编辑对话框
const showEditDialog = (field) => {
  let title = '';
  let message = '';
  
  switch (field) {
    case 'username':
      title = '修改用户名';
      message = '请输入新的用户名';
      break;
    case 'phone':
      title = '修改手机号';
      message = '请输入新的手机号码';
      break;
    case 'email':
      title = '修改邮箱';
      message = '请输入新的邮箱地址';
      break;
    case 'password':
      title = '修改密码';
      message = '请输入当前密码和新密码';
      break;
  }
  
  showDialog({
    title,
    message,
    showCancelButton: true
  }).then(() => {
    showToast(`${title}功能即将上线`);
  });
};

// 显示设备选项
const showDeviceOptions = (device) => {
  showDialog({
    title: device.name,
    message: '请选择要执行的操作',
    showCancelButton: true,
    confirmButtonText: '重命名',
    cancelButtonText: '解除绑定'
  }).then(() => {
    showToast('重命名设备功能即将上线');
  }).catch(() => {
    showToast('解除绑定功能即将上线');
  });
};

// 显示添加设备对话框
const showAddDeviceDialog = () => {
  showDialog({
    title: '添加设备',
    message: '请输入设备ID或扫描设备上的二维码',
    showCancelButton: true
  }).then(() => {
    showToast('添加设备功能即将上线');
  });
};

// 导航到页面
const navigateTo = (page) => {
  showToast(`${page}页面功能即将上线`);
};

// 清除缓存
const clearCache = () => {
  showDialog({
    title: '清除缓存',
    message: '确定要清除应用缓存吗？',
    showCancelButton: true
  }).then(() => {
    showToast('缓存已清除');
  });
};

// 退出登录确认
const showLogoutConfirm = () => {
  showDialog({
    title: '退出登录',
    message: '确定要退出当前账号吗？',
    showCancelButton: true
  }).then(() => {
    showToast('退出登录成功');
    // 实际应用中应该调用登出API并清除用户会话
    setTimeout(() => {
      router.push('/login');
    }, 1000);
  });
};
</script>

<style scoped>
.account-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: var(--card-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar i {
  font-size: 48px;
  color: var(--primary-color);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 18px;
  font-weight: 600;
}

.user-role {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.account-actions {
  display: flex;
  justify-content: flex-end;
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.device-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.device-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.device-icon i {
  font-size: 20px;
  color: white;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 16px;
  font-weight: 500;
}

.device-id {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.device-actions {
  cursor: pointer;
  padding: 8px;
}

.action-buttons {
  margin-top: 24px;
}
</style>
