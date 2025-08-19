import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.scss'
import { PermissionDirective } from './directives/permission'
import { installApiPermissionInterceptor } from './utils/apiPermissionInterceptor'

const app = createApp(App)

// 注册权限指令
app.use(PermissionDirective)

// 安装API权限拦截器
installApiPermissionInterceptor()

app.use(store)
app.use(router)
app.use(ElementPlus)

app.mount('#app')