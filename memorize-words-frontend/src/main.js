import {
	createSSRApp
} from "vue";
import App from "./App.vue";
import permissionPlugin from "@/plugins/permission.js";
import "@/utils/routeGuard.js"; // 自动初始化路由守卫

export function createApp() {
	const app = createSSRApp(App);
	
	// 安装权限插件
	app.use(permissionPlugin);
	
	return {
		app,
	};
}
