/**
 * 菜单定位计算工具
 * 统一管理所有菜单的位置计算逻辑
 */

import { getMenuZIndex } from './zIndexManager.js'

/**
 * 计算弹出菜单的位置
 * @param {HTMLElement} triggerElement - 触发元素
 * @param {Object} options - 配置选项
 * @returns {Object} 位置样式对象
 */
export function calculatePopupPosition(triggerElement, options = {}) {
  const {
    menuWidth = 200,
    menuHeight = 'auto',
    placement = 'top', // 'top', 'bottom', 'left', 'right'
    offset = 12,
    boundary = 16 // 距离屏幕边界的最小距离
  } = options

  if (!triggerElement) {
    console.warn('触发元素不存在')
    return {}
  }

  const rect = triggerElement.getBoundingClientRect()
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  
  let position = {
    position: 'fixed',
    zIndex: getMenuZIndex(false)
  }

  // 根据placement计算基础位置
  switch (placement) {
    case 'top':
      position = calculateTopPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
      break
    case 'bottom':
      position = calculateBottomPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
      break
    case 'left':
      position = calculateLeftPlacement(rect, menuWidth, offset, boundary, windowWidth)
      break
    case 'right':
      position = calculateRightPlacement(rect, menuWidth, offset, boundary, windowWidth)
      break
    default:
      position = calculateTopPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
  }

  // 添加最大高度限制
  if (menuHeight === 'auto') {
    position.maxHeight = 'calc(100vh - 120px)'
  }

  return position
}

/**
 * 计算顶部弹出位置
 */
function calculateTopPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight) {
  // 计算水平居中位置
  let leftPosition = rect.left + (rect.width / 2) - (menuWidth / 2)
  
  // 边界检查
  if (leftPosition < boundary) {
    leftPosition = boundary
  } else if (leftPosition + menuWidth > windowWidth - boundary) {
    leftPosition = windowWidth - menuWidth - boundary
  }
  
  // 垂直位置：显示在按钮上方
  const topPosition = rect.top - offset
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    bottom: (windowHeight - topPosition) + 'px',
    zIndex: getMenuZIndex(false)
  }
}

/**
 * 计算底部弹出位置
 */
function calculateBottomPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight) {
  // 计算水平居中位置
  let leftPosition = rect.left + (rect.width / 2) - (menuWidth / 2)
  
  // 边界检查
  if (leftPosition < boundary) {
    leftPosition = boundary
  } else if (leftPosition + menuWidth > windowWidth - boundary) {
    leftPosition = windowWidth - menuWidth - boundary
  }
  
  // 垂直位置：显示在按钮下方
  const topPosition = rect.bottom + offset
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    top: topPosition + 'px',
    zIndex: getMenuZIndex(false)
  }
}

/**
 * 计算左侧弹出位置
 */
function calculateLeftPlacement(rect, menuWidth, offset, boundary, windowWidth) {
  let leftPosition = rect.left - menuWidth - offset
  
  // 如果左侧空间不够，调整到右侧
  if (leftPosition < boundary) {
    leftPosition = rect.right + offset
    // 如果右侧也不够，则贴边显示
    if (leftPosition + menuWidth > windowWidth - boundary) {
      leftPosition = windowWidth - menuWidth - boundary
    }
  }
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    top: Math.max(rect.top, boundary) + 'px',
    zIndex: getMenuZIndex(false)
  }
}

/**
 * 计算右侧弹出位置
 */
function calculateRightPlacement(rect, menuWidth, offset, boundary, windowWidth) {
  let leftPosition = rect.right + offset
  
  // 如果右侧空间不够，调整到左侧
  if (leftPosition + menuWidth > windowWidth - boundary) {
    leftPosition = rect.left - menuWidth - offset
    // 如果左侧也不够，则贴边显示
    if (leftPosition < boundary) {
      leftPosition = boundary
    }
  }
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    top: Math.max(rect.top, boundary) + 'px',
    zIndex: getMenuZIndex(false)
  }
}

/**
 * 计算菜单位置
 * @param {HTMLElement} triggerElement - 触发元素
 * @param {HTMLElement} menuElement - 菜单元素
 * @param {Object} options - 配置选项
 * @returns {Object} 位置信息
 */
