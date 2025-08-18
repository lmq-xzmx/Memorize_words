/**
 * 权限变更通知管理器
 * 处理权限变更时的用户通知机制，包括实时通知、批量通知和通知历史管理
 */

import { webSocketManager } from './websocketManager';
import { PermissionCache } from './permissionCache';

// 类型定义
interface NotificationData {
    userId?: string;
    permissions?: string[];
    action?: string;
    resource?: string;
    timestamp?: number;
    oldRole?: string;
    newRole?: string;
    menuChanges?: MenuChanges;
    type?: string;
    title?: string;
    message?: string;
    priority?: string;
    targetUsers?: string[];
    updates?: any[];
}

interface MenuChanges {
    added?: string[];
    removed?: string[];
}

interface NotificationAction {
    label: string;
    action: string;
    primary: boolean;
}

interface Notification {
    id: string;
    type: string;
    priority: string;
    title: string;
    message: string;
    data: NotificationData;
    timestamp: number;
    displayMethod: string;
    actions?: NotificationAction[];
    read?: boolean;
    readAt?: number;
}

interface NotificationConfig {
    enableRealTimeNotifications: boolean;
    enableBatchNotifications: boolean;
    batchInterval: number;
    maxToastNotifications: number;
    autoHideDelay: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    soundEnabled: boolean;
    vibrationEnabled: boolean;
}

interface ModalData {
    id: string;
    title: string;
    message: string;
    priority: string;
    actions: NotificationAction[];
    onAction: (action: string) => void;
    onClose: () => void;
}

interface BannerData {
    id: string;
    message: string;
    priority: string;
    actions: NotificationAction[];
    onAction: (action: string) => void;
    onDismiss: () => void;
}

interface NotificationStats {
    total: number;
    unread: number;
    byType: Record<string, number>;
    byPriority: Record<string, number>;
    recentActivity: Notification[];
}

type NotificationListener = (event: string, data: any) => void;

class PermissionNotificationManager {
    private notifications: Map<string, Notification>;
    private notificationHistory: Notification[];
    private maxHistorySize: number;
    private listeners: Set<NotificationListener>;
    private notificationTypes: Record<string, string>;
    private notificationPriorities: Record<string, string>;
    private displayMethods: Record<string, string>;
    private config: NotificationConfig;
    private batchQueue: NotificationData[];
    private activeToasts: Set<string>;
    private soundCache: Map<string, HTMLAudioElement>;

    constructor() {
        this.notifications = new Map();
        this.notificationHistory = [];
        this.maxHistorySize = 200;
        this.listeners = new Set();
        
        this.notificationTypes = {
            PERMISSION_GRANTED: 'permission_granted',
            PERMISSION_REVOKED: 'permission_revoked',
            ROLE_CHANGED: 'role_changed',
            MENU_ACCESS_UPDATED: 'menu_access_updated',
            SYSTEM_MAINTENANCE: 'system_maintenance',
            SECURITY_ALERT: 'security_alert',
            BATCH_UPDATE: 'batch_update'
        };
        
        this.notificationPriorities = {
            LOW: 'low',
            MEDIUM: 'medium',
            HIGH: 'high',
            CRITICAL: 'critical'
        };
        
        this.displayMethods = {
            TOAST: 'toast',
            MODAL: 'modal',
            BANNER: 'banner',
            BADGE: 'badge',
            SILENT: 'silent'
        };
        
        this.config = {
            enableRealTimeNotifications: true,
            enableBatchNotifications: true,
            batchInterval: 30000, // 30秒
            maxToastNotifications: 5,
            autoHideDelay: {
                low: 3000,
                medium: 5000,
                high: 8000,
                critical: 0 // 不自动隐藏
            },
            soundEnabled: true,
            vibrationEnabled: true
        };
        
        this.batchQueue = [];
        this.activeToasts = new Set();
        this.soundCache = new Map();
        
        this.init();
    }

