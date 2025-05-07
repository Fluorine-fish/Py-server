/**
 * 家长监控面板功能模块
 * 提供学习状态监控、数据可视化和报告生成功能
 */

// 全局变量
let postureChart = null;
let emotionChart = null;
let focusChart = null;
let monitoringStartTime = null;
let dashboardDataInterval = null;

// 监测数据存储
const monitoringData = {
    posture: {
        labels: [],
        good: [],
        poor: [],
        unknown: []
    },
    emotion: {
        labels: [],
        positive: [],
        neutral: [],
        negative: []
    },
    focus: {
        labels: [],
        focused: [],
        distracted: []
    }
};

// 初始化函数
document.addEventListener('DOMContentLoaded', function() {
    // 仅在有dashboard标签页时执行初始化
    if (document.getElementById('dashboardTab')) {
        initCharts();
        setupDashboardControls();
    }
});

// 初始化图表
function initCharts() {
    // 初始化姿势监测图表
    const postureCtx = document.getElementById('postureChart').getContext('2d');
    postureChart = new Chart(postureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '良好姿势',
                    data: [],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    tension: 0.3
                },
                {
                    label: '不良姿势',
                    data: [],
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '姿势状态监测'
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: '百分比 (%)'
                    }
                }
            }
        }
    });

    // 初始化情绪监测图表
    const emotionCtx = document.getElementById('emotionChart').getContext('2d');
    emotionChart = new Chart(emotionCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '积极情绪',
                    data: [],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    tension: 0.3
                },
                {
                    label: '中性情绪',
                    data: [],
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                    tension: 0.3
                },
                {
                    label: '消极情绪',
                    data: [],
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '情绪状态监测'
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: '百分比 (%)'
                    }
                }
            }
        }
    });

    // 初始化专注度监测图表
    const focusCtx = document.getElementById('focusChart').getContext('2d');
    focusChart = new Chart(focusCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '专注状态',
                    data: [],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '专注度监测'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: '专注度 (%)'
                    }
                }
            }
        }
    });
}

// 设置控制面板事件监听
function setupDashboardControls() {
    // 启动分析按钮
    const startBtn = document.getElementById('dashStartAnalysisBtn');
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            startMonitoring();
        });
    }

    // 停止分析按钮
    const stopBtn = document.getElementById('dashStopAnalysisBtn');
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            stopMonitoring();
        });
    }

    // 同步主面板系统状态
    const mainStatusSpan = document.getElementById('systemStatusText');
    const dashStatusSpan = document.getElementById('dashSystemStatusText');
    
    if (mainStatusSpan && dashStatusSpan) {
        // 初始同步
        dashStatusSpan.textContent = mainStatusSpan.textContent;
        if (mainStatusSpan.textContent.includes('运行中')) {
            dashStatusSpan.className = 'status-running';
            monitoringStartTime = new Date();
            startDataCollection();
        } else {
            dashStatusSpan.className = 'status-stopped';
        }
        
        // 创建一个MutationObserver来监听主状态的变化
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'characterData' || mutation.type === 'childList') {
                    dashStatusSpan.textContent = mainStatusSpan.textContent;
                    
                    if (mainStatusSpan.textContent.includes('运行中')) {
                        dashStatusSpan.className = 'status-running';
                    } else {
                        dashStatusSpan.className = 'status-stopped';
                    }
                }
            });
        });
        
        // 配置观察选项
        const config = { characterData: true, childList: true, subtree: true };
        
        // 开始观察
        observer.observe(mainStatusSpan, config);
    }
}

// 启动监控
function startMonitoring() {
    // 同步启动主页面的分析系统
    const mainStartBtn = document.getElementById('startAnalysisBtn');
    if (mainStartBtn) {
        mainStartBtn.click();
    }
    
    monitoringStartTime = new Date();
    document.getElementById('dashStartTime').textContent = formatDate(monitoringStartTime);
    
    // 启动数据收集
    startDataCollection();
}

// 停止监控
function stopMonitoring() {
    // 同步停止主页面的分析系统
    const mainStopBtn = document.getElementById('stopAnalysisBtn');
    if (mainStopBtn) {
        mainStopBtn.click();
    }
    
    // 停止数据收集
    if (dashboardDataInterval) {
        clearInterval(dashboardDataInterval);
        dashboardDataInterval = null;
    }
}

// 启动数据收集
function startDataCollection() {
    if (dashboardDataInterval) {
        clearInterval(dashboardDataInterval);
    }
    
    // 每10秒更新一次图表数据
    dashboardDataInterval = setInterval(fetchAndUpdateData, 10000);
    
    // 立即获取一次数据
    fetchAndUpdateData();
}

// 获取并更新数据
function fetchAndUpdateData() {
    // 获取当前姿势和情绪状态
    updateRealTimeStatus();
    
    // 获取分析数据并更新图表
    fetch('/api/dashboard/data')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateCharts(data);
            }
        })
        .catch(error => {
            console.error('获取监控数据失败:', error);
        });
}