export function calculateMenuPosition(triggerElement, menuElement, options = {}) {
  const {
    placement = 'bottom-start',
    offset = 8,
    boundary = 'viewport',
    flip = true,
    shift = true,
    padding = 8
  } = options

  if (!triggerElement || !menuElement) {
    console.warn('calculateMenuPosition: 缺少必要的元素参数')
    return { top: 0, left: 0, placement: placement }
  }

  try {
    const triggerRect = triggerElement.getBoundingClientRect()
    const menuRect = menuElement.getBoundingClientRect()
    const viewport = getViewportSize()
    const boundaryRect = getBoundaryRect(boundary)
    
    // 基础位置计算
    let position = calculateBasePosition(triggerRect, menuRect, placement, offset)
    let finalPlacement = placement
    
    // 边界检测和调整
    if (flip || shift) {
      const adjusted = adjustPositionForBoundary(position, menuRect, boundaryRect, {
        flip,
        shift,
        padding,
        originalPlacement: placement
      })
      position = adjusted.position
      finalPlacement = adjusted.placement
    }
    
    return {
      ...position,
      placement: finalPlacement,
      isFlipped: finalPlacement !== placement
    }
  } catch (error) {
    console.error('计算菜单位置时出错:', error)
    return { top: 0, left: 0, placement: placement, isFlipped: false }
  }
}

/**
 * 计算二级菜单位置
 * @param {HTMLElement} parentMenu - 父菜单元素
 * @param {Object} options - 配置选项
 * @returns {Object} 位置样式对象
 */
export function calculateSubmenuPosition(parentMenu, options = {}) {
  const {
    menuWidth = 320,
    menuHeight = 'auto',
    offset = 8,
    boundary = 16,
    placement = 'right' // 'right', 'left', 'bottom', 'top'
  } = options

  if (!parentMenu) {
    console.warn('父菜单元素不存在')
    return {
      position: 'fixed',
      left: '50%',
      top: '50%',
      transform: 'translate(-50%, -50%)',
      zIndex: 1002
    }
  }

  const rect = parentMenu.getBoundingClientRect()
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  
  let position = {
    position: 'fixed',
    zIndex: getMenuZIndex(true)
  }
  
  // 根据placement计算位置
  switch (placement) {
    case 'right':
      position = calculateSubmenuRightPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
      break
    case 'left':
      position = calculateSubmenuLeftPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
      break
    case 'bottom':
      position = calculateSubmenuBottomPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
      break
    case 'top':
      position = calculateSubmenuTopPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
      break
    default:
      position = calculateSubmenuRightPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight)
  }
  
  // 添加最大高度限制
  if (menuHeight === 'auto') {
    position.maxHeight = `${Math.min(windowHeight - position.top - boundary, 400)}px`
  }
  
  return position
}

/**
 * 计算子菜单右侧弹出位置
 */
function calculateSubmenuRightPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight) {
  let leftPosition = rect.right + offset
  let topPosition = rect.top
  let transformOrigin = 'left top'
  
  // 如果右侧空间不够，则显示在左侧
  if (leftPosition + menuWidth > windowWidth - boundary) {
    leftPosition = rect.left - menuWidth - offset
    transformOrigin = 'right top'
    
    // 如果左侧也不够，则贴边显示
    if (leftPosition < boundary) {
      leftPosition = boundary
      transformOrigin = 'left top'
    }
  }
  
  // 垂直位置调整，确保不超出视口
  if (topPosition + 200 > windowHeight - boundary) { // 假设菜单高度约200px
    topPosition = Math.max(windowHeight - 200 - boundary, boundary)
  }
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    top: Math.max(topPosition, boundary) + 'px',
    transformOrigin,
    zIndex: getMenuZIndex(true)
  }
}

/**
 * 计算子菜单左侧弹出位置
 */
function calculateSubmenuLeftPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight) {
  let leftPosition = rect.left - menuWidth - offset
  let topPosition = rect.top
  let transformOrigin = 'right top'
  
  // 如果左侧空间不够，则显示在右侧
  if (leftPosition < boundary) {
    leftPosition = rect.right + offset
    transformOrigin = 'left top'
    
    // 如果右侧也不够，则贴边显示
    if (leftPosition + menuWidth > windowWidth - boundary) {
      leftPosition = windowWidth - menuWidth - boundary
      transformOrigin = 'right top'
    }
  }
  
  // 垂直位置调整
  if (topPosition + 200 > windowHeight - boundary) {
    topPosition = Math.max(windowHeight - 200 - boundary, boundary)
  }
  
  return {
    position: 'fixed',
    left: Math.max(leftPosition, boundary) + 'px',
    top: Math.max(topPosition, boundary) + 'px',
    transformOrigin,
    zIndex: getMenuZIndex(true)
  }
}

/**
 * 计算子菜单底部弹出位置
 */
function calculateSubmenuBottomPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight) {
  let leftPosition = rect.left
  let topPosition = rect.bottom + offset
  
  // 水平位置调整
  if (leftPosition + menuWidth > windowWidth - boundary) {
    leftPosition = windowWidth - menuWidth - boundary
  }
  leftPosition = Math.max(leftPosition, boundary)
  
  // 垂直位置调整
  if (topPosition + 200 > windowHeight - boundary) {
    topPosition = rect.top - 200 - offset
  }
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    top: Math.max(topPosition, boundary) + 'px',
    transformOrigin: 'left top',
    zIndex: getMenuZIndex(true)
  }
}

/**
 * 计算子菜单顶部弹出位置
 */
function calculateSubmenuTopPlacement(rect, menuWidth, offset, boundary, windowWidth, windowHeight) {
  let leftPosition = rect.left
  let topPosition = rect.top - 200 - offset // 假设菜单高度约200px
  
  // 水平位置调整
  if (leftPosition + menuWidth > windowWidth - boundary) {
    leftPosition = windowWidth - menuWidth - boundary
  }
  leftPosition = Math.max(leftPosition, boundary)
  
  // 垂直位置调整
  if (topPosition < boundary) {
    topPosition = rect.bottom + offset
  }
  
  return {
    position: 'fixed',
    left: leftPosition + 'px',
    top: Math.max(topPosition, boundary) + 'px',
    transformOrigin: 'left bottom',
    zIndex: getMenuZIndex(true)
  }
}

/**
 * 自动调整菜单位置
 * @param {HTMLElement} menuElement - 菜单元素
 * @param {HTMLElement} triggerElement - 触发元素
 * @param {Object} options - 配置选项
 */
export function autoAdjustMenuPosition(menuElement, triggerElement, options = {}) {
  if (!menuElement || !triggerElement) return
  
  const position = calculatePopupPosition(triggerElement, options)
  
  // 应用位置样式
  Object.assign(menuElement.style, position)
}

/**
 * 检查元素是否在视口内
 * @param {HTMLElement} element - 要检查的元素
 * @returns {boolean} 是否在视口内
 */
export function isElementInViewport(element) {
  if (!element) return false
  
  const rect = element.getBoundingClientRect()
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= window.innerHeight &&
    rect.right <= window.innerWidth
  )
}

/**
 * 获取最佳弹出方向
 * @param {HTMLElement} triggerElement - 触发元素
 * @param {number} menuWidth - 菜单宽度
 * @param {number} menuHeight - 菜单高度
 * @returns {string} 最佳方向
 */
export function getBestPlacement(triggerElement, menuWidth = 200, menuHeight = 200) {
  if (!triggerElement) return 'top'
  
  const rect = triggerElement.getBoundingClientRect()
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  
  const spaces = {
    top: rect.top,
    bottom: windowHeight - rect.bottom,
    left: rect.left,
    right: windowWidth - rect.right
  }
  
  // 优先选择空间最大的方向
  const bestDirection = Object.keys(spaces).reduce((a, b) => 
    spaces[a] > spaces[b] ? a : b
  )
  
  return bestDirection
}

/**
 * 防抖函数，用于优化位置计算性能
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 计算基础位置
 */
function calculateBasePosition(triggerRect, menuRect, placement, offset) {
  const positions = {
    'top': {
      top: triggerRect.top - menuRect.height - offset,
      left: triggerRect.left + (triggerRect.width - menuRect.width) / 2
    },
    'top-start': {
      top: triggerRect.top - menuRect.height - offset,
      left: triggerRect.left
    },
    'top-end': {
      top: triggerRect.top - menuRect.height - offset,
      left: triggerRect.right - menuRect.width
    },
    'bottom': {
      top: triggerRect.bottom + offset,
      left: triggerRect.left + (triggerRect.width - menuRect.width) / 2
    },
    'bottom-start': {
      top: triggerRect.bottom + offset,
      left: triggerRect.left
    },
    'bottom-end': {
      top: triggerRect.bottom + offset,
      left: triggerRect.right - menuRect.width
    },
    'left': {
      top: triggerRect.top + (triggerRect.height - menuRect.height) / 2,
      left: triggerRect.left - menuRect.width - offset
    },
    'right': {
      top: triggerRect.top + (triggerRect.height - menuRect.height) / 2,
      left: triggerRect.right + offset
    }
  }
  
  return positions[placement] || positions['bottom-start']
}

/**
 * 边界检测和位置调整
 */