    /**
     * 初始化通知管理器
     */
    init(): void {
        this.setupWebSocketListeners();
        this.startBatchProcessor();
        this.loadNotificationSettings();
        this.preloadSounds();
        
        console.log('[PermissionNotificationManager] 权限通知管理器已初始化');
    }

    /**
     * 设置WebSocket监听器
     */
    setupWebSocketListeners(): void {
        webSocketManager.addListener('permissionChanged', (data: NotificationData) => {
            this.handlePermissionChange(data);
        });
        
        webSocketManager.addListener('roleUpdated', (data: NotificationData) => {
            this.handleRoleUpdate(data);
        });
        
        webSocketManager.addListener('menuAccessChanged', (data: NotificationData) => {
            this.handleMenuAccessChange(data);
        });
        
        webSocketManager.addListener('systemNotification', (data: NotificationData) => {
            this.handleSystemNotification(data);
        });
    }

    /**
     * 处理权限变更
     */
    async handlePermissionChange(data: NotificationData): Promise<void> {
        const { userId, permissions, action, resource, timestamp } = data;
        
        // 检查是否为当前用户
        const currentUserId = this.getCurrentUserId();
        if (userId !== currentUserId) {
            return;
        }
        
        const notificationType = action === 'grant' 
            ? this.notificationTypes.PERMISSION_GRANTED 
            : this.notificationTypes.PERMISSION_REVOKED;
        
        const notification: Notification = {
            id: this.generateId(),
            type: notificationType,
            priority: this.notificationPriorities.MEDIUM,
            title: action === 'grant' ? '权限已授予' : '权限已撤销',
            message: this.formatPermissionMessage(resource || '', action || ''),
            data: { userId, permissions, action, resource },
            timestamp: timestamp || Date.now(),
            displayMethod: this.getDisplayMethod(notificationType),
            actions: this.getNotificationActions(notificationType)
        };
        
        await this.showNotification(notification);
        
        // 清除相关缓存
        this.clearRelatedCache(resource || '');
        
        console.log('[PermissionNotificationManager] 权限变更通知:', notification);
    }

    /**
     * 处理角色更新
     */
    async handleRoleUpdate(data: NotificationData): Promise<void> {
        const { userId, oldRole, newRole, permissions, timestamp } = data;
        
        const currentUserId = this.getCurrentUserId();
        if (userId !== currentUserId) {
            return;
        }
        
        const notification: Notification = {
            id: this.generateId(),
            type: this.notificationTypes.ROLE_CHANGED,
            priority: this.notificationPriorities.HIGH,
            title: '角色已更新',
            message: `您的角色已从 "${oldRole}" 更改为 "${newRole}"`,
            data: { userId, oldRole, newRole, permissions },
            timestamp: timestamp || Date.now(),
            displayMethod: this.displayMethods.MODAL,
            actions: [
                {
                    label: '查看详情',
                    action: 'viewRoleDetails',
                    primary: true
                },
                {
                    label: '刷新页面',
                    action: 'refreshPage',
                    primary: false
                }
            ]
        };
        
        await this.showNotification(notification);
        
        // 清除所有权限缓存
        this.clearAllPermissionCache();
        
        console.log('[PermissionNotificationManager] 角色更新通知:', notification);
    }

    /**
     * 处理菜单访问变更
     */
    async handleMenuAccessChange(data: NotificationData): Promise<void> {
        const { userId, menuChanges, timestamp } = data;
        
        const currentUserId = this.getCurrentUserId();
        if (userId !== currentUserId) {
            return;
        }
        
        const notification: Notification = {
            id: this.generateId(),
            type: this.notificationTypes.MENU_ACCESS_UPDATED,
            priority: this.notificationPriorities.MEDIUM,
            title: '菜单访问权限已更新',
            message: this.formatMenuChangeMessage(menuChanges || {}),
            data: { userId, menuChanges },
            timestamp: timestamp || Date.now(),
            displayMethod: this.displayMethods.TOAST,
            actions: [
                {
                    label: '刷新菜单',
                    action: 'refreshMenu',
                    primary: true
                }
            ]
        };
        
        await this.showNotification(notification);
        
        // 触发菜单刷新
        this.triggerMenuRefresh();
        
        console.log('[PermissionNotificationManager] 菜单访问变更通知:', notification);
    }

