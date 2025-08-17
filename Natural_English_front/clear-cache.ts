#!/usr/bin/env node

/**
 * 清除前端开发缓存脚本
 * 用于解决前端代码修改后未生效的问题
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

console.log('🧹 开始清除前端缓存...');

// 清除目录的函数
function removeDir(dirPath) {
  if (fs.existsSync(dirPath)) {
    try {
      fs.rmSync(dirPath, { recursive: true, force: true });
      console.log(`✅ 已清除: ${dirPath}`);
    } catch (error) {
      console.log(`❌ 清除失败: ${dirPath} - ${error.message}`);
    }
  } else {
    console.log(`ℹ️  目录不存在: ${dirPath}`);
  }
}

// 清除文件的函数
function removeFile(filePath) {
  if (fs.existsSync(filePath)) {
    try {
      fs.unlinkSync(filePath);
      console.log(`✅ 已清除: ${filePath}`);
    } catch (error) {
      console.log(`❌ 清除失败: ${filePath} - ${error.message}`);
    }
  }
}

try {
  // 1. 清除 Vite 缓存
  console.log('\n📦 清除 Vite 缓存...');
  removeDir('node_modules/.vite');
  removeDir('dist');
  removeDir('.vite');
  
  // 2. 清除 Node.js 缓存
  console.log('\n📦 清除 Node.js 缓存...');
  removeDir('node_modules/.cache');
  
  // 3. 清除 npm 缓存
  console.log('\n📦 清除 npm 缓存...');
  try {
    execSync('npm cache clean --force', { stdio: 'inherit' });
    console.log('✅ npm 缓存已清除');
  } catch (error) {
    console.log('❌ npm 缓存清除失败:', error.message);
  }
  
  // 4. 清除可能的临时文件
  console.log('\n📦 清除临时文件...');
  removeFile('.DS_Store');
  removeDir('.tmp');
  removeDir('tmp');
  
  // 5. 提示清除浏览器缓存
  console.log('\n🌐 请手动清除浏览器缓存:');
  console.log('   - Chrome/Edge: Ctrl+Shift+R 或 F12 -> Network -> Disable cache');
  console.log('   - Firefox: Ctrl+Shift+R 或 F12 -> Network -> 设置 -> Disable cache');
  console.log('   - Safari: Cmd+Option+R 或 开发 -> 清空缓存');
  
  console.log('\n✨ 缓存清除完成！建议重启开发服务器。');
  console.log('💡 运行 npm run dev 重新启动开发服务器');
  
} catch (error) {
  console.error('❌ 清除缓存时发生错误:', error.message);
  process.exit(1);
}