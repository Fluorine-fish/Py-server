/**
 * 家长端监控面板 - 前端交互脚本
 * 功能：
 * 1. 管理分析系统启动/停止
 * 2. 获取并显示实时姿势和情绪状态
 * 3. 生成并更新各种图表数据
 * 4. 提供日报和周报生成功能
 */

// 全局变量
let postureData = []; // 坐姿数据
let emotionData = {}; // 情绪数据
let focusData = []; // 专注度数据
let statusUpdateInterval = null; // 状态更新定时器
let chartUpdateInterval = null; // 图表更新定时器
let dataRecordInterval = null; // 数据记录定时器
let postureChart = null; // 坐姿图表实例
let emotionChart = null; // 情绪图表实例
let focusChart = null; // 专注度图表实例

// 页面加载完成初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('家长端监控面板初始化中...');
    
    // 初始化图表
    initCharts();
    
    // 初始化控制按钮事件
    initControlEvents();
    
    // 获取系统初始状态
    getSystemStatus();
    
    // 开始定时更新状态
    startStatusUpdates();
    
    // 开始定时更新图表数据
    startChartDataUpdates();
    
    // 开始定时记录数据
    startDataRecording();
});

/**
 * 初始化控制按钮事件
 */
function initControlEvents() {
    // 绑定启动分析按钮
    document.getElementById('startAnalysisBtn').addEventListener('click', function() {
        startAnalysisSystem();
    });
    
    // 绑定停止分析按钮
    document.getElementById('stopAnalysisBtn').addEventListener('click', function() {
        stopAnalysisSystem();
    });
}

/**
 * 启动分析系统
 */
function startAnalysisSystem() {
    fetch('/api/start_posture_analysis', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateSystemStatus('运行中', true);
            showNotification('分析系统已启动', 'success');
            
            // 重新开始定时记录数据
            startDataRecording();
        } else {
            updateSystemStatus('启动失败', false);
            showNotification('启动失败: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('启动系统失败:', error);
        updateSystemStatus('错误', false);
        showNotification('启动系统出错', 'error');
    });
}

/**
 * 停止分析系统
 */
function stopAnalysisSystem() {
    fetch('/api/stop_posture_analysis', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateSystemStatus('已停止', false);
            showNotification('分析系统已停止', 'success');
            
            // 停止定时记录
            if (dataRecordInterval) {
                clearInterval(dataRecordInterval);
                dataRecordInterval = null;
            }
        } else {
            showNotification('停止失败: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('停止系统失败:', error);
        showNotification('停止系统出错', 'error');
    });
}

/**
 * 获取系统状态
 */
function getSystemStatus() {
    fetch('/api/get_pose_status')
    .then(response => response.json())
    .then(data => {
        console.log('获取到系统状态:', data);
        
        // 更新系统状态显示
        if (data.status === 'success' || data.status === 'partial') {
            updateSystemStatus(data.is_running ? '运行中' : '已停止', data.is_running);
            
            // 更新姿势和情绪状态
            if (data.pose_data) {
                updatePostureStatus(data.pose_data);
            }
            
            if (data.emotion_data) {
                updateEmotionStatus(data.emotion_data);
            }
        } else {
            updateSystemStatus('错误: ' + data.message, false);
        }
    })
    .catch(error => {
        console.error('获取系统状态失败:', error);
        updateSystemStatus('连接错误', false);
    });
}

/**
 * 更新系统状态显示
 */
function updateSystemStatus(status, isRunning) {
    const statusElement = document.getElementById('systemStatusText');
    statusElement.textContent = status;
    
    if (isRunning) {
        statusElement.className = 'status-running';
    } else {
        statusElement.className = 'status-stopped';
    }
}

/**
 * 更新姿势状态显示
 */
