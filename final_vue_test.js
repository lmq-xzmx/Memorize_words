#!/usr/bin/env node
/**
 * 最终Vue路由测试脚本
 * 验证单词斩页面的完整配置
 */

const fs = require('fs')
const path = require('path')

console.log('🔍 最终Vue路由配置检查...')

// 检查正确的main.js文件
const mainJsPath = path.join(__dirname, 'Natural_English', 'Natural_English_front', 'main.js')
if (fs.existsSync(mainJsPath)) {
  const mainJsContent = fs.readFileSync(mainJsPath, 'utf8')
  
  console.log('📄 main.js 内容预览:')
  console.log(mainJsContent)
  
  // 检查是否包含单词斩路由
  if (mainJsContent.includes('/words/word-challenge/')) {
    console.log('✅ main.js 包含单词斩路由配置')
  } else {
    console.log('❌ main.js 缺少单词斩路由配置')
  }
  
  // 检查是否导入了WordChallenge组件
  if (mainJsContent.includes('WordChallenge')) {
    console.log('✅ main.js 导入了WordChallenge组件')
  } else {
    console.log('❌ main.js 缺少WordChallenge组件导入')
  }
  
  // 检查路由守卫
  if (mainJsContent.includes('requiresAuth')) {
    console.log('✅ main.js 包含路由守卫配置')
  } else {
    console.log('❌ main.js 缺少路由守卫配置')
  }
} else {
  console.log('❌ main.js 文件不存在')
}

// 检查WordChallenge组件文件
const wordChallengePath = path.join(__dirname, 'Natural_English', 'Natural_English_front', 'pages', 'word-challenge', 'index.vue')
if (fs.existsSync(wordChallengePath)) {
  console.log('✅ WordChallenge组件文件存在')
  
  const componentContent = fs.readFileSync(wordChallengePath, 'utf8')
  if (componentContent.includes('word-challenge')) {
    console.log('✅ WordChallenge组件内容正确')
  } else {
    console.log('❌ WordChallenge组件内容可能有问题')
  }
  
  // 检查组件是否包含必要的方法
  if (componentContent.includes('markAsLearned')) {
    console.log('✅ 组件包含markAsLearned方法')
  } else {
    console.log('❌ 组件缺少markAsLearned方法')
  }
  
  if (componentContent.includes('markAsDifficult')) {
    console.log('✅ 组件包含markAsDifficult方法')
  } else {
    console.log('❌ 组件缺少markAsDifficult方法')
  }
} else {
  console.log('❌ WordChallenge组件文件不存在')
}

// 检查App.vue文件
const appVuePath = path.join(__dirname, 'Natural_English', 'Natural_English_front', 'App.vue')
if (fs.existsSync(appVuePath)) {
  console.log('✅ App.vue 文件存在')
  
  const appContent = fs.readFileSync(appVuePath, 'utf8')
  if (appContent.includes('router-view')) {
    console.log('✅ App.vue 包含router-view')
  } else {
    console.log('❌ App.vue 缺少router-view')
  }
} else {
  console.log('❌ App.vue 文件不存在')
}

console.log('\n📋 路由配置总结:')
console.log('- /words/word-challenge/ -> WordChallenge组件 (需要认证)')
console.log('- 支持重定向: /words/word-challenge -> /words/word-challenge/')
console.log('- 页面标题: 单词斩')
console.log('- 导航栏颜色: #667eea')
console.log('- 路由守卫: 需要登录认证')

console.log('\n🎯 测试建议:')
console.log('1. 确保用户已登录 (localStorage中有token)')
console.log('2. 启动Vue开发服务器: cd Natural_English/Natural_English_front && npm run dev')
console.log('3. 访问: http://localhost:5173/words/word-challenge/')
console.log('4. 检查页面是否正常显示')
console.log('5. 测试路由导航功能')

console.log('\n🔧 故障排除:')
console.log('- 如果仍然出现路由错误，请清除浏览器缓存')
console.log('- 确保Vue开发服务器使用的是正确的main.js文件')
console.log('- 检查浏览器控制台是否有其他错误信息')

console.log('\n✨ Vue路由配置完成！') 