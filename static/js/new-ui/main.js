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