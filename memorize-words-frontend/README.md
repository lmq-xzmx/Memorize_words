# 记忆单词前端项目

基于uni-app框架开发的英语单词记忆学习平台前端应用，支持H5、微信小程序、安卓和iOS多端发布。

## 项目信息

- **项目名称**: 记忆单词
- **微信小程序AppID**: wxa7e913069496e09c
- **框架**: uni-app + Vue 3
- **构建工具**: Vite

## 支持平台

- H5网页版
- 微信小程序
- 支付宝小程序
- 百度小程序
- 字节跳动小程序
- QQ小程序
- 安卓App
- iOS App
- 鸿蒙App

## 开发环境

### 安装依赖
```bash
npm install
```

### 开发调试

```bash
# H5开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin

# 支付宝小程序开发
npm run dev:mp-alipay

# 百度小程序开发
npm run dev:mp-baidu

# 字节跳动小程序开发
npm run dev:mp-toutiao

# QQ小程序开发
npm run dev:mp-qq
```

### 生产构建

```bash
# H5构建
npm run build:h5

# 微信小程序构建
npm run build:mp-weixin

# 支付宝小程序构建
npm run build:mp-alipay

# 百度小程序构建
npm run build:mp-baidu

# 字节跳动小程序构建
npm run build:mp-toutiao

# QQ小程序构建
npm run build:mp-qq
```

## 项目结构

```
src/
├── pages/          # 页面文件
│   └── index/      # 首页
├── static/         # 静态资源
├── App.vue         # 应用入口组件
├── main.js         # 应用入口文件
├── manifest.json   # 应用配置文件
├── pages.json      # 页面路由配置
└── uni.scss        # 全局样式
```

## 后端接口

前端项目需要配合Django后端项目使用，后端项目位于上级目录。

## 开发说明

1. 使用uni-app框架，一套代码多端运行
2. 基于Vue 3 + Composition API开发
3. 支持TypeScript（可选）
4. 使用Vite作为构建工具，开发体验更佳
5. 遵循uni-app官方开发规范

## 注意事项

- 开发微信小程序时需要在微信开发者工具中导入项目
- 各平台的特殊API需要使用条件编译
- 发布到应用商店前需要配置相应的证书和签名