// 更新实时状态显示
function updateRealTimeStatus() {
    // 从主页面获取状态并同步到仪表盘
    const headAngle = document.getElementById('headAngle').textContent;
    const postureStatus = document.getElementById('postureStatus').textContent;
    const emotionStatus = document.getElementById('emotionStatus').textContent;
    const detectionStatus = document.getElementById('detectionStatus').textContent;
    
    document.getElementById('dashHeadAngle').textContent = headAngle;
    document.getElementById('dashPostureStatus').textContent = postureStatus;
    document.getElementById('dashEmotionStatus').textContent = emotionStatus;
    document.getElementById('dashDetectionStatus').textContent = detectionStatus;
}

// 更新图表数据
function updateCharts(data) {
    // 时间标签
    const timeLabel = formatTime(new Date());
    
    // 更新姿势数据
    updatePostureChart(timeLabel, data.posture);
    
    // 更新情绪数据
    updateEmotionChart(timeLabel, data.emotion);
    
    // 更新专注度数据
    updateFocusChart(timeLabel, data.focus);
}

// 更新姿势图表
function updatePostureChart(timeLabel, postureData) {
    // 限制数据点数量，保持最新的10个点
    if (monitoringData.posture.labels.length >= 10) {
        monitoringData.posture.labels.shift();
        monitoringData.posture.good.shift();
        monitoringData.posture.poor.shift();
    }
    
    // 添加新数据点
    monitoringData.posture.labels.push(timeLabel);
    monitoringData.posture.good.push(postureData.good_percentage);
    monitoringData.posture.poor.push(postureData.poor_percentage);
    
    // 更新图表
    postureChart.data.labels = monitoringData.posture.labels;
    postureChart.data.datasets[0].data = monitoringData.posture.good;
    postureChart.data.datasets[1].data = monitoringData.posture.poor;
    postureChart.update();
}

// 更新情绪图表
function updateEmotionChart(timeLabel, emotionData) {
    // 限制数据点数量，保持最新的10个点
    if (monitoringData.emotion.labels.length >= 10) {
        monitoringData.emotion.labels.shift();
        monitoringData.emotion.positive.shift();
        monitoringData.emotion.neutral.shift();
        monitoringData.emotion.negative.shift();
    }
    
    // 添加新数据点
    monitoringData.emotion.labels.push(timeLabel);
    monitoringData.emotion.positive.push(emotionData.positive_percentage);
    monitoringData.emotion.neutral.push(emotionData.neutral_percentage);
    monitoringData.emotion.negative.push(emotionData.negative_percentage);
    
    // 更新图表
    emotionChart.data.labels = monitoringData.emotion.labels;
    emotionChart.data.datasets[0].data = monitoringData.emotion.positive;
    emotionChart.data.datasets[1].data = monitoringData.emotion.neutral;
    emotionChart.data.datasets[2].data = monitoringData.emotion.negative;
    emotionChart.update();
}

// 更新专注度图表
function updateFocusChart(timeLabel, focusData) {
    // 限制数据点数量，保持最新的10个点
    if (monitoringData.focus.labels.length >= 10) {
        monitoringData.focus.labels.shift();
        monitoringData.focus.focused.shift();
    }
    
    // 添加新数据点
    monitoringData.focus.labels.push(timeLabel);
    monitoringData.focus.focused.push(focusData.focus_percentage);
    
    // 更新图表
    focusChart.data.labels = monitoringData.focus.labels;
    focusChart.data.datasets[0].data = monitoringData.focus.focused;
    focusChart.update();
}

// 生成报告
function generateReport(type) {
    const reportOutput = document.getElementById('reportOutput');
    reportOutput.innerHTML = '<p>正在生成报告...</p>';
    
    fetch(`/api/dashboard/report?type=${type}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 显示报告内容
                reportOutput.innerHTML = `
                    <h4>${type === 'daily' ? '日报告' : '周报告'}</h4>
                    <div class="report-content">
                        <h5>姿势分析摘要</h5>
                        <p>${data.report.posture_summary}</p>
                        
                        <h5>情绪分析摘要</h5>
                        <p>${data.report.emotion_summary}</p>
                        
                        <h5>专注度分析摘要</h5>
                        <p>${data.report.focus_summary}</p>
                        
                        <h5>学习建议</h5>
                        <p>${data.report.suggestions}</p>
                    </div>
                    <div class="report-timestamp">
                        报告生成时间: ${formatDate(new Date())}
                    </div>
                `;
            } else {
                reportOutput.innerHTML = `<p class="error">生成报告失败: ${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error('生成报告失败:', error);
            reportOutput.innerHTML = '<p class="error">生成报告失败，请稍后再试</p>';
        });
}

// 辅助函数：格式化日期
function formatDate(date) {
    return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).format(date);
}

// 辅助函数：格式化时间（仅时分秒）
function formatTime(date) {
    return new Intl.DateTimeFormat('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).format(date);
}