function adjustPositionForBoundary(position, menuRect, boundaryRect, options) {
  const { flip, shift, padding = 8, originalPlacement } = options
  let adjustedPosition = { ...position }
  let finalPlacement = originalPlacement
  
  const menuWidth = menuRect.width
  const menuHeight = menuRect.height
  
  // 检测溢出情况
  const overflow = {
    top: adjustedPosition.top < boundaryRect.top + padding,
    bottom: adjustedPosition.top + menuHeight > boundaryRect.bottom - padding,
    left: adjustedPosition.left < boundaryRect.left + padding,
    right: adjustedPosition.left + menuWidth > boundaryRect.right - padding
  }
  
  // 垂直方向调整
  if (flip && (overflow.bottom || overflow.top)) {
    const canFlipUp = originalPlacement.includes('bottom') && 
                     position.top - menuHeight - padding >= boundaryRect.top
    const canFlipDown = originalPlacement.includes('top') && 
                       position.top + menuHeight + padding <= boundaryRect.bottom
    
    if (overflow.bottom && canFlipUp) {
      // 翻转到上方
      adjustedPosition.top = position.top - menuHeight - (options.offset || 8) * 2
      finalPlacement = originalPlacement.replace('bottom', 'top')
    } else if (overflow.top && canFlipDown) {
      // 翻转到下方
      adjustedPosition.top = position.top + menuHeight + (options.offset || 8) * 2
      finalPlacement = originalPlacement.replace('top', 'bottom')
    }
  }
  
  // 垂直方向位移调整
  if (shift) {
    if (adjustedPosition.top < boundaryRect.top + padding) {
      adjustedPosition.top = boundaryRect.top + padding
    } else if (adjustedPosition.top + menuHeight > boundaryRect.bottom - padding) {
      adjustedPosition.top = boundaryRect.bottom - menuHeight - padding
    }
  }
  
  // 水平方向调整
  if (flip && (overflow.left || overflow.right)) {
    const canFlipLeft = originalPlacement.includes('end') && 
                       position.left - menuWidth - padding >= boundaryRect.left
    const canFlipRight = originalPlacement.includes('start') && 
                        position.left + menuWidth + padding <= boundaryRect.right
    
    if (overflow.right && canFlipLeft) {
      // 翻转到左侧
      adjustedPosition.left = position.left - menuWidth
      finalPlacement = originalPlacement.replace('start', 'end')
    } else if (overflow.left && canFlipRight) {
      // 翻转到右侧
      adjustedPosition.left = position.left + menuWidth
      finalPlacement = originalPlacement.replace('end', 'start')
    }
  }
  
  // 水平方向位移调整
  if (shift) {
    if (adjustedPosition.left < boundaryRect.left + padding) {
      adjustedPosition.left = boundaryRect.left + padding
    } else if (adjustedPosition.left + menuWidth > boundaryRect.right - padding) {
      adjustedPosition.left = boundaryRect.right - menuWidth - padding
    }
  }
  
  return {
    position: adjustedPosition,
    placement: finalPlacement
  }
}

/**
 * 获取视口尺寸
 */
function getViewportSize() {
  return {
    width: window.innerWidth || document.documentElement.clientWidth,
    height: window.innerHeight || document.documentElement.clientHeight
  }
}

/**
 * 获取边界矩形
 */
function getBoundaryRect(boundary) {
  if (boundary === 'viewport') {
    return {
      top: 0,
      left: 0,
      right: window.innerWidth,
      bottom: window.innerHeight,
      width: window.innerWidth,
      height: window.innerHeight
    }
  }
  
  if (typeof boundary === 'string') {
    const element = document.querySelector(boundary)
    return element ? element.getBoundingClientRect() : getViewportSize()
  }
  
  if (boundary instanceof HTMLElement) {
    return boundary.getBoundingClientRect()
  }
  
  // 默认返回视口
  return {
    top: 0,
    left: 0,
    right: window.innerWidth,
    bottom: window.innerHeight,
    width: window.innerWidth,
    height: window.innerHeight
  }
}

/**
 * 创建位置观察器
 * @param {HTMLElement} element - 要观察的元素
 * @param {Function} callback - 位置变化回调
 * @returns {Function} 清理函数
 */
export function createPositionObserver(element, callback) {
  if (!element || !callback) return () => {}
  
  const debouncedCallback = debounce(callback, 16) // 约60fps
  
  // 监听窗口大小变化
  window.addEventListener('resize', debouncedCallback)
  window.addEventListener('scroll', debouncedCallback)
  
  // 返回清理函数
  return () => {
    window.removeEventListener('resize', debouncedCallback)
    window.removeEventListener('scroll', debouncedCallback)
  }
}