    /**
     * 处理系统通知
     */
    async handleSystemNotification(data: NotificationData): Promise<void> {
        const { type, title, message, priority, targetUsers, timestamp } = data;
        
        const currentUserId = this.getCurrentUserId();
        if (targetUsers && !targetUsers.includes(currentUserId || '')) {
            return;
        }
        
        const notification: Notification = {
            id: this.generateId(),
            type: type || this.notificationTypes.SYSTEM_MAINTENANCE,
            priority: priority || this.notificationPriorities.MEDIUM,
            title: title || '系统通知',
            message: message || '',
            data: data,
            timestamp: timestamp || Date.now(),
            displayMethod: this.getDisplayMethod(type, priority),
            actions: this.getSystemNotificationActions(type)
        };
        
        await this.showNotification(notification);
        
        console.log('[PermissionNotificationManager] 系统通知:', notification);
    }

    /**
     * 显示通知
     */
    async showNotification(notification: Notification): Promise<void> {
        // 添加到通知历史
        this.addToHistory(notification);
        
        // 根据显示方法处理通知
        switch (notification.displayMethod) {
            case this.displayMethods.TOAST:
                await this.showToastNotification(notification);
                break;
            
            case this.displayMethods.MODAL:
                await this.showModalNotification(notification);
                break;
            
            case this.displayMethods.BANNER:
                await this.showBannerNotification(notification);
                break;
            
            case this.displayMethods.BADGE:
                await this.showBadgeNotification(notification);
                break;
            
            case this.displayMethods.SILENT:
                // 静默通知，只记录历史
                break;
            
            default:
                await this.showToastNotification(notification);
        }
        
        // 播放声音和振动
        await this.playNotificationEffects(notification);
        
        // 通知监听器
        this.notifyListeners('notificationShown', notification);
    }

    /**
     * 显示Toast通知
     */
    async showToastNotification(notification: Notification): Promise<void> {
        // 检查Toast数量限制
        if (this.activeToasts.size >= this.config.maxToastNotifications) {
            // 移除最旧的Toast
            const oldestToast = Array.from(this.activeToasts)[0];
            this.hideToastNotification(oldestToast);
        }
        
        const toastElement = this.createToastElement(notification);
        this.activeToasts.add(notification.id);
        
        // 添加到DOM
        this.getToastContainer().appendChild(toastElement);
        
        // 自动隐藏
        const autoHideDelay = this.config.autoHideDelay[notification.priority as keyof typeof this.config.autoHideDelay];
        if (autoHideDelay > 0) {
            setTimeout(() => {
                this.hideToastNotification(notification.id);
            }, autoHideDelay);
        }
        
        console.log('[PermissionNotificationManager] Toast通知已显示:', notification.id);
    }

    /**
     * 显示模态通知
     */
    async showModalNotification(notification: Notification): Promise<void> {
        const modalData: ModalData = {
            id: notification.id,
            title: notification.title,
            message: notification.message,
            priority: notification.priority,
            actions: notification.actions || [],
            onAction: (action: string) => this.handleNotificationAction(notification, action),
            onClose: () => this.markAsRead(notification.id)
        };
        
        // 触发模态显示事件
        window.dispatchEvent(new CustomEvent('showPermissionModal', {
            detail: modalData
        }));
        
        console.log('[PermissionNotificationManager] 模态通知已显示:', notification.id);
    }

