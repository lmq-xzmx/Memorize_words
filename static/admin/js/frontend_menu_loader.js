/**
 * 前端菜单组件加载器
 * 确保组件按正确顺序加载，并提供统一的初始化入口
 */

(function() {
    'use strict';
    
    // 组件加载状态
    const loadStatus = {
        FrontendMenuSelector: false,
        FrontendMenuSelectorConfig: false,
        FrontendMenuSelectorFactory: false,
        integration: false
    };
    
    // 等待加载的回调队列
    const loadCallbacks = [];
    
    // 检查所有组件是否已加载
    function checkAllLoaded() {
        const allLoaded = Object.values(loadStatus).every(status => status);
        if (allLoaded) {
            executeCallbacks();
        }
        return allLoaded;
    }
    
    // 执行等待的回调
    function executeCallbacks() {
        while (loadCallbacks.length > 0) {
            const callback = loadCallbacks.shift();
            try {
                callback();
            } catch (error) {
                console.error('Error executing frontend menu callback:', error);
            }
        }
    }
    
    // 标记组件已加载
    function markLoaded(componentName) {
        if (loadStatus.hasOwnProperty(componentName)) {
            loadStatus[componentName] = true;
            console.log(`Frontend menu component loaded: ${componentName}`);
            checkAllLoaded();
        }
    }
    
    // 等待所有组件加载完成
    function waitForComponents(callback) {
        if (checkAllLoaded()) {
            callback();
        } else {
            loadCallbacks.push(callback);
        }
    }
    
    // 动态加载脚本
    function loadScript(src, componentName) {
        return new Promise((resolve, reject) => {
            // 检查是否已经加载
            if (document.querySelector(`script[src="${src}"]`)) {
                markLoaded(componentName);
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => {
                markLoaded(componentName);
                resolve();
            };
            script.onerror = () => {
                console.error(`Failed to load script: ${src}`);
                reject(new Error(`Failed to load ${componentName}`));
            };
            
            document.head.appendChild(script);
        });
    }
    
    // 加载所有组件
    async function loadAllComponents() {
        const basePath = '/static/admin/js/components/';
        
        try {
            // 按顺序加载组件
            await loadScript(basePath + 'FrontendMenuSelector.js', 'FrontendMenuSelector');
            await loadScript(basePath + 'FrontendMenuSelectorConfig.js', 'FrontendMenuSelectorConfig');
            await loadScript(basePath + 'FrontendMenuSelectorFactory.js', 'FrontendMenuSelectorFactory');
            await loadScript('/static/admin/js/frontend_menu_integration.js', 'integration');
            
            console.log('All frontend menu components loaded successfully');
            
        } catch (error) {
            console.error('Failed to load frontend menu components:', error);
            // 标记为降级模式
            window.frontendMenuFallbackMode = true;
        }
    }
    
    // 初始化组件系统
    function initializeComponents() {
        if (window.frontendMenuFallbackMode) {
            console.warn('Frontend menu components running in fallback mode');
            return;
        }
        
        try {
            // 检查依赖是否正确加载
            if (!window.FrontendMenuSelectorFactory) {
                throw new Error('FrontendMenuSelectorFactory not available');
            }
            
            // 初始化工厂
            if (!window.frontendMenuSelectorFactory) {
                window.frontendMenuSelectorFactory = new window.FrontendMenuSelectorFactory();
            }
            
            console.log('Frontend menu component system initialized');
            
        } catch (error) {
            console.error('Failed to initialize frontend menu components:', error);
            window.frontendMenuFallbackMode = true;
        }
    }
    
    // 页面特定初始化
    function initPageSpecific() {
        const currentUrl = window.location.pathname;
        
        // 根据页面类型进行特定初始化
        if (currentUrl.includes('/admin/permissions/')) {
            if (currentUrl.includes('frontendmenuroleassignment')) {
                initFrontendMenuRoleAssignmentPage();
            } else if (currentUrl.includes('frontendmenuconfig')) {
                initFrontendMenuConfigPage();
            } else if (currentUrl.includes('menuvalidity')) {
                initMenuValidityPage();
            }
        }
    }
    
    // 前端菜单角色分配页面初始化
    function initFrontendMenuRoleAssignmentPage() {
        console.log('Initializing frontend menu role assignment page');
        
        if (window.frontendMenuSelectorFactory) {
            const config = window.FrontendMenuSelectorConfig.getFrontendMenuRoleAssignmentConfig();
            window.frontendMenuSelectorFactory.create('frontendMenuRoleAssignment', config);
        }
    }
    
    // 前端菜单配置页面初始化
    function initFrontendMenuConfigPage() {
        console.log('Initializing frontend menu config page');
        
        if (window.frontendMenuSelectorFactory) {
            const config = window.FrontendMenuSelectorConfig.getFrontendMenuConfigConfig();
            window.frontendMenuSelectorFactory.create('frontendMenuConfig', config);
        }
    }
    
    // 菜单有效性页面初始化
    function initMenuValidityPage() {
        console.log('Initializing menu validity page');
        
        if (window.frontendMenuSelectorFactory) {
            const config = window.FrontendMenuSelectorConfig.getMenuValidityConfig();
            window.frontendMenuSelectorFactory.create('menuValidity', config);
        }
    }
    
    // 清理函数
    function cleanup() {
        if (window.frontendMenuSelectorFactory) {
            window.frontendMenuSelectorFactory.destroyAll();
        }
    }
    
    // 主初始化函数
    function init() {
        // 检查jQuery是否可用
        if (typeof django === 'undefined' || !django.jQuery) {
            console.error('Django jQuery not available for frontend menu components');
            window.frontendMenuFallbackMode = true;
            return;
        }
        
        // 加载组件
        loadAllComponents().then(() => {
            waitForComponents(() => {
                initializeComponents();
                initPageSpecific();
            });
        });
    }
    
    // 导出到全局
    window.frontendMenuLoader = {
        init: init,
        waitForComponents: waitForComponents,
        loadAllComponents: loadAllComponents,
        initializeComponents: initializeComponents,
        cleanup: cleanup,
        loadStatus: loadStatus
    };
    
    // 页面卸载时清理
    window.addEventListener('beforeunload', cleanup);
    
    // DOM加载完成后自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM已经加载完成
        init();
    }
    
})();