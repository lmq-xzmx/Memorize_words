// HTTP请求工具类
class Request {
  constructor() {
    this.baseURL = 'http://127.0.0.1:8003'
    this.timeout = 10000
    this.header = {
      'Content-Type': 'application/json'
    }
  }
  
  // 请求拦截器
  interceptors = {
    request: {
      use: (fn) => {
        this.requestInterceptor = fn
      }
    },
    response: {
      use: (successFn, errorFn) => {
        this.responseSuccessInterceptor = successFn
        this.responseErrorInterceptor = errorFn
      }
    }
  }
  
  // 发送请求
  request(options) {
    return new Promise((resolve, reject) => {
      // 合并配置
      const config = {
        url: this.baseURL + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: { ...this.header, ...options.header },
        timeout: options.timeout || this.timeout,
        dataType: options.dataType || 'json',
        responseType: options.responseType || 'text'
      }
      
      // 添加token
      const token = uni.getStorageSync('token')
      if (token) {
        config.header.Authorization = `Bearer ${token}`
      }
      
      // 请求拦截
      if (this.requestInterceptor) {
        try {
          const interceptedConfig = this.requestInterceptor(config)
          Object.assign(config, interceptedConfig)
        } catch (error) {
          reject(error)
          return
        }
      }
      
      // 发送请求
      uni.request({
        ...config,
        success: (response) => {
          // 响应成功拦截
          if (this.responseSuccessInterceptor) {
            try {
              const interceptedResponse = this.responseSuccessInterceptor(response)
              resolve(interceptedResponse)
            } catch (error) {
              reject(error)
            }
          } else {
            resolve(response)
          }
        },
        fail: (error) => {
          // 响应失败拦截
          if (this.responseErrorInterceptor) {
            try {
              const interceptedError = this.responseErrorInterceptor(error)
              reject(interceptedError)
            } catch (err) {
              reject(err)
            }
          } else {
            reject(error)
          }
        }
      })
    })
  }
  
  // GET请求
  get(url, params = {}, options = {}) {
    const queryString = Object.keys(params)
      .map(key => `${key}=${encodeURIComponent(params[key])}`)
      .join('&')
    
    const fullUrl = queryString ? `${url}?${queryString}` : url
    
    return this.request({
      url: fullUrl,
      method: 'GET',
      ...options
    })
  }
  
  // POST请求
  post(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'POST',
      data,
      ...options
    })
  }
  
  // PUT请求
  put(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'PUT',
      data,
      ...options
    })
  }
  
  // DELETE请求
  delete(url, options = {}) {
    return this.request({
      url,
      method: 'DELETE',
      ...options
    })
  }
  
  // 上传文件
  upload(url, filePath, formData = {}, options = {}) {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync('token')
      const header = {
        ...options.header
      }
      
      if (token) {
        header.Authorization = `Bearer ${token}`
      }
      
      uni.uploadFile({
        url: this.baseURL + url,
        filePath,
        name: options.name || 'file',
        formData,
        header,
        success: (response) => {
          try {
            const data = JSON.parse(response.data)
            resolve({
              statusCode: response.statusCode,
              data
            })
          } catch (error) {
            resolve({
              statusCode: response.statusCode,
              data: response.data
            })
          }
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }
  
  // 下载文件
  download(url, options = {}) {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync('token')
      const header = {
        ...options.header
      }
      
      if (token) {
        header.Authorization = `Bearer ${token}`
      }
      
      uni.downloadFile({
        url: this.baseURL + url,
        header,
        success: (response) => {
          resolve(response)
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }
}

// 创建请求实例
const request = new Request()

// 请求拦截器
request.interceptors.request.use((config) => {
  // 显示加载提示
  if (config.showLoading !== false) {
    uni.showLoading({
      title: '加载中...',
      mask: true
    })
  }
  
  console.log('请求配置:', config)
  return config
})

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 隐藏加载提示
    uni.hideLoading()
    
    console.log('响应数据:', response)
    
    // 处理响应状态码
    if (response.statusCode === 200) {
      const { data } = response
      
      // 处理业务状态码
      if (data.code === 0 || data.success === true) {
        return data
      } else {
        // 业务错误
        const errorMessage = data.message || data.msg || '请求失败'
        uni.showToast({
          title: errorMessage,
          icon: 'none',
          duration: 2000
        })
        return Promise.reject(new Error(errorMessage))
      }
    } else if (response.statusCode === 401) {
      // 未授权，清除token并跳转到登录页
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      uni.showToast({
        title: '登录已过期，请重新登录',
        icon: 'none'
      })
      
      setTimeout(() => {
        uni.redirectTo({
          url: '/pages/login/login'
        })
      }, 1500)
      
      return Promise.reject(new Error('登录已过期'))
    } else if (response.statusCode === 403) {
      // 无权限
      uni.showToast({
        title: '无权限访问',
        icon: 'none'
      })
      return Promise.reject(new Error('无权限访问'))
    } else if (response.statusCode === 404) {
      // 资源不存在
      uni.showToast({
        title: '请求的资源不存在',
        icon: 'none'
      })
      return Promise.reject(new Error('请求的资源不存在'))
    } else if (response.statusCode >= 500) {
      // 服务器错误
      uni.showToast({
        title: '服务器错误，请稍后重试',
        icon: 'none'
      })
      return Promise.reject(new Error('服务器错误'))
    } else {
      // 其他错误
      uni.showToast({
        title: `请求失败 (${response.statusCode})`,
        icon: 'none'
      })
      return Promise.reject(new Error(`请求失败 (${response.statusCode})`))
    }
  },
  (error) => {
    // 隐藏加载提示
    uni.hideLoading()
    
    console.error('请求错误:', error)
    
    // 网络错误处理
    if (error.errMsg) {
      if (error.errMsg.includes('timeout')) {
        uni.showToast({
          title: '请求超时，请检查网络',
          icon: 'none'
        })
      } else if (error.errMsg.includes('fail')) {
        uni.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
      } else {
        uni.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    } else {
      uni.showToast({
        title: error.message || '未知错误',
        icon: 'none'
      })
    }
    
    return Promise.reject(error)
  }
)

// 导出请求实例
export default request

// 导出请求方法
export const { get, post, put, delete: del, upload, download } = request