    /**
     * 显示横幅通知
     */
    async showBannerNotification(notification: Notification): Promise<void> {
        const bannerData: BannerData = {
            id: notification.id,
            message: notification.message,
            priority: notification.priority,
            actions: notification.actions || [],
            onAction: (action: string) => this.handleNotificationAction(notification, action),
            onDismiss: () => this.markAsRead(notification.id)
        };
        
        // 触发横幅显示事件
        window.dispatchEvent(new CustomEvent('showPermissionBanner', {
            detail: bannerData
        }));
        
        console.log('[PermissionNotificationManager] 横幅通知已显示:', notification.id);
    }

    /**
     * 显示徽章通知
     */
    async showBadgeNotification(notification: Notification): Promise<void> {
        // 更新通知徽章计数
        const unreadCount = this.getUnreadCount();
        
        // 触发徽章更新事件
        window.dispatchEvent(new CustomEvent('updateNotificationBadge', {
            detail: { count: unreadCount }
        }));
        
        console.log('[PermissionNotificationManager] 徽章通知已更新:', unreadCount);
    }

    /**
     * 创建Toast元素
     */
    createToastElement(notification: Notification): HTMLElement {
        const toast = document.createElement('div');
        toast.className = `permission-toast toast-${notification.priority}`;
        toast.setAttribute('data-notification-id', notification.id);
        
        const iconClass = this.getNotificationIcon(notification.type);
        
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="toast-body">
                    <div class="toast-title">${notification.title}</div>
                    <div class="toast-message">${notification.message}</div>
                </div>
                <div class="toast-actions">
                    ${this.renderToastActions(notification)}
                    <button class="toast-close" onclick="permissionNotificationManager.hideToastNotification('${notification.id}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        return toast;
    }

    /**
     * 渲染Toast操作按钮
     */
    renderToastActions(notification: Notification): string {
        if (!notification.actions || notification.actions.length === 0) {
            return '';
        }
        
        return notification.actions.map(action => `
            <button class="toast-action ${action.primary ? 'primary' : 'secondary'}" 
                    onclick="permissionNotificationManager.handleNotificationAction('${notification.id}', '${action.action}')">
                ${action.label}
            </button>
        `).join('');
    }

    /**
     * 隐藏Toast通知
     */
    hideToastNotification(notificationId: string): void {
        const toastElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (toastElement) {
            toastElement.classList.add('toast-hiding');
            setTimeout(() => {
                toastElement.remove();
                this.activeToasts.delete(notificationId);
            }, 300);
        }
    }

    /**
     * 处理通知操作
     */
    async handleNotificationAction(notification: Notification | string, actionType: string): Promise<void> {
        console.log('[PermissionNotificationManager] 处理通知操作:', actionType);
        
        const notificationId = typeof notification === 'string' ? notification : notification.id;
        
        switch (actionType) {
            case 'viewRoleDetails':
                if (typeof notification !== 'string') {
                    this.showRoleDetails(notification.data);
                }
                break;
            
            case 'refreshPage':
                window.location.reload();
                break;
            
            case 'refreshMenu':
                this.triggerMenuRefresh();
                break;
            
            case 'viewPermissions':
                this.navigateToPermissions();
                break;
            
            case 'contactSupport':
                this.openSupportChat();
                break;
            
            default:
                console.warn('[PermissionNotificationManager] 未知的通知操作:', actionType);
        }
        
        // 标记为已读
        this.markAsRead(notificationId);
    }

    /**
     * 批量处理通知
     */
    processBatchNotifications(): void {
        if (this.batchQueue.length === 0) {
            return;
        }
        
        const batchNotification: Notification = {
            id: this.generateId(),
            type: this.notificationTypes.BATCH_UPDATE,
            priority: this.notificationPriorities.MEDIUM,
            title: '权限批量更新',
            message: `${this.batchQueue.length} 项权限变更`,
            data: { updates: [...this.batchQueue] },
            timestamp: Date.now(),
            displayMethod: this.displayMethods.TOAST,
            actions: [
                {
                    label: '查看详情',
                    action: 'viewBatchDetails',
                    primary: true
                }
            ]
        };
        
        this.showNotification(batchNotification);
        
        // 清空批量队列
        this.batchQueue = [];
        
        console.log('[PermissionNotificationManager] 批量通知已处理');
    }

