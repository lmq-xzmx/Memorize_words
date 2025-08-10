#!/usr/bin/env node
/**
 * 简单Vue路由测试脚本
 */

const fs = require('fs')
const path = require('path')

console.log('🔍 检查Vue路由配置...')

// 检查main.js文件
const mainJsPath = path.join(__dirname, 'Natural_English_front', 'main.js')
if (fs.existsSync(mainJsPath)) {
  const mainJsContent = fs.readFileSync(mainJsPath, 'utf8')
  
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
} else {
  console.log('❌ WordChallenge组件文件不存在')
}

console.log('\n📋 配置总结:')
console.log('- 路由: /words/word-challenge/')
console.log('- 组件: WordChallenge')
console.log('- 重定向: /words/word-challenge -> /words/word-challenge/')

console.log('\n🎯 解决方案:')
console.log('1. 清除浏览器缓存')
console.log('2. 重启Vue开发服务器')
console.log('3. 访问: http://localhost:5173/#/words/word-challenge/')

console.log('\n✨ 配置完成！') 