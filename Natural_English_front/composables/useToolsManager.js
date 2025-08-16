/**
 * 工具管理器 Composable
 * 管理开发工具的启用/禁用状态和用户偏好
 */

import { ref, computed, watch } from 'vue'
import { toolsMenuConfig } from '../config/menuConfig.js'
import { getCurrentUser } from '../utils/permission.js'

export function useToolsManager() {
  // 响应式状态
  const allDevTools = ref([])
  const selectedTool = ref(null)
  const userId = ref(null)
  
  // 计算属性
  const enabledTools = computed(() => {
    return allDevTools.value
      .filter(tool => tool.enabled)
      .map(tool => ({
        id: tool.id,
        name: tool.title,
        title: tool.title,
        path: tool.path,
        icon: tool.icon
      }))
  })
  
  const enabledCount = computed(() => {
    return allDevTools.value.filter(tool => tool.enabled).length
  })
  
  const totalCount = computed(() => {
    return allDevTools.value.length
  })
  
  // 初始化工具列表
  const initializeTools = () => {
    allDevTools.value = (toolsMenuConfig.items || []).map(item => ({
      ...item,
      enabled: false
    }))
  }
  
  // 获取用户ID
  const getUserId = () => {
    try {
      const userInfo = getCurrentUser()
      if (userInfo) {
        userId.value = userInfo.id || userInfo.user_id || 'default'
      } else {
        userId.value = 'default'
      }
    } catch (error) {
      console.error('获取用户ID失败:', error)
      userId.value = 'default'
    }
  }
  
  // 切换工具状态
  const toggleTool = (tool) => {
    const targetTool = allDevTools.value.find(t => t.id === tool.id)
    if (targetTool) {
      targetTool.enabled = !targetTool.enabled
      
      // 如果当前选中的工具被禁用，清除选择
      if (!targetTool.enabled && selectedTool.value === tool.id) {
        selectedTool.value = null
      }
      
      // 保存用户偏好
      saveUserPreferences()
    }
  }
  
  // 启用所有工具
  const enableAllTools = () => {
    allDevTools.value.forEach(tool => {
      tool.enabled = true
    })
    saveUserPreferences()
  }
  
  // 禁用所有工具
  const disableAllTools = () => {
    allDevTools.value.forEach(tool => {
      tool.enabled = false
    })
    selectedTool.value = null
    saveUserPreferences()
  }
  
  // 选择工具
  const selectTool = (tool) => {
    selectedTool.value = tool.id
    saveUserPreferences()
  }
  
  // 检查工具是否启用
  const isToolEnabled = (toolId) => {
    const tool = allDevTools.value.find(t => t.id === toolId)
    return tool ? tool.enabled : false
  }
  
  // 获取启用的工具
  const getEnabledTool = (toolId) => {
    return enabledTools.value.find(tool => tool.id === toolId)
  }
  
  // 保存用户偏好
  const saveUserPreferences = () => {
    try {
      if (!userId.value) {
        getUserId()
      }
      
      const preferences = {
        enabledMenuItems: enabledTools.value,
        selectedTool: selectedTool.value,
        toolsEnabled: allDevTools.value.map(tool => ({
          id: tool.id,
          enabled: tool.enabled
        })),
        lastUpdated: new Date().toISOString()
      }
      
      const storageKey = `menuPreferences_${userId.value}`
      localStorage.setItem(storageKey, JSON.stringify(preferences))
      
      console.log('工具偏好已保存:', preferences)
    } catch (error) {
      console.error('保存工具偏好失败:', error)
    }
  }
  
  // 加载用户偏好
  const loadUserPreferences = () => {
    try {
      getUserId()
      
      const storageKey = `menuPreferences_${userId.value}`
      const savedPreferences = localStorage.getItem(storageKey)
      
      if (savedPreferences) {
        const preferences = JSON.parse(savedPreferences)
        
        // 恢复选中的工具
        if (preferences.selectedTool) {
          selectedTool.value = preferences.selectedTool
        }
        
        // 恢复工具启用状态
        if (preferences.toolsEnabled) {
          allDevTools.value.forEach(tool => {
            const savedTool = preferences.toolsEnabled.find(t => t.id === tool.id)
            if (savedTool) {
              tool.enabled = savedTool.enabled
            }
          })
        }
        
        console.log('工具偏好已恢复:', preferences)
      }
    } catch (error) {
      console.error('加载工具偏好失败:', error)
    }
  }
  
  // 重置工具偏好
  const resetUserPreferences = () => {
    try {
      allDevTools.value.forEach(tool => {
        tool.enabled = false
      })
      selectedTool.value = null
      
      const storageKey = `menuPreferences_${userId.value}`
      localStorage.removeItem(storageKey)
      
      console.log('工具偏好已重置')
    } catch (error) {
      console.error('重置工具偏好失败:', error)
    }
  }
  
  // 导出工具配置
  const exportToolsConfig = () => {
    try {
      const config = {
        tools: allDevTools.value.map(tool => ({
          id: tool.id,
          title: tool.title,
          enabled: tool.enabled
        })),
        selectedTool: selectedTool.value,
        exportTime: new Date().toISOString()
      }
      
      const dataStr = JSON.stringify(config, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      
      const link = document.createElement('a')
      link.href = URL.createObjectURL(dataBlob)
      link.download = `tools-config-${userId.value}-${Date.now()}.json`
      link.click()
      
      console.log('工具配置已导出')
    } catch (error) {
      console.error('导出工具配置失败:', error)
    }
  }
  
  // 导入工具配置
  const importToolsConfig = (configData) => {
    try {
      const config = typeof configData === 'string' ? JSON.parse(configData) : configData
      
      if (config.tools && Array.isArray(config.tools)) {
        allDevTools.value.forEach(tool => {
          const importedTool = config.tools.find(t => t.id === tool.id)
          if (importedTool) {
            tool.enabled = importedTool.enabled
          }
        })
      }
      
      if (config.selectedTool) {
        selectedTool.value = config.selectedTool
      }
      
      saveUserPreferences()
      console.log('工具配置已导入')
    } catch (error) {
      console.error('导入工具配置失败:', error)
    }
  }
  
  // 获取工具统计信息
  const getToolsStats = () => {
    return {
      total: totalCount.value,
      enabled: enabledCount.value,
      disabled: totalCount.value - enabledCount.value,
      enabledPercentage: totalCount.value > 0 ? Math.round((enabledCount.value / totalCount.value) * 100) : 0
    }
  }
  
  // 监听用户变化
  watch(() => userId.value, (newUserId, oldUserId) => {
    if (newUserId && newUserId !== oldUserId) {
      loadUserPreferences()
    }
  })
  
  // 初始化
  initializeTools()
  
  return {
    // 状态
    allDevTools,
    enabledTools,
    selectedTool,
    userId,
    enabledCount,
    totalCount,
    
    // 方法
    toggleTool,
    enableAllTools,
    disableAllTools,
    selectTool,
    isToolEnabled,
    getEnabledTool,
    loadUserPreferences,
    saveUserPreferences,
    resetUserPreferences,
    exportToolsConfig,
    importToolsConfig,
    getToolsStats,
    initializeTools
  }
}