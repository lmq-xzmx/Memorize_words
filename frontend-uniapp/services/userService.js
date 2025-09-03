import request from '@/utils/request'

/**
 * 用户登录
 * @param {Object} loginForm 登录表单数据
 * @param {string} loginForm.username 用户名
 * @param {string} loginForm.password 密码
 */
export const login = (loginForm) => {
  return request.post('/api/auth/login/', loginForm)
}

/**
 * 用户注册
 * @param {Object} registerForm 注册表单数据
 * @param {string} registerForm.username 用户名
 * @param {string} registerForm.password 密码
 * @param {string} registerForm.email 邮箱
 * @param {string} registerForm.phone 手机号
 */
export const register = (registerForm) => {
  return request.post('/api/auth/register/', registerForm)
}

/**
 * 用户登出
 */
export const logout = () => {
  return request.post('/api/auth/logout/')
}

/**
 * 获取用户信息
 */
export const getUserInfo = () => {
  return request.get('/api/auth/user-info/')
}

/**
 * 更新用户信息
 * @param {Object} userInfo 用户信息
 */
export const updateUserInfo = (userInfo) => {
  return request.put('/api/auth/user-info/', userInfo)
}

/**
 * 修改密码
 * @param {Object} passwordForm 密码表单
 * @param {string} passwordForm.old_password 旧密码
 * @param {string} passwordForm.new_password 新密码
 */
export const changePassword = (passwordForm) => {
  return request.post('/api/auth/change-password/', passwordForm)
}

/**
 * 重置密码
 * @param {Object} resetForm 重置密码表单
 * @param {string} resetForm.email 邮箱
 */
export const resetPassword = (resetForm) => {
  return request.post('/api/auth/reset-password/', resetForm)
}

/**
 * 验证邮箱
 * @param {string} email 邮箱地址
 */
export const verifyEmail = (email) => {
  return request.post('/api/auth/verify-email/', { email })
}

/**
 * 验证手机号
 * @param {string} phone 手机号
 */
export const verifyPhone = (phone) => {
  return request.post('/api/auth/verify-phone/', { phone })
}

/**
 * 发送验证码
 * @param {Object} codeForm 验证码表单
 * @param {string} codeForm.type 验证码类型 (email/phone)
 * @param {string} codeForm.target 目标邮箱或手机号
 */
export const sendVerificationCode = (codeForm) => {
  return request.post('/api/auth/send-code/', codeForm)
}

/**
 * 验证验证码
 * @param {Object} verifyForm 验证表单
 * @param {string} verifyForm.type 验证码类型
 * @param {string} verifyForm.target 目标邮箱或手机号
 * @param {string} verifyForm.code 验证码
 */
export const verifyCode = (verifyForm) => {
  return request.post('/api/auth/verify-code/', verifyForm)
}

/**
 * 刷新token
 * @param {string} refreshToken 刷新token
 */
export const refreshToken = (refreshToken) => {
  return request.post('/api/auth/refresh-token/', { refresh_token: refreshToken })
}

/**
 * 获取用户角色
 */
export const getUserRoles = () => {
  return request.get('/api/auth/user-roles/')
}

/**
 * 获取用户权限
 */
export const getUserPermissions = () => {
  return request.get('/api/auth/user-permissions/')
}

/**
 * 上传头像
 * @param {string} filePath 文件路径
 */
export const uploadAvatar = (filePath) => {
  return request.upload('/api/auth/upload-avatar/', filePath, {}, {
    name: 'avatar'
  })
}

/**
 * 绑定第三方账号
 * @param {Object} bindForm 绑定表单
 * @param {string} bindForm.platform 平台 (wechat/qq/weibo)
 * @param {string} bindForm.openid 第三方openid
 * @param {string} bindForm.access_token 访问token
 */
export const bindThirdParty = (bindForm) => {
  return request.post('/api/auth/bind-third-party/', bindForm)
}

/**
 * 解绑第三方账号
 * @param {string} platform 平台名称
 */
export const unbindThirdParty = (platform) => {
  return request.post('/api/auth/unbind-third-party/', { platform })
}

/**
 * 获取第三方绑定状态
 */
export const getThirdPartyBindStatus = () => {
  return request.get('/api/auth/third-party-bind-status/')
}

/**
 * 检查用户名是否可用
 * @param {string} username 用户名
 */
export const checkUsernameAvailable = (username) => {
  return request.get('/api/auth/check-username/', { username })
}

/**
 * 检查邮箱是否可用
 * @param {string} email 邮箱
 */
export const checkEmailAvailable = (email) => {
  return request.get('/api/auth/check-email/', { email })
}

/**
 * 检查手机号是否可用
 * @param {string} phone 手机号
 */
export const checkPhoneAvailable = (phone) => {
  return request.get('/api/auth/check-phone/', { phone })
}

/**
 * 获取用户学习统计
 */
export const getUserLearningStats = () => {
  return request.get('/api/user/learning-stats/')
}

/**
 * 获取用户学习记录
 * @param {Object} params 查询参数
 * @param {number} params.page 页码
 * @param {number} params.page_size 每页数量
 * @param {string} params.start_date 开始日期
 * @param {string} params.end_date 结束日期
 */
export const getUserLearningRecords = (params = {}) => {
  return request.get('/api/user/learning-records/', params)
}

/**
 * 更新用户学习进度
 * @param {Object} progressData 进度数据
 * @param {string} progressData.lesson_id 课程ID
 * @param {number} progressData.progress 进度百分比
 * @param {number} progressData.score 得分
 */
export const updateLearningProgress = (progressData) => {
  return request.post('/api/user/update-progress/', progressData)
}

/**
 * 获取用户收藏列表
 * @param {Object} params 查询参数
 * @param {string} params.type 收藏类型 (word/article/video)
 * @param {number} params.page 页码
 * @param {number} params.page_size 每页数量
 */
export const getUserFavorites = (params = {}) => {
  return request.get('/api/user/favorites/', params)
}

/**
 * 添加收藏
 * @param {Object} favoriteData 收藏数据
 * @param {string} favoriteData.type 收藏类型
 * @param {string} favoriteData.item_id 项目ID
 */
export const addFavorite = (favoriteData) => {
  return request.post('/api/user/favorites/', favoriteData)
}

/**
 * 取消收藏
 * @param {string} favoriteId 收藏ID
 */
export const removeFavorite = (favoriteId) => {
  return request.delete(`/api/user/favorites/${favoriteId}/`)
}

/**
 * 获取用户设置
 */
export const getUserSettings = () => {
  return request.get('/api/user/settings/')
}

/**
 * 更新用户设置
 * @param {Object} settings 设置数据
 */
export const updateUserSettings = (settings) => {
  return request.put('/api/user/settings/', settings)
}

/**
 * 注销账号
 * @param {Object} deleteForm 注销表单
 * @param {string} deleteForm.password 密码确认
 * @param {string} deleteForm.reason 注销原因
 */
export const deleteAccount = (deleteForm) => {
  return request.post('/api/auth/delete-account/', deleteForm)
}