    /**
     * 开始批量处理器
     */
    startBatchProcessor(): void {
        if (!this.config.enableBatchNotifications) {
            return;
        }
        
        setInterval(() => {
            this.processBatchNotifications();
        }, this.config.batchInterval);
    }

    /**
     * 播放通知效果
     */
    async playNotificationEffects(notification: Notification): Promise<void> {
        // 播放声音
        if (this.config.soundEnabled) {
            await this.playNotificationSound(notification.priority);
        }
        
        // 振动
        if (this.config.vibrationEnabled && 'vibrate' in navigator) {
            const vibrationPattern = this.getVibrationPattern(notification.priority);
            (navigator as any).vibrate(vibrationPattern);
        }
    }

    /**
     * 播放通知声音
     */
    async playNotificationSound(priority: string): Promise<void> {
        try {
            const soundFile = this.getSoundFile(priority);
            const audio = this.soundCache.get(soundFile);
            
            if (audio) {
                audio.currentTime = 0;
                await audio.play();
            }
        } catch (error) {
            console.warn('[PermissionNotificationManager] 播放声音失败:', error);
        }
    }

    /**
     * 预加载声音文件
     */
    preloadSounds(): void {
        const soundFiles = {
            low: '/sounds/notification-low.mp3',
            medium: '/sounds/notification-medium.mp3',
            high: '/sounds/notification-high.mp3',
            critical: '/sounds/notification-critical.mp3'
        };
        
        Object.entries(soundFiles).forEach(([priority, file]) => {
            const audio = new Audio(file);
            audio.preload = 'auto';
            this.soundCache.set(file, audio);
        });
    }

    /**
     * 获取声音文件
     */
    getSoundFile(priority: string): string {
        const soundFiles: Record<string, string> = {
            low: '/sounds/notification-low.mp3',
            medium: '/sounds/notification-medium.mp3',
            high: '/sounds/notification-high.mp3',
            critical: '/sounds/notification-critical.mp3'
        };
        
        return soundFiles[priority] || soundFiles.medium;
    }

    /**
     * 获取振动模式
     */
    getVibrationPattern(priority: string): number[] {
        const patterns: Record<string, number[]> = {
            low: [100],
            medium: [100, 50, 100],
            high: [200, 100, 200],
            critical: [300, 100, 300, 100, 300]
        };
        
        return patterns[priority] || patterns.medium;
    }

    /**
     * 获取显示方法
     */
    getDisplayMethod(type?: string, priority?: string): string {
        if (priority === this.notificationPriorities.CRITICAL) {
            return this.displayMethods.MODAL;
        }
        
        if (type === this.notificationTypes.ROLE_CHANGED) {
            return this.displayMethods.MODAL;
        }
        
        if (type === this.notificationTypes.SECURITY_ALERT) {
            return this.displayMethods.BANNER;
        }
        
        return this.displayMethods.TOAST;
    }

    /**
     * 获取通知图标
     */
    getNotificationIcon(type: string): string {
        const icons: Record<string, string> = {
            [this.notificationTypes.PERMISSION_GRANTED]: 'fas fa-check-circle',
            [this.notificationTypes.PERMISSION_REVOKED]: 'fas fa-times-circle',
            [this.notificationTypes.ROLE_CHANGED]: 'fas fa-user-cog',
            [this.notificationTypes.MENU_ACCESS_UPDATED]: 'fas fa-bars',
            [this.notificationTypes.SYSTEM_MAINTENANCE]: 'fas fa-tools',
            [this.notificationTypes.SECURITY_ALERT]: 'fas fa-shield-alt',
            [this.notificationTypes.BATCH_UPDATE]: 'fas fa-layer-group'
        };
        
        return icons[type] || 'fas fa-bell';
    }

