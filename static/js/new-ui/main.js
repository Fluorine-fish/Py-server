/**
 * Main Application Script - Modern UI Framework
 * For Smart Working Environment Monitoring System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    initializeUI();
    
    // Set up periodic data refreshing
    setupDataRefresh();
    
    // Set up notifications
    setupNotifications();
});

// 全局变量
let monitorData = {
    postureQuality: null,
    sittingTime: 0,
    headAngle: 0,
    lastBreakTime: null
};

// 图表实例
let dailyStatsChart = null;
let postureTrendChart = null;
let sittingPatternChart = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    startMonitoring();
    setupEventListeners();
});

/**
 * Initialize all UI components
 */
function initializeUI() {
    // Setup system status indicators
    updateSystemStatus();
    
    // Initialize dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const menu = this.nextElementSibling;
            menu.classList.toggle('show');
            
            // Close other open dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                }
            });
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
    });
    
    // Initialize collapsible panels
    const collapsibles = document.querySelectorAll('.collapsible-header');
    collapsibles.forEach(header => {
        header.addEventListener('click', function() {
            this.parentElement.classList.toggle('collapsed');
            const content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
    
    // Add page-specific initializations based on current page
    const currentPage = getCurrentPage();
    switch (currentPage) {
        case 'posture':
            initializePosturePage();
            break;
        case 'emotion':
            initializeEmotionPage();
            break;
        case 'eyesight':
            initializeEyesightPage();
            break;
        case 'serial':
            initializeSerialPage();
            break;
        case 'settings':
            initializeSettingsPage();
            break;
    }
}

/**
 * Get current page based on URL
 * @returns {string} Current page identifier
 */
function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('posture')) return 'posture';
    if (path.includes('emotion')) return 'emotion';
    if (path.includes('eyesight')) return 'eyesight';
    if (path.includes('serial')) return 'serial';
    if (path.includes('settings')) return 'settings';
    return 'home';
}

/**
 * Set up periodic data refreshing
 */
function setupDataRefresh() {
    // Get system status every 30 seconds
    setInterval(updateSystemStatus, 30000);
    
    // Refresh page-specific data
    const currentPage = getCurrentPage();
    switch (currentPage) {
        case 'posture':
            setInterval(refreshPostureData, 1000);
            break;
        case 'emotion':
            setInterval(refreshEmotionData, 1000);
            break;
        case 'eyesight':
            setInterval(refreshEyesightData, 1000);
            break;
        case 'serial':
            // Serial page uses event-based updates
            break;
    }
}

/**
 * Update system status indicators
 */
function updateSystemStatus() {
    fetch('/api/get_system_info')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update CPU and memory indicators
                updateResourceMetrics(data.system_info);
                
                // Check version
                document.querySelectorAll('.system-version').forEach(el => {
                    el.textContent = data.system_info.version;
                });
            }
        })
        .catch(error => {
            console.error('Error fetching system status:', error);
        });
}

/**
 * Update CPU and memory usage indicators
 */
function updateResourceMetrics(systemInfo) {
    // Update CPU usage
    const cpuUsage = systemInfo.cpu_usage;
    const cpuElement = document.getElementById('cpuUsage');
    if (cpuElement) {
        cpuElement.textContent = `${cpuUsage}%`;
        updateMetricColor(cpuElement, cpuUsage);
    }
    
    // Update memory usage
    const memUsage = systemInfo.memory_usage.percent;
    const memElement = document.getElementById('memoryUsage');
    if (memElement) {
        memElement.textContent = `${memUsage}%`;
        updateMetricColor(memElement, memUsage);
    }
    
    // Update uptime
    const uptime = formatUptime(systemInfo.uptime);
    const uptimeElement = document.getElementById('systemUptime');
    if (uptimeElement) {
        uptimeElement.textContent = uptime;
    }
}

/**
 * Format uptime in a human-readable format
 */
