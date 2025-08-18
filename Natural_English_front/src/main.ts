import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.scss'
import { createPermissionDirective } from '@/utils/permissions'

const app = createApp(App)

// 注册权限指令
app.directive('permission', createPermissionDirective())

app.use(store)
app.use(router)
app.use(ElementPlus)

app.mount('#app')