    /**
     * 获取通知操作
     */
    getNotificationActions(type: string): NotificationAction[] {
        const actions: Record<string, NotificationAction[]> = {
            [this.notificationTypes.PERMISSION_GRANTED]: [
                { label: '查看权限', action: 'viewPermissions', primary: true }
            ],
            [this.notificationTypes.PERMISSION_REVOKED]: [
                { label: '联系支持', action: 'contactSupport', primary: true }
            ],
            [this.notificationTypes.SECURITY_ALERT]: [
                { label: '查看详情', action: 'viewSecurityDetails', primary: true },
                { label: '联系支持', action: 'contactSupport', primary: false }
            ]
        };
        
        return actions[type] || [];
    }

    /**
     * 获取系统通知操作
     */
    getSystemNotificationActions(type?: string): NotificationAction[] {
        if (type === 'maintenance') {
            return [
                { label: '了解详情', action: 'viewMaintenanceDetails', primary: true }
            ];
        }
        
        return [
            { label: '确定', action: 'dismiss', primary: true }
        ];
    }

    /**
     * 格式化权限消息
     */
    formatPermissionMessage(resource: string, action: string): string {
        const actionText = action === 'grant' ? '获得了' : '失去了';
        return `您${actionText}对 "${resource}" 的访问权限`;
    }

    /**
     * 格式化菜单变更消息
     */
    formatMenuChangeMessage(menuChanges: MenuChanges): string {
        const addedCount = menuChanges.added?.length || 0;
        const removedCount = menuChanges.removed?.length || 0;
        
        if (addedCount > 0 && removedCount > 0) {
            return `新增 ${addedCount} 个菜单，移除 ${removedCount} 个菜单`;
        } else if (addedCount > 0) {
            return `新增 ${addedCount} 个可访问菜单`;
        } else if (removedCount > 0) {
            return `移除 ${removedCount} 个菜单访问权限`;
        }
        
        return '菜单访问权限已更新';
    }

