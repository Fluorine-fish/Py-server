<template>
  <div class="mobile-page">
    <div class="page-heading">设置</div>
    
    <!-- 设置列表 -->
    <div class="mobile-card">
      <div class="settings-list">
        <!-- 账号设置 -->
        <router-link to="/settings/account" class="settings-item">
          <div class="settings-icon">
            <i class="bi bi-person-circle"></i>
          </div>
          <div class="settings-info">
            <div class="settings-title">账号设置</div>
            <div class="settings-desc">个人信息、密码、隐私</div>
          </div>
          <i class="bi bi-chevron-right settings-arrow"></i>
        </router-link>
        
        <!-- 监护设置 -->
        <router-link to="/settings/monitor" class="settings-item">
          <div class="settings-icon">
            <i class="bi bi-shield-check"></i>
          </div>
          <div class="settings-info">
            <div class="settings-title">监护设置</div>
            <div class="settings-desc">坐姿检测、用眼监护、智能提醒</div>
          </div>
          <i class="bi bi-chevron-right settings-arrow"></i>
        </router-link>
        
        <!-- 通知设置 -->
        <router-link to="/settings/notifications" class="settings-item">
          <div class="settings-icon">
            <i class="bi bi-bell"></i>
          </div>
          <div class="settings-info">
            <div class="settings-title">通知设置</div>
            <div class="settings-desc">提醒方式、免打扰时段</div>
          </div>
          <i class="bi bi-chevron-right settings-arrow"></i>
        </router-link>
        
        <!-- 系统设置 -->
        <router-link to="/settings/system" class="settings-item">
          <div class="settings-icon">
            <i class="bi bi-gear"></i>
          </div>
          <div class="settings-info">
            <div class="settings-title">系统设置</div>
            <div class="settings-desc">网络、存储、固件升级</div>
          </div>
          <i class="bi bi-chevron-right settings-arrow"></i>
        </router-link>
      </div>
    </div>
    
    <!-- 设备信息 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">设备信息</div>
      </div>
      <div class="mobile-card-content">
        <div class="device-info-list">
          <div class="device-info-item">
            <div class="info-label">设备名称</div>
            <div class="info-value">曈灵智能台灯 Pro</div>
          </div>
          <div class="device-info-item">
            <div class="info-label">设备型号</div>
            <div class="info-value">TL-2023</div>
          </div>
          <div class="device-info-item">
            <div class="info-label">固件版本</div>
            <div class="info-value">2.5.7</div>
          </div>
          <div class="device-info-item">
            <div class="info-label">序列号</div>
            <div class="info-value">TL20230612A5B8C3</div>
          </div>
          <div class="device-info-item">
            <div class="info-label">绑定日期</div>
            <div class="info-value">2024-05-20</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 应用信息 -->
    <div class="mobile-card">
      <div class="mobile-card-header">
        <div class="mobile-card-title">应用信息</div>
      </div>
      <div class="mobile-card-content">
        <div class="app-info-list">
          <div class="device-info-item">
            <div class="info-label">应用版本</div>
            <div class="info-value">3.1.4</div>
          </div>
          <div class="device-info-item">
            <div class="info-label">存储空间</div>
            <div class="info-value">28.5MB</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <van-button block plain type="primary" class="action-button" @click="checkUpdate">
        <i class="bi bi-arrow-repeat"></i>
        <span>检查更新</span>
      </van-button>
      
      <van-button block plain type="primary" class="action-button" @click="gotoHelp">
        <i class="bi bi-question-circle"></i>
        <span>帮助中心</span>
      </van-button>
      
      <van-button block plain type="primary" class="action-button" @click="contactSupport">
        <i class="bi bi-headset"></i>
        <span>联系客服</span>
      </van-button>
      
      <van-button block plain type="danger" class="action-button logout-button" @click="confirmLogout">
        <i class="bi bi-box-arrow-right"></i>
        <span>退出登录</span>
      </van-button>
    </div>
    
    <!-- 页脚 -->
    <div class="app-footer">
      <div class="app-copyright">© 2025 曈灵科技</div>
      <div class="app-version">v3.1.4</div>
    </div>
    
    <!-- 退出登录确认弹窗 -->
    <van-dialog
      v-model:show="showLogoutDialog"
      title="确认退出"
      message="确定要退出登录吗？"
      show-cancel-button
      @confirm="logout"
    />
    
    <!-- 操作反馈 -->
    <van-toast id="toast" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Toast } from 'vant';

// 退出登录对话框
const showLogoutDialog = ref(false);

// 检查更新
const checkUpdate = () => {
  Toast('正在检查更新...');
  setTimeout(() => {
    Toast.success('当前已是最新版本');
  }, 1500);
};

// 帮助中心
const gotoHelp = () => {
  Toast('跳转至帮助中心...');
};

// 联系客服
const contactSupport = () => {
  Toast('正在连接客服系统...');
};

// 确认退出
const confirmLogout = () => {
  showLogoutDialog.value = true;
};

// 退出登录
const logout = () => {
  Toast.success('已退出登录');
  setTimeout(() => {
    // 实际应用中，这里应该有清除登录状态的逻辑
    window.location.href = '/mobile/login';
  }, 1000);
};
</script>

<style scoped>
.page-heading {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.settings-list {
  padding: 0 8px;
}

.settings-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--color-border);
  text-decoration: none;
  color: var(--color-text);
}

.settings-item:last-child {
  border-bottom: none;
}

.settings-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 16px;
}

.settings-info {
  flex: 1;
}

.settings-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.settings-desc {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.settings-arrow {
  color: var(--color-text-tertiary);
}

.device-info-list,
.app-info-list {
  padding: 8px;
}

.device-info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}

.device-info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--color-text-secondary);
}

.info-value {
  font-weight: 500;
}

.action-buttons {
  margin: 24px 0;
}

.action-button {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.logout-button {
  margin-top: 12px;
}

.app-footer {
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 12px;
  margin: 24px 0;
}

.app-copyright {
  margin-bottom: 4px;
}
</style>
