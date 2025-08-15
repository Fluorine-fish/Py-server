<template>
<!-- 这是一个样式组件，没有实际内容 -->
</template>

<script setup>
// 这个文件只是包含样式，没有脚本逻辑
</script>

<style scoped>
/* 坐姿检测页面样式 - 与主页面保持一致 */

/* 继承主页面的统一布局样式 */
.main-content-card {
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  margin-bottom: 0;
  padding: 0;
}

.unified-layout {
  display: flex;
  gap: 20px;
  margin-top: 16px;
  align-items: flex-end; /* 底部对齐 */
}

.video-stats-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* 内容底部对齐 */
}

.tools-section-unified {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 80px !important;
  min-width: 80px !important; /* 确保最小宽度 */
  max-width: 80px !important; /* 确保最大宽度 */
  flex-shrink: 0 !important; /* 防止被压缩 */
  flex-grow: 0 !important; /* 防止被拉伸 */
  justify-content: flex-end; /* 内容底部对齐 */
}

/* 时间段切换按钮组 */
.time-period-selector {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.period-btn {
  padding: 6px 12px;
  border: 1px solid rgba(116, 198, 157, 0.3);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
  color: #404F48;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}

.period-btn:hover {
  background: rgba(116, 198, 157, 0.1);
  border-color: #74c69d;
  transform: translateY(-1px);
}

.period-btn.active {
  background: linear-gradient(135deg, #3A8469 0%, #4a9c7a 100%);
  border-color: #3A8469;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(58, 132, 105, 0.3);
}

/* 饼图容器样式 - 按照图示风格 */
.chart-container-styled {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 280px;
  margin: 20px 0;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
}

#posturePieChart {
  max-width: 240px;
  max-height: 240px;
}

/* 图例网格布局 - 2行2列，完全按照截图 */
.chart-legend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
  margin: 20px 0;
  padding: 0 10px;
}

.legend-item-styled {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #3A8469 0%, #4a9c7a 100%);
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(58, 132, 105, 0.2);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-dot.good {
  background: #4CAF50;
}

.legend-dot.mild {
  background: #FFC107;
}

.legend-dot.moderate {
  background: #FF9800;
}

.legend-dot.severe {
  background: #F44336;
}

.legend-text-styled {
  font-size: 13px;
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 底部数据卡片 - 3个并排的蓝色数字卡片 */
.stats-cards-row {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding: 0 10px;
}

.stat-card {
  flex: 1;
  padding: 16px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-number-blue {
  font-size: 20px;
  font-weight: 700;
  color: #2196F3;
  margin-bottom: 6px;
  line-height: 1;
}

.stat-desc-gray {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* 统一的视频容器 */
.video-container-unified {
  position: relative;
  width: 100%;
  border-radius: var(--radius);
  overflow: hidden;
  aspect-ratio: 16/9;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #f0f4f3 0%, #e5f2ef 100%);
  border: 1px solid rgba(116, 198, 157, 0.2);
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius);
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.video-status {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(4px);
}

.posture-indicator {
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
  backdrop-filter: blur(4px);
}

.posture-indicator.status-good {
  background-color: rgba(16, 185, 129, 0.8);
}

.posture-indicator.status-warning {
  background-color: rgba(245, 158, 11, 0.8);
}

.posture-indicator.status-bad {
  background-color: rgba(239, 68, 68, 0.8);
}

/* 统一的统计数据样式 */
.stats-horizontal-unified {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: stretch; /* 确保所有项目高度一致 */
}

.stat-item-unified {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%);
  border-radius: var(--radius-small);
  border: 1px solid rgba(116, 198, 157, 0.2);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  justify-content: center; /* 内容垂直居中 */
  min-height: 60px; /* 确保最小高度 */
}

.stat-item-unified .stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.stat-item-unified .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

/* 统一的工具按钮样式 */
.tool-button-unified {
  display: flex !important;
  flex-direction: row !important; /* 改为水平排列 */
  align-items: center !important;
  justify-content: flex-start !important; /* 左对齐 */
  padding: 12px 16px; /* 调整内边距 */
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%);
  border-radius: var(--radius-small);
  border: 1px solid rgba(116, 198, 157, 0.2);
  cursor: pointer;
  transition: var(--transition);
  backdrop-filter: blur(8px);
  min-height: 70px !important;
  min-width: 60px !important;
  width: 100% !important;
  /* 重置button默认样式 */
  outline: none;
  font-family: inherit;
  box-sizing: border-box !important; /* 确保盒模型一致 */
  flex-shrink: 0 !important; /* 防止按钮被压缩 */
  gap: 12px; /* 图标和文字之间的间距 */
}

.tool-button-unified:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 250, 252, 0.9) 100%);
}

.tool-button-unified:active {
  transform: translateY(0);
}

.tool-button-unified:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(116, 198, 157, 0.3);
}