    /**
     * 获取Toast容器
     */
    getToastContainer(): HTMLElement {
        let container = document.getElementById('permission-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'permission-toast-container';
            container.className = 'permission-toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * 添加到历史记录
     */
    addToHistory(notification: Notification): void {
        this.notificationHistory.unshift(notification);
        
        // 保持历史记录大小
        if (this.notificationHistory.length > this.maxHistorySize) {
            this.notificationHistory = this.notificationHistory.slice(0, this.maxHistorySize);
        }
        
        // 保存到本地存储
        this.saveNotificationHistory();
    }

    /**
     * 标记为已读
     */
    markAsRead(notificationId: string): void {
        const notification = this.notificationHistory.find(n => n.id === notificationId);
        if (notification) {
            notification.read = true;
            notification.readAt = Date.now();
            this.saveNotificationHistory();
        }
    }

    /**
     * 获取未读数量
     */
    getUnreadCount(): number {
        return this.notificationHistory.filter(n => !n.read).length;
    }

    /**
     * 清除相关缓存
     */
    clearRelatedCache(resource: string): void {
        const cache = new PermissionCache();
        cache.clearByPattern(resource);
    }

    /**
     * 清除所有权限缓存
     */
    clearAllPermissionCache(): void {
        const cache = new PermissionCache();
        cache.clear();
    }

    /**
     * 触发菜单刷新
     */
    triggerMenuRefresh(): void {
        window.dispatchEvent(new CustomEvent('refreshPermissionMenu'));
    }

    /**
     * 获取当前用户ID
     */
    getCurrentUserId(): string | null {
        try {
            const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
            return userInfo.id || userInfo.userId || null;
        } catch {
            return null;
        }
    }

    /**
     * 生成ID
     */
    generateId(): string {
        return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * 加载通知设置
     */
    loadNotificationSettings(): void {
        try {
            const settings = JSON.parse(localStorage.getItem('notificationSettings') || '{}');
            this.config = { ...this.config, ...settings };
        } catch (error) {
            console.warn('[PermissionNotificationManager] 加载通知设置失败:', error);
        }
    }

    /**
     * 保存通知设置
     */
    saveNotificationSettings(): void {
        try {
            localStorage.setItem('notificationSettings', JSON.stringify(this.config));
        } catch (error) {
            console.warn('[PermissionNotificationManager] 保存通知设置失败:', error);
        }
    }

    /**
     * 保存通知历史
     */
    saveNotificationHistory(): void {
        try {
            const historyToSave = this.notificationHistory.slice(0, 50); // 只保存最近50条
            localStorage.setItem('notificationHistory', JSON.stringify(historyToSave));
        } catch (error) {
            console.warn('[PermissionNotificationManager] 保存通知历史失败:', error);
        }
    }

    /**
     * 加载通知历史
     */
    loadNotificationHistory(): void {
        try {
            const history = JSON.parse(localStorage.getItem('notificationHistory') || '[]');
            this.notificationHistory = history;
        } catch (error) {
            console.warn('[PermissionNotificationManager] 加载通知历史失败:', error);
        }
    }

    /**
     * 添加监听器
     */
    addListener(listener: NotificationListener): void {
        this.listeners.add(listener);
    }

    /**
     * 移除监听器
     */
    removeListener(listener: NotificationListener): void {
        this.listeners.delete(listener);
    }

    /**
     * 通知监听器
     */
    notifyListeners(event: string, data: any): void {
        this.listeners.forEach(listener => {
            try {
                listener(event, data);
            } catch (error) {
                console.error('[PermissionNotificationManager] 监听器错误:', error);
            }
        });
    }

    /**
     * 更新配置
     */
    updateConfig(newConfig: Partial<NotificationConfig>): void {
        this.config = { ...this.config, ...newConfig };
        this.saveNotificationSettings();
        console.log('[PermissionNotificationManager] 配置已更新:', this.config);
    }

    /**
     * 获取通知历史
     */
    getNotificationHistory(limit: number = 20): Notification[] {
        return this.notificationHistory.slice(0, limit);
    }

    /**
     * 清除通知历史
     */
    clearNotificationHistory(): void {
        this.notificationHistory = [];
        localStorage.removeItem('notificationHistory');
        console.log('[PermissionNotificationManager] 通知历史已清除');
    }

    /**
     * 获取统计信息
     */
    getStats(): NotificationStats {
        const stats: NotificationStats = {
            total: this.notificationHistory.length,
            unread: this.getUnreadCount(),
            byType: {},
            byPriority: {},
            recentActivity: this.notificationHistory.slice(0, 10)
        };
        
        // 按类型统计
        this.notificationHistory.forEach(notification => {
            stats.byType[notification.type] = (stats.byType[notification.type] || 0) + 1;
            stats.byPriority[notification.priority] = (stats.byPriority[notification.priority] || 0) + 1;
        });
        
        return stats;
    }

    // 辅助方法（需要在实际项目中实现）
    private showRoleDetails(data: NotificationData): void {
        console.log('[PermissionNotificationManager] 显示角色详情:', data);
        // 实际实现中应该打开角色详情页面或模态框
    }

    private navigateToPermissions(): void {
        console.log('[PermissionNotificationManager] 导航到权限页面');
        // 实际实现中应该导航到权限管理页面
    }

    private openSupportChat(): void {
        console.log('[PermissionNotificationManager] 打开支持聊天');
        // 实际实现中应该打开客服聊天窗口
    }
}

// 创建全局通知管理器实例
const permissionNotificationManager = new PermissionNotificationManager();

// 暴露到全局作用域以便在HTML中使用
if (typeof window !== 'undefined') {
    (window as any).permissionNotificationManager = permissionNotificationManager;
}

export { permissionNotificationManager, PermissionNotificationManager };
export default permissionNotificationManager;