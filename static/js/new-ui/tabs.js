/**
 * Tabs Component - Modern UI Framework
 * For Smart Working Environment Monitoring System
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
});

/**
 * Initialize all tab components on the page
 */
function initializeTabs() {
    const tabContainers = document.querySelectorAll('.tabs-container');
    
    tabContainers.forEach(container => {
        const tabLinks = container.querySelectorAll('.tabs-nav-link');
        const tabContents = container.querySelectorAll('.tab-content');
        
        // Set first tab as active by default if none is active
        if (!container.querySelector('.tabs-nav-link.active')) {
            const firstTab = container.querySelector('.tabs-nav-link');
            if (firstTab) {
                firstTab.classList.add('active');
                const targetId = firstTab.getAttribute('data-tab');
                const targetContent = container.querySelector(`#${targetId}`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            }
        }
        
        // Add click event listeners to all tab links
        tabLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all tabs
                tabLinks.forEach(tab => tab.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to current tab
                this.classList.add('active');
                
                // Show corresponding content
                const targetId = this.getAttribute('data-tab');
                const targetContent = container.querySelector(`#${targetId}`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                // Save active tab in localStorage if persistentTabs is enabled
                const containerId = container.getAttribute('id');
                if (containerId && container.getAttribute('data-persistent') === 'true') {
                    localStorage.setItem(`activeTab-${containerId}`, targetId);
                }
                
                // Trigger custom event for tab change
                const tabChangeEvent = new CustomEvent('tabChange', {
                    detail: {
                        tabId: targetId,
                        containerId: containerId
                    }
                });
                container.dispatchEvent(tabChangeEvent);
            });
        });
        
        // Restore active tab from localStorage if persistentTabs is enabled
        const containerId = container.getAttribute('id');
        if (containerId && container.getAttribute('data-persistent') === 'true') {
            const activeTabId = localStorage.getItem(`activeTab-${containerId}`);
            if (activeTabId) {
                const savedTab = container.querySelector(`.tabs-nav-link[data-tab="${activeTabId}"]`);
                if (savedTab) {
                    savedTab.click();
                }
            }
        }
    });
}

/**
 * Dynamically update content of a tab
 * @param {string} containerId - ID of the tabs container
 * @param {string} tabId - ID of the tab content to update
 * @param {string|HTMLElement} content - New content to display
 */
function updateTabContent(containerId, tabId, content) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const tabContent = container.querySelector(`#${tabId}`);
    if (!tabContent) return;
    
    if (typeof content === 'string') {
        tabContent.innerHTML = content;
    } else if (content instanceof HTMLElement) {
        tabContent.innerHTML = '';
        tabContent.appendChild(content);
    }
}

/**
 * Switch to a specific tab programmatically
 * @param {string} containerId - ID of the tabs container
 * @param {string} tabId - ID of the tab to activate
 */
function switchToTab(containerId, tabId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const tabLink = container.querySelector(`.tabs-nav-link[data-tab="${tabId}"]`);
    if (!tabLink) return;
    
    tabLink.click();
}

document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tabs li a');
    const panels = document.querySelectorAll('.tab-panel');
    
    // 初始化标签页
    function initTabs() {
        const hash = window.location.hash || '#overview';
        activateTab(hash);
        
        // 为每个标签添加点击事件
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                activateTab(tab.getAttribute('href'));
            });
        });
        
        // 处理浏览器后退/前进
        window.addEventListener('hashchange', () => {
            activateTab(window.location.hash || '#overview');
        });
    }
    
    // 激活指定标签页
    function activateTab(hash) {
        // 移除所有活动状态
        tabs.forEach(tab => {
            tab.parentElement.classList.remove('active');
        });
        panels.forEach(panel => {
            panel.classList.remove('active');
        });
        
        // 激活目标标签和面板
        const targetTab = document.querySelector(`.tabs li a[href="${hash}"]`);
        const targetPanel = document.querySelector(hash);
        
        if (targetTab && targetPanel) {
            targetTab.parentElement.classList.add('active');
            targetPanel.classList.add('active');
            window.location.hash = hash;
        }
    }
    
    // 初始化
    initTabs();
});