function updatePostureStatus(poseData) {
    // 更新头部角度
    if (poseData.angle !== undefined) {
        document.getElementById('headAngle').textContent = poseData.angle.toFixed(1) + ' °';
    }
    
    // 更新姿势状态
    if (poseData.status) {
        const statusElement = document.getElementById('postureStatus');
        statusElement.textContent = poseData.status;
        
        // 添加状态样式
        if (poseData.is_bad_posture) {
            statusElement.innerHTML = poseData.status + ' <span class="badge badge-bad">不良</span>';
        } else {
            statusElement.innerHTML = poseData.status + ' <span class="badge badge-good">良好</span>';
        }
    }
    
    // 更新检测状态
    if (poseData.is_occluded !== undefined) {
        const detectionElement = document.getElementById('detectionStatus');
        if (poseData.is_occluded) {
            detectionElement.innerHTML = '遮挡 <span class="badge badge-warning">无法检测</span>';
        } else {
            detectionElement.innerHTML = '正常 <span class="badge badge-good">检测中</span>';
        }
    }
}

/**
 * 更新情绪状态显示
 */
function updateEmotionStatus(emotionData) {
    if (emotionData.emotion) {
        const statusElement = document.getElementById('emotionStatus');
        let emotionText = '';
        let badgeClass = 'badge-good';
        
        // 根据情绪类型设置不同的样式
        switch (emotionData.emotion) {
            case 'HAPPY':
                emotionText = '快乐';
                badgeClass = 'badge-good';
                break;
            case 'ANGRY':
                emotionText = '生气';
                badgeClass = 'badge-bad';
                break;
            case 'SAD':
                emotionText = '悲伤';
                badgeClass = 'badge-warning';
                break;
            case 'SURPRISED':
                emotionText = '惊讶';
                badgeClass = 'badge-warning';
                break;
            case 'NEUTRAL':
                emotionText = '平静';
                badgeClass = 'badge-good';
                break;
            case 'CONFUSED':
                emotionText = '困惑';
                badgeClass = 'badge-warning';
                break;
            default:
                emotionText = emotionData.emotion;
                badgeClass = 'badge-warning';
        }
        
        statusElement.innerHTML = emotionText + ` <span class="badge ${badgeClass}">${emotionText}</span>`;
    }
}

/**
 * 初始化所有图表
 */
function initCharts() {
    // 初始化默认数据 (实际数据将从API获取)
    postureData = {
        labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        data: [3, 1, 2, 4, 1, 0, 5]
    };
    
    emotionData = {
        labels: ['快乐', '平静', '生气', '困惑', '专注'],
        data: [20, 30, 10, 7, 30]
    };
    
    focusData = {
        labels: ['9:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'],
        data: [80, 60, 70, 90, 50, 60, 85]
    };
    
    // 从API获取初始数据
    fetchPostureData();
    fetchEmotionData();
    fetchFocusData();
    
    // 初始化坐姿图表
    const postureCtx = document.getElementById('postureChart').getContext('2d');
    postureChart = new Chart(postureCtx, {
        type: 'bar',
        data: {
            labels: postureData.labels,
            datasets: [{
                label: '坐姿不良次数',
                data: postureData.data,
                backgroundColor: '#f67280'
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '一周坐姿不良次数统计'
                }
            }
        }
    });
    
    // 初始化情绪图表
    const emotionCtx = document.getElementById('emotionChart').getContext('2d');
    emotionChart = new Chart(emotionCtx, {
        type: 'pie',
        data: {
            labels: emotionData.labels,
            datasets: [{
                data: emotionData.data,
                backgroundColor: ['#6a89cc', '#78e08f', '#e55039', '#60a3bc', '#f6b93b']
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '情绪分布统计'
                }
            }
        }
    });
    
    // 初始化专注度图表
    const focusCtx = document.getElementById('focusChart').getContext('2d');
    focusChart = new Chart(focusCtx, {
        type: 'line',
        data: {
            labels: focusData.labels,
            datasets: [{
                label: '专注度(%)',
                data: focusData.data,
                fill: true,
                backgroundColor: 'rgba(56, 173, 169, 0.2)',
                borderColor: '#38ada9',
                tension: 0.3
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '今日专注度趋势'
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100
                }
            }
        }
    });
    
    console.log('所有图表初始化完成');
}

