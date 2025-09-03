const state = {
  // 应用加载状态
  loading: false,
  // 网络状态
  networkStatus: true,
  // 系统信息
  systemInfo: uni.getStorageSync('systemInfo') || {},
  // 当前页面路径
  currentPage: '',
  // 页面栈
  pageStack: [],
  // 全局配置
  globalConfig: {
    // API基础URL
    baseURL: 'http://127.0.0.1:8003',
    // 请求超时时间
    timeout: 10000,
    // 是否显示加载提示
    showLoading: true,
    // 是否显示错误提示
    showError: true
  },
  // 主题配置
  theme: {
    primaryColor: '#007aff',
    backgroundColor: '#f5f5f5',
    textColor: '#333333',
    borderColor: '#e5e5e5'
  }
}

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_NETWORK_STATUS(state, status) {
    state.networkStatus = status
  },
  
  SET_SYSTEM_INFO(state, info) {
    state.systemInfo = info
    uni.setStorageSync('systemInfo', info)
  },
  
  SET_CURRENT_PAGE(state, page) {
    state.currentPage = page
  },
  
  PUSH_PAGE(state, page) {
    state.pageStack.push(page)
  },
  
  POP_PAGE(state) {
    state.pageStack.pop()
  },
  
  SET_GLOBAL_CONFIG(state, config) {
    state.globalConfig = { ...state.globalConfig, ...config }
  },
  
  SET_THEME(state, theme) {
    state.theme = { ...state.theme, ...theme }
  }
}

const actions = {
  // 显示加载状态
  showLoading({ commit }, title = '加载中...') {
    commit('SET_LOADING', true)
    uni.showLoading({
      title,
      mask: true
    })
  },
  
  // 隐藏加载状态
  hideLoading({ commit }) {
    commit('SET_LOADING', false)
    uni.hideLoading()
  },
  
  // 显示提示信息
  showToast({ state }, { title, icon = 'none', duration = 2000 }) {
    if (state.globalConfig.showError || icon === 'success') {
      uni.showToast({
        title,
        icon,
        duration
      })
    }
  },
  
  // 显示模态框
  showModal({ state }, { title, content, showCancel = true }) {
    return new Promise((resolve) => {
      uni.showModal({
        title,
        content,
        showCancel,
        success: (res) => {
          resolve(res.confirm)
        },
        fail: () => {
          resolve(false)
        }
      })
    })
  },
  
  // 获取系统信息
  getSystemInfo({ commit }) {
    return new Promise((resolve) => {
      uni.getSystemInfo({
        success: (res) => {
          commit('SET_SYSTEM_INFO', res)
          resolve(res)
        },
        fail: (err) => {
          console.error('获取系统信息失败:', err)
          resolve({})
        }
      })
    })
  },
  
  // 监听网络状态
  watchNetworkStatus({ commit, dispatch }) {
    // 获取当前网络状态
    uni.getNetworkType({
      success: (res) => {
        const isConnected = res.networkType !== 'none'
        commit('SET_NETWORK_STATUS', isConnected)
        
        if (!isConnected) {
          dispatch('showToast', {
            title: '网络连接异常',
            icon: 'none'
          })
        }
      }
    })
    
    // 监听网络状态变化
    uni.onNetworkStatusChange((res) => {
      commit('SET_NETWORK_STATUS', res.isConnected)
      
      if (res.isConnected) {
        dispatch('showToast', {
          title: '网络已连接',
          icon: 'success'
        })
      } else {
        dispatch('showToast', {
          title: '网络连接断开',
          icon: 'none'
        })
      }
    })
  },
  
  // 页面导航
  navigateTo({ commit }, { url, params = {} }) {
    let queryString = ''
    if (Object.keys(params).length > 0) {
      queryString = '?' + Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
    }
    
    const fullUrl = url + queryString
    
    return new Promise((resolve, reject) => {
      uni.navigateTo({
        url: fullUrl,
        success: (res) => {
          commit('PUSH_PAGE', fullUrl)
          commit('SET_CURRENT_PAGE', fullUrl)
          resolve(res)
        },
        fail: (err) => {
          console.error('页面跳转失败:', err)
          reject(err)
        }
      })
    })
  },
  
  // 页面重定向
  redirectTo({ commit }, { url, params = {} }) {
    let queryString = ''
    if (Object.keys(params).length > 0) {
      queryString = '?' + Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
    }
    
    const fullUrl = url + queryString
    
    return new Promise((resolve, reject) => {
      uni.redirectTo({
        url: fullUrl,
        success: (res) => {
          commit('SET_CURRENT_PAGE', fullUrl)
          resolve(res)
        },
        fail: (err) => {
          console.error('页面重定向失败:', err)
          reject(err)
        }
      })
    })
  },
  
  // 切换标签页
  switchTab({ commit }, url) {
    return new Promise((resolve, reject) => {
      uni.switchTab({
        url,
        success: (res) => {
          commit('SET_CURRENT_PAGE', url)
          resolve(res)
        },
        fail: (err) => {
          console.error('切换标签页失败:', err)
          reject(err)
        }
      })
    })
  },
  
  // 返回上一页
  navigateBack({ commit }, delta = 1) {
    return new Promise((resolve, reject) => {
      uni.navigateBack({
        delta,
        success: (res) => {
          for (let i = 0; i < delta; i++) {
            commit('POP_PAGE')
          }
          resolve(res)
        },
        fail: (err) => {
          console.error('返回上一页失败:', err)
          reject(err)
        }
      })
    })
  },
  
  // 更新全局配置
  updateGlobalConfig({ commit }, config) {
    commit('SET_GLOBAL_CONFIG', config)
  },
  
  // 更新主题
  updateTheme({ commit }, theme) {
    commit('SET_THEME', theme)
  }
}

const getters = {
  loading: state => state.loading,
  networkStatus: state => state.networkStatus,
  systemInfo: state => state.systemInfo,
  currentPage: state => state.currentPage,
  pageStack: state => state.pageStack,
  globalConfig: state => state.globalConfig,
  theme: state => state.theme,
  
  // 是否为移动端
  isMobile: state => {
    const { platform } = state.systemInfo
    return platform === 'android' || platform === 'ios'
  },
  
  // 是否为小程序
  isMiniProgram: state => {
    const { platform } = state.systemInfo
    return platform === 'mp-weixin' || platform === 'mp-alipay' || platform === 'mp-baidu'
  },
  
  // 是否为H5
  isH5: state => {
    const { platform } = state.systemInfo
    return platform === 'h5'
  },
  
  // 状态栏高度
  statusBarHeight: state => {
    return state.systemInfo.statusBarHeight || 0
  },
  
  // 导航栏高度
  navigationBarHeight: state => {
    const { platform, statusBarHeight } = state.systemInfo
    if (platform === 'ios') {
      return 44
    } else if (platform === 'android') {
      return 48
    }
    return 44
  },
  
  // 安全区域
  safeArea: state => {
    return state.systemInfo.safeArea || {}
  },
  
  // 屏幕宽度
  screenWidth: state => {
    return state.systemInfo.screenWidth || 375
  },
  
  // 屏幕高度
  screenHeight: state => {
    return state.systemInfo.screenHeight || 667
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}