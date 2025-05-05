// statistics.js - 统计数据可视化功能

let postureChart = null;
let emotionChart = null;
let focusChart = null;

document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表
    initCharts();
    
    // 获取初始数据
    fetchStatistics('day');
    
    // 绑定时间范围选择器事件
    document.querySelectorAll('.period-selector').forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.dataset.period;
            fetchStatistics(period);
            
            // 更新按钮状态
            document.querySelectorAll('.period-selector').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

function initCharts() {
    // 初始化姿势统计图表
    const postureCtx = document.getElementById('postureChart').getContext('2d');
    postureChart = new Chart(postureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '头部角度',
                    data: [],
                    borderColor: '#4a90e2',
                    tension: 0.4
                },
                {
                    label: '良好姿势比例',
                    data: [],
                    borderColor: '#2ecc71',
                    tension: 0.4
                }
            ]
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
    
    // 初始化情绪分布图表
    const emotionCtx = document.getElementById('emotionChart').getContext('2d');
    emotionChart = new Chart(emotionCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#4a90e2',  // 中性
                    '#2ecc71',  // 开心
                    '#e74c3c',  // 生气
                    '#f1c40f',  // 专注
                    '#95a5a6'   // 其他
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // 初始化专注度趋势图表
    const focusCtx = document.getElementById('focusChart').getContext('2d');
    focusChart = new Chart(focusCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '专注度',
                data: [],
                borderColor: '#2ecc71',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function fetchStatistics(period) {
    // 获取姿势统计数据
    fetch(`/api/posture/stats?period=${period}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updatePostureChart(data.data);
                updatePostureStats(data.data.stats);
            }
        })
        .catch(error => console.error('获取姿势统计失败:', error));
    
    // 获取情绪统计数据
    fetch(`/api/emotion/stats?period=${period}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateEmotionChart(data.data);
                updateEmotionStats(data.data.distribution);
            }
        })
        .catch(error => console.error('获取情绪统计失败:', error));
    
    // 获取专注度统计数据
    fetch('/api/focus/stats')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateFocusChart(data.data);
                updateFocusStats(data.data.current_session);
            }
        })
        .catch(error => console.error('获取专注度统计失败:', error));
}

function updatePostureChart(data) {
    const labels = data.trends.map(item => item.hour);
    const angles = data.trends.map(item => item.avg_angle);
    const goodRatios = data.trends.map(item => (item.good_count / item.count) * 100);
    
    postureChart.data.labels = labels;
    postureChart.data.datasets[0].data = angles;
    postureChart.data.datasets[1].data = goodRatios;
    postureChart.update();
}

function updateEmotionChart(data) {
    const emotionData = data.distribution;
    const labels = emotionData.map(item => item.emotion_type);
    const counts = emotionData.map(item => item.count);
    
    emotionChart.data.labels = labels;
    emotionChart.data.datasets[0].data = counts;
    emotionChart.update();
}

function updateFocusChart(data) {
    const trends = data.trends;
    const labels = trends.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleTimeString();
    });
    const scores = trends.map(item => item.focus_score);
    
    focusChart.data.labels = labels;
    focusChart.data.datasets[0].data = scores;
    focusChart.update();
}

function updatePostureStats(stats) {
    document.getElementById('avgAngle').textContent = stats.avg_angle.toFixed(1) + '°';
    document.getElementById('goodPostureTime').textContent = formatDuration(stats.good_duration);
    document.getElementById('badPostureTime').textContent = formatDuration(stats.bad_duration);
    document.getElementById('occludedTime').textContent = formatDuration(stats.occluded_duration);
}

function updateEmotionStats(distribution) {
    const totalCount = distribution.reduce((sum, item) => sum + item.count, 0);
    const statsContainer = document.getElementById('emotionStats');
    statsContainer.innerHTML = '';
    
    distribution.forEach(item => {
        const percentage = ((item.count / totalCount) * 100).toFixed(1);
        const div = document.createElement('div');
        div.className = 'stat-item';
        div.innerHTML = `
            <span class="emotion-type">${item.emotion_type}</span>
            <span class="emotion-percentage">${percentage}%</span>
            <span class="emotion-confidence">(置信度: ${(item.avg_confidence * 100).toFixed(1)}%)</span>
        `;
        statsContainer.appendChild(div);
    });
}

function updateFocusStats(stats) {
    document.getElementById('avgFocus').textContent = stats.avg_focus.toFixed(1);
    document.getElementById('maxFocus').textContent = stats.max_focus.toFixed(1);
    document.getElementById('minFocus').textContent = stats.min_focus.toFixed(1);
    document.getElementById('focusDuration').textContent = formatDuration(stats.total_duration);
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    const parts = [];
    if (hours > 0) parts.push(`${hours}小时`);
    if (minutes > 0) parts.push(`${minutes}分钟`);
    if (remainingSeconds > 0) parts.push(`${remainingSeconds}秒`);
    
    return parts.join(' ');
}