function formatUptime(seconds) {
    const days = Math.floor(seconds / (24 * 60 * 60));
    seconds -= days * 24 * 60 * 60;
    const hours = Math.floor(seconds / (60 * 60));
    seconds -= hours * 60 * 60;
    const minutes = Math.floor(seconds / 60);
    
    let result = '';
    if (days > 0) result += `${days}天 `;
    if (hours > 0 || days > 0) result += `${hours}小时 `;
    result += `${minutes}分钟`;
    
    return result;
}

/**
 * Update color of a metric based on its value
 */
function updateMetricColor(element, value) {
    if (value > 90) {
        element.className = 'metric-value danger';
    } else if (value > 70) {
        element.className = 'metric-value warning';
    } else {
        element.className = 'metric-value normal';
    }
}

/**
 * Set up notification system
 */
function setupNotifications() {
    // Check for API error responses and display notifications
    window.addEventListener('apiError', function(e) {
        showNotification(e.detail.message, 'error');
    });
    
    // Handle custom events
    window.addEventListener('apiSuccess', function(e) {
        if (e.detail.showNotification) {
            showNotification(e.detail.message, 'success');
        }
    });
}

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 * @param {number} duration - How long to show the notification (ms)
 */
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notificationContainer') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Remove notification after duration
    setTimeout(() => {
        notification.classList.add('hiding');
        setTimeout(() => {
            container.removeChild(notification);
            if (container.children.length === 0) {
                document.body.removeChild(container);
            }
        }, 300);
    }, duration);
}

/**
 * Create notification container if it doesn't exist
 */
function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notificationContainer';
    container.className = 'notification-container';
    document.body.appendChild(container);
    return container;
}

/**
 * Helper function for API calls with consistent error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise} - Promise resolving to JSON response
 */
function apiCall(url, options = {}) {
    return fetch(url, options)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                const errorEvent = new CustomEvent('apiError', {
                    detail: {
                        message: data.message,
                        endpoint: url
                    }
                });
                window.dispatchEvent(errorEvent);
                return Promise.reject(data.message);
            }
            return data;
        })
        .catch(error => {
            console.error(`API Error (${url}):`, error);
            const errorEvent = new CustomEvent('apiError', {
                detail: {
                    message: typeof error === 'string' ? error : 'API请求失败，请重试',
                    endpoint: url
                }
            });
            window.dispatchEvent(errorEvent);
            return Promise.reject(error);
        });
}

// Page-specific initialization functions will be implemented separately

