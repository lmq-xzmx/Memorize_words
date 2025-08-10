<template>
  <div class="dashboard-container">
    <main class="dashboard-main">
      <div class="dashboard-content">
        <div class="user-profile-card">
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
          <button @click="showEditProfile = true" class="edit-btn">
            编辑个人信息
          </button>
        </div>
        
        <div class="quick-actions">
          <h2>快速操作</h2>
          <div class="action-cards">
            <div class="action-card">
              <h3>开始学习</h3>
              <p>开始您的英语学习之旅</p>
              <button class="action-btn">进入学习</button>
            </div>
            <div class="action-card">
              <h3>单词例句</h3>
              <p>通过例句学习单词用法</p>
              <button @click="goToWordExamples" class="action-btn">查看例句</button>
            </div>
            <div class="action-card">
              <h3>学习进度</h3>
              <p>查看您的学习进度和成就</p>
              <button class="action-btn">查看进度</button>
            </div>
            <div class="action-card">
              <h3>修改密码</h3>
              <p>更新您的账户密码</p>
              <button @click="showChangePassword = true" class="action-btn">修改密码</button>
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

export default {
  name: 'Dashboard',
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
  async mounted() {
    await this.loadUserProfile()
  },
  methods: {
    async loadUserProfile() {
      try {
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
      this.$router.push('/word-examples')
    },
    
    goToDevIndex() {
      this.$router.push('/admin/dev-index')
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
  padding-bottom: 80px; /* 为底部菜单栏留出空间 */
}

.dashboard-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.dashboard-main {
  padding: 20px;
  position: relative;
  z-index: 5;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.user-profile-card,
.quick-actions {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-profile-card:hover,
.quick-actions:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.user-profile-card h2,
.quick-actions h2 {
  margin-bottom: 25px;
  color: #2d3748;
  font-size: 24px;
  font-weight: 700;
  position: relative;
  padding-bottom: 10px;
}

.user-profile-card h2::after,
.quick-actions h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.profile-info {
  margin-bottom: 25px;
}

.info-item {
  display: flex;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.info-item label {
  width: 100px;
  color: #718096;
  font-weight: 600;
  font-size: 14px;
}

.info-item span {
  color: #2d3748;
  font-weight: 500;
}

.edit-btn,
.action-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.edit-btn:hover,
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.action-cards {
  display: grid;
  gap: 20px;
}

.action-card {
  padding: 25px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  text-align: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.action-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.action-card h3 {
  margin-bottom: 10px;
  color: #2d3748;
  font-weight: 700;
  font-size: 18px;
}

.action-card p {
  margin-bottom: 20px;
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
}

.dev-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.dev-card h3 {
  color: white;
}

.dev-card p {
  color: rgba(255, 255, 255, 0.9);
}

.dev-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.dev-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 450px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-content h3 {
  margin-bottom: 25px;
  color: #2d3748;
  font-size: 22px;
  font-weight: 700;
  text-align: center;
  position: relative;
  padding-bottom: 15px;
}

.modal-content h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2d3748;
  font-weight: 600;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.error-message {
  background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
  color: #c53030;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid rgba(197, 48, 48, 0.2);
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.cancel-btn {
  padding: 12px 24px;
  background: rgba(226, 232, 240, 0.8);
  color: #4a5568;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.cancel-btn:hover {
  background: rgba(226, 232, 240, 1);
  transform: translateY(-1px);
}

.save-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    padding: 0 10px;
  }
  
  .user-info {
    flex-direction: column;
    gap: 8px;
  }
}
</style>