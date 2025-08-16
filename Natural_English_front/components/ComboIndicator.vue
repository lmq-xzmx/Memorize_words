<template>
  <div class="dashboard-container">
    <!-- 权限状态提示 -->
    <div v-if="!$isAuthenticated()" class="auth-warning">
      <p>⚠️ 您的登录状态异常，请重新登录</p>
      <button @click="$router.push('/login')" class="btn-primary">重新登录</button>
    </div>
    
    <main class="dashboard-main">
      <div class="dashboard-content">
        <div class="user-profile-card" v-if="user">
          <h2>个人信息</h2>
          <div class="profile-info">
            <div class="info-item">
              <label>用户名:</label>
              <span>{{ user?.username }}</span>
            </div>
            <div class="info-item">
              <label>真实姓名:</label>
              <span>{{ user?.real_name }}</span>
            </div>
            <div class="info-item">
              <label>邮箱:</label>
              <span>{{ user?.email }}</span>
            </div>
            <div class="info-item">
              <label>角色:</label>
              <span>{{ getRoleText(user?.role) }}</span>
            </div>
            <div v-if="user?.grade_level" class="info-item">
              <label>年级:</label>
              <span>{{ user.grade_level }}</span>
            </div>
            <div v-if="user?.school" class="info-item">
              <label>学校:</label>
              <span>{{ user.school }}</span>
            </div>
            <div v-if="user?.class_name" class="info-item">
              <label>班级:</label>
              <span>{{ user.class_name }}</span>
            </div>
          </div>
          <button 
            v-permission="'change_own_profile'"
            @click="showEditProfile = true" 
            class="edit-btn"
          >
            编辑个人信息
          </button>
        </div>
        
        <!-- 用户学习目标组件 -->
        <UserLearningGoalWidget />
        
        <div class="quick-actions">
          <h2>快速操作</h2>
          <div class="action-cards">
            <div 
              v-permission="'view_word_learning'"
              class="action-card"
            >
              <h3>开始学习</h3>
              <p>开始您的英语学习之旅</p>
              <button @click="navigateWithPermission('/word-learning')" class="action-btn">进入学习</button>
            </div>
            <div 
              v-permission="'view_word_examples'"
              class="action-card"
            >
              <h3>单词例句</h3>
              <p>通过例句学习单词用法</p>
              <button @click="goToWordExamples" class="action-btn">查看例句</button>
            </div>
            <div 
              v-permission="'view_own_profile'"
              class="action-card"
            >
              <h3>学习进度</h3>
              <p>查看您的学习进度和成就</p>
              <button @click="navigateWithPermission('/profile')" class="action-btn">查看进度</button>
            </div>
            <div 
              v-permission="'view_analytics'"
              class="action-card"
            >
              <h3>📊 数据分析</h3>
              <p>查看用户参与度和学习分析</p>
              <button @click="goToAnalytics" class="action-btn">查看分析</button>
            </div>
            <div 
              v-permission="'change_own_settings'"
              class="action-card"
            >
              <h3>修改密码</h3>
              <p>更新您的账户密码</p>
              <button @click="showChangePassword = true" class="action-btn">修改密码</button>
            </div>
            
            <!-- 教师专用功能 -->
            <div 
              v-role="['teacher', 'dean', 'academic_director', 'research_leader']"
              class="action-card teacher-card"
            >
              <h3>🎓 教学管理</h3>
              <p>资源管理和教学工具</p>
              <button @click="navigateWithPermission('/resource-auth')" class="action-btn">教学管理</button>
            </div>
            
            <!-- 管理员专用功能 -->
            <div 
              v-role="['admin', 'dean']"
              class="action-card admin-card"
            >
              <h3>⚙️ 系统管理</h3>
              <p>系统配置和管理面板</p>
              <button @click="goToDevIndex" class="action-btn">系统管理</button>
            </div>
            
            <div class="action-card dev-card">
              <h3>🚀 开发期首页</h3>
              <p>快速定位待开发或优化的页面</p>
              <button @click="goToDevIndex" class="action-btn dev-btn">进入开发</button>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 编辑个人信息弹窗 -->
    <div v-if="showEditProfile" class="modal-overlay" @click="showEditProfile = false">
      <div class="modal-content" @click.stop>
        <h3>编辑个人信息</h3>
        <form @submit.prevent="handleUpdateProfile">
          <div class="form-group">
            <label>邮箱:</label>
            <input v-model="editForm.email" type="email" required />
          </div>
          <div class="form-group">
            <label>真实姓名:</label>
            <input v-model="editForm.real_name" type="text" required />
          </div>
          <div class="form-group">
            <label>手机号:</label>
            <input v-model="editForm.phone" type="tel" />
          </div>
          <div class="form-group">
            <label>年级:</label>
            <input v-model="editForm.grade_level" type="text" />
          </div>
          <div class="form-group">
            <label>学校:</label>
            <input v-model="editForm.school" type="text" />
          </div>
          <div class="form-group">
            <label>班级:</label>
            <input v-model="editForm.class_name" type="text" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showEditProfile = false" class="cancel-btn">
              取消
            </button>
            <button type="submit" class="save-btn" :disabled="updateLoading">
              {{ updateLoading ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <div class="modal-content" @click.stop>
        <h3>修改密码</h3>
        <form @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label>原密码:</label>
            <input v-model="passwordForm.old_password" type="password" required />
          </div>
          <div class="form-group">
            <label>新密码:</label>
            <input v-model="passwordForm.new_password" type="password" required />
          </div>
          <div class="form-group">
            <label>确认新密码:</label>
            <input v-model="passwordForm.confirm_password" type="password" required />
          </div>
          <div v-if="passwordError" class="error-message">
            {{ passwordError }}
          </div>
          <div class="modal-actions">
            <button type="button" @click="showChangePassword = false" class="cancel-btn">
              取消
            </button>
            <button type="submit" class="save-btn" :disabled="passwordLoading">
              {{ passwordLoading ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI, userAPI } from '../utils/api.js'
import permissionMixin from '../mixins/permissionMixin.js'
import UserLearningGoalWidget from '../components/UserLearningGoalWidget.vue'

export default {
  name: 'Dashboard',
  components: {
    UserLearningGoalWidget
  },
  mixins: [permissionMixin],
  data() {
    return {
      user: null,
      showEditProfile: false,
      showChangePassword: false,
      updateLoading: false,
      passwordLoading: false,
      passwordError: '',
      editForm: {
        email: '',
        real_name: '',
        phone: '',
        grade_level: '',
        school: '',
        class_name: ''
      },
      passwordForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
    }
  },
  computed: {
    // 移除重复定义的计算属性，使用混入中的方法
    userRoleDisplayName() {
      return this.getRoleText(this.currentUser?.role)
    }
  },
  async mounted() {
    await this.loadUserProfile()
    // 监听权限变更
    this.$onPermissionChange = this.handlePermissionChange
  },
  beforeDestroy() {
    // 清理事件监听
    this.$onPermissionChange = null
  },
  methods: {
    async loadUserProfile() {
      try {
        // 检查认证状态
        if (!this.$isAuthenticated()) {
          this.$router.push('/login')
          return
        }
        
        // 先从本地存储获取用户信息
        const localUser = localStorage.getItem('user')
        if (localUser) {
          this.user = JSON.parse(localUser)
          this.initEditForm()
        }
        
        // 从服务器获取最新用户信息
        const userProfile = await userAPI.getProfile()
        this.user = userProfile
        localStorage.setItem('user', JSON.stringify(userProfile))
        this.initEditForm()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        if (error.response?.status === 401) {
          // Token无效，清除认证信息并重定向
          this.$showError('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          this.$router.push('/login')
        }
      }
    },
    
    navigateWithPermission(route) {
      if (this.$canAccessPage(route)) {
        this.$router.push(route)
      } else {
        this.$showError(`您没有权限访问页面：${route}`)
      }
    },
    
    handlePermissionChange(user) {
      if (!user) {
        this.$router.push('/login')
      } else {
        this.loadUserProfile()
      }
    },
    
    initEditForm() {
      if (this.user) {
        this.editForm = {
          email: this.user.email || '',
          real_name: this.user.real_name || '',
          phone: this.user.phone || '',
          grade_level: this.user.grade_level || '',
          school: this.user.school || '',
          class_name: this.user.class_name || ''
        }
      }
    },
    
    async handleUpdateProfile() {
      this.updateLoading = true
      try {
        const updatedUser = await userAPI.updateProfile(this.editForm)
        this.user = updatedUser
        localStorage.setItem('user', JSON.stringify(updatedUser))
        this.showEditProfile = false
        alert('个人信息更新成功！')
      } catch (error) {
        console.error('更新个人信息失败:', error)
        alert('更新失败，请稍后重试')
      } finally {
        this.updateLoading = false
      }
    },
    
    async handleChangePassword() {
      if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
        this.passwordError = '两次输入的新密码不一致'
        return
      }
      
      this.passwordLoading = true
      this.passwordError = ''
      
      try {
        await userAPI.changePassword(this.passwordForm)
        this.showChangePassword = false
        this.passwordForm = {
          old_password: '',
          new_password: '',
          confirm_password: ''
        }
        alert('密码修改成功！')
      } catch (error) {
        console.error('修改密码失败:', error)
        this.passwordError = error.old_password?.[0] || error.confirm_password?.[0] || '修改失败，请稍后重试'
      } finally {
        this.passwordLoading = false
      }
    },
    
    async handleLogout() {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        // 清除本地存储
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // 跳转到登录页
        this.$router.push('/login')
      }
    },
    
    getRoleText(role) {
      const roleMap = {
        student: '学生',
        teacher: '教师',
        admin: '管理员'
      }
      return roleMap[role] || role
    },
    
    goToWordExamples() {
      this.$navigateWithPermission('/word-examples')
    },
    
    goToDevIndex() {
      this.$navigateWithPermission('/admin/dev-index')
    },
    
    goToAnalytics() {
      this.$navigateWithPermission('/analytics')
    }
  }
}
</script>