.tool-icon-unified {
  /* 使用圆角矩形，避免变形问题 */
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;
  max-width: 28px !important;
  max-height: 28px !important;
  
  /* 圆角矩形 - 不会变形 */
  border-radius: 8px !important;
  
  /* 布局 */
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  
  /* 防止变形 */
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  
  /* 盒模型 */
  box-sizing: border-box !important;
  padding: 0 !important;
  margin: 0 !important; /* 去掉下边距 */
  
  /* 背景和颜色 */
  background: #f8f9fa; /* 浅灰色背景，与底部标签栏一致 */
  color: #6c757d; /* 深灰色图标 */
  font-size: 16px; /* 增大图标字体 */
  
  /* 阴影效果让它更立体 */
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.2) !important;
}

.tool-text-unified {
  font-size: 14px; /* 适中的字体大小 */
  color: var(--color-text);
  font-weight: 600; /* 稍微减轻一点粗细 */
  text-align: left; /* 左对齐 */
  line-height: 1.2;
  flex: 1; /* 占据剩余空间 */
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 强制两行显示 */
  line-clamp: 2; /* 标准属性 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all; /* 强制换行 */
}

/* 工具区域标题样式 */
.tools-header {
  margin-bottom: 12px;
}

.tools-title {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin: 0;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.tools-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 不同功能按钮的背景色区分 */
.tool-analysis {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.05) 0%, rgba(156, 39, 176, 0.1) 100%);
  border: 1px solid rgba(156, 39, 176, 0.2);
}

.tool-posture {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.05) 0%, rgba(52, 152, 219, 0.1) 100%);
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.tool-gallery {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.05) 0%, rgba(46, 204, 113, 0.1) 100%);
  border: 1px solid rgba(46, 204, 113, 0.2);
}

.tool-reminder {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05) 0%, rgba(255, 193, 7, 0.1) 100%);
  border: 1px solid rgba(255, 193, 7, 0.2);
}

/* 对应的图标颜色 */
.tool-analysis .tool-icon-unified {
  background: rgba(156, 39, 176, 0.1) !important;
  color: #9c27b0 !important;
}

.tool-posture .tool-icon-unified {
  background: rgba(52, 152, 219, 0.1) !important;
  color: #3498db !important;
}

.tool-gallery .tool-icon-unified {
  background: rgba(46, 204, 113, 0.1) !important;
  color: #2ecc71 !important;
}

.tool-reminder .tool-icon-unified {
  background: rgba(255, 193, 7, 0.1) !important;
  color: #ffc107 !important;
}

/* 刷新按钮 */
.refresh-button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  color: white;
}

.refresh-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(180deg);
}

/* 时间范围选择器 */
.time-range-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 0 4px;
}

.time-range-btn {
  flex: 1;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(116, 198, 157, 0.3);
  border-radius: var(--radius-small);
  text-align: center;
  cursor: pointer;
  transition: var(--transition);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  backdrop-filter: blur(8px);
}

.time-range-btn.active {
  background: var(--gradient-green);
  color: white;
  border-color: transparent;
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.time-range-btn:hover:not(.active) {
  background: rgba(116, 198, 157, 0.1);
  border-color: rgba(116, 198, 157, 0.5);
}

/* Tab 导航样式 */
.posture-tabs-nav {
  display: flex;
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-small);
  padding: 4px;
  margin-bottom: 16px;
  border: 1px solid rgba(116, 198, 157, 0.2);
}

.posture-tab-btn {
  flex: 1;
  padding: 8px 12px;
  text-align: center;
  border-radius: var(--radius-small);
  cursor: pointer;
  transition: var(--transition);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.posture-tab-btn.active {
  background: var(--gradient-green);
  color: white;
  transform: translateY(-1px);
}

.posture-tab-btn:hover:not(.active) {
  background: rgba(116, 198, 157, 0.1);
  color: var(--color-text);
}

/* 图表容器 */
.chart-container {
  height: 220px;
  margin-bottom: 16px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-small);
  border: 1px solid rgba(116, 198, 157, 0.2);
}

/* 让 Chart.js 画布填满容器并可响应尺寸 */
.chart-container canvas,
#posturePieChart {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: var(--radius-small);
  border: 1px solid rgba(116, 198, 157, 0.2);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* 建议卡片样式 */
.improvement-suggestion .suggestion-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-small);
  border: 1px solid rgba(116, 198, 157, 0.2);
  margin-bottom: 12px;
}

.suggestion-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}

.suggestion-indicator.warning {
  background: var(--color-warning);
}

.suggestion-indicator.info {
  background: var(--color-info);
}

.suggestion-text {
  flex: 1;
  font-size: 14px;
  color: var(--color-text);
  line-height: 1.4;
}

/* 坐姿提醒样式 */
.posture-tips {
  margin-bottom: 16px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(116, 198, 157, 0.1);
}

.tip-item:last-child {
  border-bottom: none;
}

.tip-item i {
  color: var(--color-success);
  font-size: 16px;
}

.tip-item span {
  flex: 1;
  font-size: 14px;
  color: var(--color-text);
}

/* 按钮样式 */
.reminder-button {
  background: var(--gradient-green) !important;
  border: none !important;
  border-radius: var(--radius-small) !important;
  padding: 12px !important;
  font-weight: 600 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
}