/**
 * 从API获取坐姿数据
 */
function fetchPostureData() {
    fetch('/api/get_posture_data?days=7')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.data) {
            // 更新图表数据
            postureData = data.data;
            
            // 更新图表
            postureChart.data.labels = postureData.labels;
            postureChart.data.datasets[0].data = postureData.data;
            postureChart.update();
            
            console.log('坐姿数据已更新');
        } else {
            console.error('获取坐姿数据失败:', data.message);
        }
    })
    .catch(error => {
        console.error('获取坐姿数据出错:', error);
    });
}

/**
 * 从API获取情绪分布数据
 */
function fetchEmotionData() {
    fetch('/api/get_emotion_distribution?hours=24')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.data) {
            // 更新图表数据
            emotionData = data.data;
            
            // 更新图表
            emotionChart.data.labels = emotionData.labels;
            emotionChart.data.datasets[0].data = emotionData.data;
            emotionChart.update();
            
            console.log('情绪数据已更新');
        } else {
            console.error('获取情绪数据失败:', data.message);
        }
    })
    .catch(error => {
        console.error('获取情绪数据出错:', error);
    });
}

/**
 * 从API获取专注度数据
 */
function fetchFocusData() {
    fetch('/api/get_focus_data?hours=7')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.data) {
            // 更新图表数据
            focusData = data.data;
            
            // 更新图表
            focusChart.data.labels = focusData.labels;
            focusChart.data.datasets[0].data = focusData.data;
            focusChart.update();
            
            console.log('专注度数据已更新');
        } else {
            console.error('获取专注度数据失败:', data.message);
        }
    })
    .catch(error => {
        console.error('获取专注度数据出错:', error);
    });
}

/**
 * 开始定时更新状态
 */
function startStatusUpdates() {
    // 清除可能存在的旧定时器
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    
    // 设置新的定时更新（每3秒更新一次状态）
    statusUpdateInterval = setInterval(function() {
        getSystemStatus();
    }, 3000);
    
    console.log('状态定时更新已启动');
}

/**
 * 开始定时更新图表数据
 */
function startChartDataUpdates() {
    // 清除可能存在的旧定时器
    if (chartUpdateInterval) {
        clearInterval(chartUpdateInterval);
    }
    
    // 设置新的定时更新（每60秒更新一次图表数据）
    chartUpdateInterval = setInterval(function() {
        fetchPostureData();
        fetchEmotionData();
        fetchFocusData();
    }, 60000);
    
    console.log('图表数据定时更新已启动');
}

/**
 * 开始定时记录分析数据
 */
function startDataRecording() {
    // 清除可能存在的旧定时器
    if (dataRecordInterval) {
        clearInterval(dataRecordInterval);
    }
    
    // 先立即记录一次数据
    recordAnalysisData();
    
    // 设置新的定时记录（每15秒记录一次数据）
    dataRecordInterval = setInterval(function() {
        recordAnalysisData();
    }, 15000);
    
    console.log('分析数据定时记录已启动');
}

/**
 * 记录分析数据到数据库
 */
function recordAnalysisData() {
    fetch('/api/record_analysis_data', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('分析数据记录成功');
        } else {
            console.warn('记录分析数据失败:', data.message);
        }
    })
    .catch(error => {
        console.error('记录分析数据出错:', error);
    });
}

/**
 * 生成报告
 */