// 初始化图表
function initializeCharts() {
    // 初始化每日统计图表
    const dailyStatsCtx = document.getElementById('daily-stats-chart').getContext('2d');
    dailyStatsChart = new Chart(dailyStatsCtx, {
        type: 'doughnut',
        data: {
            labels: ['良好姿势', '轻微不良', '严重不良'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // 初始化姿势趋势图表
    const postureTrendCtx = document.getElementById('posture-trend-chart').getContext('2d');
    postureTrendChart = new Chart(postureTrendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '头部角度',
                data: [],
                borderColor: '#2196F3',
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 90
                }
            }
        }
    });

    // 初始化久坐模式图表
    const sittingPatternCtx = document.getElementById('sitting-pattern-chart').getContext('2d');
    sittingPatternChart = new Chart(sittingPatternCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '久坐时长',
                data: [],
                backgroundColor: '#2196F3'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 开始监控
function startMonitoring() {
    // 每秒更新一次监控数据
    setInterval(updateMonitorData, 1000);
    
    // 每分钟更新一次图表
    setInterval(updateCharts, 60000);
}

// 更新监控数据
async function updateMonitorData() {
    try {
        const response = await fetch('/api/monitor/status');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateUI(data.data);
            checkWarnings(data.data);
        }
    } catch (error) {
        console.error('获取监控数据失败:', error);
    }
}

// 更新UI显示
function updateUI(data) {
    // 更新状态显示
    document.getElementById('posture-status').textContent = getPostureStatusText(data.posture_status);
    document.getElementById('sitting-time').textContent = formatTime(data.sitting_time);
    document.getElementById('head-angle').textContent = `${Math.round(data.head_angle)}°`;
    
    // 更新姿势分析面板
    document.getElementById('posture-quality').textContent = getPostureStatusText(data.posture_status);
    document.getElementById('head-angle-value').textContent = `${Math.round(data.head_angle)}°`;
    
    // 更新久坐监控面板
    document.getElementById('current-sitting-time').textContent = formatTime(data.sitting_time);
    if (data.last_break_time) {
        document.getElementById('last-break-time').textContent = formatDateTime(data.last_break_time);
    }
    
    // 更新进度条
    const progressBar = document.getElementById('sitting-progress');
    const progress = (data.sitting_time / (30 * 60)) * 100; // 30分钟为标准
    progressBar.style.width = `${Math.min(progress, 100)}%`;
    progressBar.className = `progress ${progress >= 100 ? 'danger' : progress >= 80 ? 'warning' : ''}`;
}

// 检查警告
function checkWarnings(data) {
    if (data.posture_status === 'bad' || data.posture_status === 'severe') {
        showWarning('posture', '检测到不良姿势，请及时调整。');
    }
    
    if (data.sitting_time >= 30 * 60) { // 30分钟
        showWarning('sitting', '您已久坐30分钟，建议起身活动。');
    }
}

// 显示警告
function showWarning(type, message) {
    const alertsList = document.getElementById('alerts-list');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="time">${formatTime(new Date())}</span>
        <span class="message">${message}</span>
    `;
    
    alertsList.insertBefore(alert, alertsList.firstChild);
    
    // 最多显示10条记录
    if (alertsList.children.length > 10) {
        alertsList.removeChild(alertsList.lastChild);
    }
}

// 更新图表
function updateCharts() {
    // 更新姿势趋势图表
    if (monitorData.headAngle !== null) {
        const now = new Date();
        postureTrendChart.data.labels.push(formatTime(now));
        postureTrendChart.data.datasets[0].data.push(monitorData.headAngle);
        
        // 保持最近30个数据点
        if (postureTrendChart.data.labels.length > 30) {
            postureTrendChart.data.labels.shift();
            postureTrendChart.data.datasets[0].data.shift();
        }
        
        postureTrendChart.update();
    }
    
    // 更新每日统计图表
    if (dailyStatsChart) {
        dailyStatsChart.update();
    }
    
    // 更新久坐模式图表
    if (sittingPatternChart) {
        sittingPatternChart.update();
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 监控设置表单提交
    const settingsForm = document.getElementById('monitor-settings');
    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const settings = {
            head_angle_threshold: Number(document.getElementById('head-angle-threshold').value),
            posture_warning_cooldown: Number(document.getElementById('posture-warning-interval').value),
            sitting_threshold: Number(document.getElementById('sitting-threshold').value),
            enable_voice: document.getElementById('enable-voice').checked,
            enable_light: document.getElementById('enable-light').checked
        };
        
        try {
            const response = await fetch('/api/monitor/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                showNotification('设置已更新');
            } else {
                showNotification('更新设置失败', 'error');
            }
        } catch (error) {
            console.error('更新设置失败:', error);
            showNotification('更新设置失败', 'error');
        }
    });
    
    // 重置设置按钮
    document.getElementById('reset-settings').addEventListener('click', () => {
        document.getElementById('head-angle-threshold').value = 30;
        document.getElementById('posture-warning-interval').value = 60;
        document.getElementById('sitting-threshold').value = 30;
        document.getElementById('break-duration').value = 5;
        document.getElementById('enable-voice').checked = true;
        document.getElementById('enable-light').checked = true;
    });
}

// 工具函数
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}分${remainingSeconds}秒`;
}

function formatDateTime(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString('zh-CN', { hour12: false });
}

function getPostureStatusText(status) {
    const statusMap = {
        'good': '良好',
        'slightly_bad': '轻微不良',
        'bad': '不良',
        'severe': '严重不良',
        'unknown': '未检测到'
    };
    return statusMap[status] || '未知';
}

// 显示通知
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}