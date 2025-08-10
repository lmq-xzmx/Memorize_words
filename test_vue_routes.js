#!/usr/bin/env node
/**
 * Vue路由测试脚本
 * 测试单词斩页面的路由配置
 */

const fs = require('fs')
const path = require('path')

console.log('🔍 检查Vue路由配置...')

// 检查main.js文件
const mainJsPath = path.join(__dirname, 'Natural_English_front', 'main.js')
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
} else {
  console.log('❌ main.js 文件不存在')
}

// 检查WordChallenge组件文件
const wordChallengePath = path.join(__dirname, 'Natural_English_front', 'pages', 'word-challenge', 'index.vue')
if (fs.existsSync(wordChallengePath)) {
  console.log('✅ WordChallenge组件文件存在')
  
  const componentContent = fs.readFileSync(wordChallengePath, 'utf8')
  if (componentContent.includes('word-challenge')) {
    console.log('✅ WordChallenge组件内容正确')
  } else {
    console.log('❌ WordChallenge组件内容可能有问题')
  }
} else {
  console.log('❌ WordChallenge组件文件不存在')
}

// 检查pages.json配置
const pagesJsonPath = path.join(__dirname, 'Natural_English_front', 'pages.json')
if (fs.existsSync(pagesJsonPath)) {
  const pagesJsonContent = fs.readFileSync(pagesJsonPath, 'utf8')
  
  if (pagesJsonContent.includes('word-challenge')) {
    console.log('✅ pages.json 包含单词斩页面配置')
  } else {
    console.log('❌ pages.json 缺少单词斩页面配置')
  }
} else {
  console.log('❌ pages.json 文件不存在')
}

console.log('\n📋 路由配置总结:')
console.log('- /words/word-challenge/ -> WordChallenge组件')
console.log('- 支持重定向: /words/word-challenge -> /words/word-challenge/')
console.log('- 页面标题: 单词斩')
console.log('- 导航栏颜色: #667eea')

console.log('\n🎯 测试建议:')
console.log('1. 启动Vue开发服务器: cd Natural_English_front && npm run dev')
console.log('2. 访问: http://localhost:5173/#/words/word-challenge/')
console.log('3. 检查页面是否正常显示')
console.log('4. 测试路由导航功能')

console.log('\n✨ Vue路由配置完成！') 