/* 图像网格 */
.mobile-image-gallery {
  margin-bottom: 16px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.image-item {
  position: relative;
  aspect-ratio: 4/3;
  border-radius: var(--radius-small);
  overflow: hidden;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(116, 198, 157, 0.2);
}

.posture-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.image-status.status-good {
  color: var(--color-success);
}

.image-status.status-warning {
  color: var(--color-warning);
}

.image-status.status-bad {
  color: var(--color-danger);
}

/* 加载和空状态 */
.loading-indicator,
.no-records {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--color-text-secondary);
  gap: 8px;
}

.loading-indicator i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 图例 */
.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.low {
  background: var(--color-success);
}

.legend-color.medium {
  background: var(--color-warning);
}

.legend-color.high {
  background: var(--color-danger);
}

/* 图像操作按钮 */
.image-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

/* 响应式优化 */
@media (max-width: 480px) {
  .unified-layout {
    flex-direction: column;
    gap: 16px;
  }
  
  .tools-section-unified {
    flex-direction: column !important; /* 在小屏幕上改为垂直排列 */
    width: 100% !important;
    max-width: 100% !important;
    gap: 12px;
  }
  
  .tools-header {
    margin-bottom: 8px;
  }
  
  .tools-title {
    font-size: 13px;
    padding-bottom: 6px;
  }
  
  .tools-list {
    gap: 6px;
  }
  
  .tool-button-unified {
    min-height: 60px !important;
    padding: 12px 16px;
    min-width: 100% !important;
    flex: none !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    flex-direction: row !important; /* 保持水平排列 */
    justify-content: flex-start !important;
    gap: 12px;
  }

  .tool-icon-unified {
    /* 响应式下的圆角矩形 */
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    max-width: 24px !important;
    max-height: 24px !important;
    
    /* 圆角矩形 - 不会变形 */
    border-radius: 6px !important;
    
    /* 布局 */
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    
    /* 防止变形 */
    flex-shrink: 0 !important;
    flex-grow: 0 !important;
    
    /* 盒模型 */
    box-sizing: border-box !important;
    padding: 0 !important;
    margin: 0 !important; /* 去掉边距 */
    
    /* 字体 */
    font-size: 14px; /* 响应式下的图标字体 */
    
    /* 阴影效果 */
    box-shadow: 0 1px 3px rgba(58, 132, 105, 0.2) !important;
  }
  
  .tool-text-unified {
    font-size: 12px; /* 响应式下的文字字体 */
    font-weight: 600; /* 保持适中粗细 */
    text-align: left;
    display: -webkit-box;
    -webkit-line-clamp: 2; /* 强制两行显示 */
    line-clamp: 2; /* 标准属性 */
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: break-all; /* 强制换行 */
    flex: 1;
  }
  
  .stats-horizontal-unified {
    flex-wrap: wrap;
  }
  
  .stat-item-unified {
    min-width: 80px;
  }
}

/* 圆角矩形图标保护规则 */
.tool-icon-unified, 
.tool-icon-unified::before, 
.tool-icon-unified::after {
  border-radius: 8px !important;
}

/* 覆盖任何可能的继承样式 */
.tools-section-unified .tool-button-unified .tool-icon-unified {
  width: 28px !important;
  height: 28px !important;
  border-radius: 8px !important;
  display: inline-flex !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.2) !important;
}

/* 具体按钮的图标颜色覆盖 */
.tools-section-unified .tool-analysis .tool-icon-unified {
  background: rgba(156, 39, 176, 0.1) !important;
  color: #9c27b0 !important;
}

.tools-section-unified .tool-posture .tool-icon-unified {
  background: rgba(52, 152, 219, 0.1) !important;
  color: #3498db !important;
}

.tools-section-unified .tool-gallery .tool-icon-unified {
  background: rgba(46, 204, 113, 0.1) !important;
  color: #2ecc71 !important;
}

.tools-section-unified .tool-reminder .tool-icon-unified {
  background: rgba(255, 193, 7, 0.1) !important;
  color: #ffc107 !important;
}

/* 响应式下的覆盖 */
@media (max-width: 480px) {
  .tool-icon-unified, 
  .tool-icon-unified::before, 
  .tool-icon-unified::after {
    border-radius: 6px !important;
  }
  
  .tools-section-unified .tool-button-unified .tool-icon-unified {
    width: 24px !important;
    height: 24px !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 3px rgba(108, 117, 125, 0.2) !important;
  }
  
  /* 响应式下具体按钮的图标颜色 */
  .tools-section-unified .tool-analysis .tool-icon-unified {
    background: rgba(156, 39, 176, 0.1) !important;
    color: #9c27b0 !important;
  }

  .tools-section-unified .tool-posture .tool-icon-unified {
    background: rgba(52, 152, 219, 0.1) !important;
    color: #3498db !important;
  }

  .tools-section-unified .tool-gallery .tool-icon-unified {
    background: rgba(46, 204, 113, 0.1) !important;
    color: #2ecc71 !important;
  }

  .tools-section-unified .tool-reminder .tool-icon-unified {
    background: rgba(255, 193, 7, 0.1) !important;
    color: #ffc107 !important;
  }
}
</style>