function generateReport(type) {
    // 显示加载中提示
    document.getElementById('reportOutput').innerHTML = `
        <div class="section" style="margin-top: 20px;">
            <h3>正在生成${type === 'daily' ? '日' : '周'}报告...</h3>
            <p>请稍候，正在收集和分析数据...</p>
        </div>
    `;
    
    // 从API获取报告数据
    fetch(`/api/generate_report?type=${type}`)
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.report) {
            const report = data.report;
            const formattedDate = new Date(report.timestamp).toLocaleDateString('zh-CN');
            
            // 生成报告内容
            let reportContent = '';
            
            if (type === 'daily') {
                reportContent = `
                    <div class="report-section">
                        <h3>坐姿情况</h3>
                        <p>今日坐姿不良次数: <strong>${report.posture_data.daily_average}</strong> 次</p>
                        <p>本周累计: <strong>${report.posture_data.total_issues}</strong> 次</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>情绪状态</h3>
                        <p>主要情绪: <strong>${report.emotion_data.main_emotion}</strong></p>
                        <p>情绪分布: ${formatEmotionDistribution(report.emotion_data.distribution)}</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>专注度分析</h3>
                        <p>今日平均专注度: <strong>${report.focus_data.average}%</strong></p>
                        <p>最高专注度: <strong>${report.focus_data.max}%</strong> (${report.focus_data.best_hour})</p>
                        <p>最低专注度: <strong>${report.focus_data.min}%</strong></p>
                    </div>
                    
                    <div class="report-section">
                        <h3>建议</h3>
                        <p>${generateSuggestions(report.posture_data.daily_average, report.emotion_data.main_emotion, report.focus_data.average)}</p>
                    </div>
                `;
            } else {
                reportContent = `
                    <div class="report-section">
                        <h3>坐姿情况</h3>
                        <p>本周坐姿不良总次数: <strong>${report.posture_data.total_issues}</strong> 次</p>
                        <p>日均坐姿不良次数: <strong>${report.posture_data.daily_average}</strong> 次</p>
                        <p>坐姿最差的日子: <strong>${report.posture_data.worst_day}</strong></p>
                    </div>
                    
                    <div class="report-section">
                        <h3>情绪状态</h3>
                        <p>一周主要情绪: <strong>${report.emotion_data.main_emotion}</strong></p>
                        <p>情绪分布: ${formatEmotionDistribution(report.emotion_data.distribution)}</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>专注度分析</h3>
                        <p>周平均专注度: <strong>${report.focus_data.average}%</strong></p>
                        <p>最佳学习时间段: <strong>${report.focus_data.best_hour}</strong> (专注度 ${report.focus_data.max}%)</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>本周总结</h3>
                        <p>${generateWeeklySummary(report.posture_data.daily_average, report.emotion_data.main_emotion, report.focus_data.average)}</p>
                    </div>
                    
                    <div class="report-section">
                        <h3>改进建议</h3>
                        <p>${generateWeeklySuggestions(report.posture_data.daily_average, report.emotion_data.main_emotion, report.focus_data.average)}</p>
                    </div>
                `;
            }
            
            // 显示报告
            document.getElementById('reportOutput').innerHTML = `
                <div class="section" style="margin-top: 20px;">
                    <h3>${type === 'daily' ? '日' : '周'}报告 (${formattedDate})</h3>
                    ${reportContent}
                </div>
            `;
            
        } else {
            document.getElementById('reportOutput').innerHTML = `
                <div class="section" style="margin-top: 20px;">
                    <h3>生成报告失败</h3>
                    <p>错误: ${data.message || '未知错误'}</p>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('生成报告出错:', error);
        document.getElementById('reportOutput').innerHTML = `
            <div class="section" style="margin-top: 20px;">
                <h3>生成报告错误</h3>
                <p>无法连接到服务器，请稍后再试。</p>
            </div>
        `;
    });
    
    // 滚动到报告位置
    document.getElementById('reportOutput').scrollIntoView({behavior: 'smooth'});
}

/**
 * 格式化情绪分布数据
 */
function formatEmotionDistribution(distribution) {
    let result = [];
    for (const [emotion, value] of Object.entries(distribution)) {
        result.push(`${emotion}(${value}%)`);
    }
    return result.join(', ');
}

/**
 * 生成每日建议
 */
function generateSuggestions(postureIssues, mainEmotion, avgFocus) {
    let suggestions = [];
    
    // 根据坐姿情况生成建议
    if (postureIssues > 4) {
        suggestions.push("坐姿需要改善，建议增加休息次数，调整椅子和桌子高度。");
    } else if (postureIssues > 2) {
        suggestions.push("坐姿情况一般，注意保持正确坐姿，每45分钟起来活动一下。");
    } else {
        suggestions.push("坐姿情况良好，继续保持。");
    }
    
    // 根据情绪状态生成建议
    if (mainEmotion === '生气' || mainEmotion === '悲伤') {
        suggestions.push("今日情绪较低落，建议安排一些轻松的活动，帮助调节心情。");
    } else if (mainEmotion === '困惑') {
        suggestions.push("孩子今日学习时有些困惑，可能需要额外的学习辅导。");
    } else if (mainEmotion === '快乐' || mainEmotion === '平静') {
        suggestions.push("今日情绪良好，是深入学习的好时机。");
    }
    
    // 根据专注度生成建议
    if (avgFocus < 50) {
        suggestions.push("今日专注度较低，建议检查学习环境是否有干扰因素，或考虑调整学习计划。");
    } else if (avgFocus < 70) {
        suggestions.push("专注度一般，可以尝试番茄钟工作法来提高专注力。");
    } else {
        suggestions.push("今日专注度良好，可以安排更具挑战性的学习任务。");
    }
    
    return suggestions.join(" ");
}

/**
 * 生成周总结
 */
function generateWeeklySummary(avgPosture, mainEmotion, avgFocus) {
    let summary = "本周";
    
    // 评价坐姿
    if (avgPosture > 3) {
        summary += "坐姿情况不佳，";
    } else if (avgPosture > 1.5) {
        summary += "坐姿情况一般，";
    } else {
        summary += "坐姿情况良好，";
    }
    
    // 评价情绪
    if (mainEmotion === '快乐' || mainEmotion === '平静') {
        summary += "情绪状态积极，";
    } else if (mainEmotion === '专注') {
        summary += "学习专注度高，";
    } else {
        summary += `情绪以${mainEmotion}为主，`;
    }
    
    // 评价专注度
    if (avgFocus > 75) {
        summary += "整体学习效率很高。";
    } else if (avgFocus > 60) {
        summary += "学习效率尚可。";
    } else {
        summary += "学习专注度有待提高。";
    }
    
    return summary;
}

/**
 * 生成周建议
 */
function generateWeeklySuggestions(avgPosture, mainEmotion, avgFocus) {
    let suggestions = [];
    
    // 坐姿建议
    if (avgPosture > 3) {
        suggestions.push("建议购买符合人体工学的椅子和桌子，定期提醒孩子保持正确坐姿。");
    } else if (avgPosture > 1.5) {
        suggestions.push("适当增加运动时间，强化核心肌群，有助于保持良好坐姿。");
    }
    
    // 情绪建议
    if (mainEmotion === '生气' || mainEmotion === '悲伤' || mainEmotion === '困惑') {
        suggestions.push("多与孩子沟通，了解学习中的困难，必要时提供专业辅导。");
    }
    
    // 专注度建议
    if (avgFocus < 65) {
        suggestions.push("检查学习环境，减少干扰因素，可以尝试白噪音助于集中注意力。");
        suggestions.push("建立规律的作息时间表，将最需要专注的任务安排在精力最充沛的时段。");
    }
    
    if (suggestions.length === 0) {
        return "本周表现良好，继续保持当前的学习和生活习惯。";
    }
    
    return suggestions.join(" ");
}

/**
 * 显示通知消息
 */
function showNotification(message, type = 'info') {
    // 如果浏览器支持原生通知，可以实现
    console.log(`通知 [${type}]: ${message}`);
    
    // 简单的消息显示方式
    alert(message);
}