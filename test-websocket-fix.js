#!/usr/bin/env node

/**
 * WebSocket连接修复验证脚本 (使用curl测试)
 * 测试修复后的WebSocket URL是否正确
 */

const { exec } = require('child_process');

console.log('🚀 WebSocket连接修复验证测试');
console.log('测试时间:', new Date().toLocaleString());
console.log('=' .repeat(50));

// 测试WebSocket端点是否可达
function testWebSocketEndpoint() {
  return new Promise((resolve) => {
    console.log('🔗 测试WebSocket端点可达性...');
    
    // 测试修复后的权限WebSocket路径
    const correctPath = '/ws/permissions/anonymous';
    const oldIncorrectPath = '/ws/menu/anonymous'; // 修复前的错误路径
    
    console.log(`📡 修复后路径: ws://localhost:8000${correctPath}`);
    console.log(`🚫 修复前路径: ws://localhost:8000${oldIncorrectPath}`);
    
    // 使用curl测试HTTP升级到WebSocket
    const testCommand = `curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" http://localhost:8000${correctPath}`;
    
    exec(testCommand, { timeout: 5000 }, (error, stdout, stderr) => {
      console.log('\n📊 测试结果:');
      
      if (error) {
        if (error.code === 'TIMEOUT') {
          console.log('⏰ 连接超时 - 可能后端服务未启动');
        } else {
          console.log('❌ 连接错误:', error.message);
        }
        resolve(false);
        return;
      }
      
      if (stdout.includes('101 Switching Protocols') || stdout.includes('Upgrade: websocket')) {
        console.log('✅ 权限WebSocket端点响应正常');
        console.log('📈 服务器支持WebSocket协议升级');
        resolve(true);
      } else if (stdout.includes('404') || stdout.includes('Not Found')) {
        console.log('❌ 权限WebSocket端点不存在 (404)');
        console.log('💡 提示: 请确保后端权限WebSocket服务正在运行');
        resolve(false);
      } else {
        console.log('🤔 未知响应:');
        console.log(stdout.substring(0, 200));
        resolve(false);
      }
    });
  });
}

// 验证URL修复
function verifyUrlFix() {
  console.log('\n🔧 验证URL修复效果:');
  console.log('');
  
  // 检查修复后的代码
  const fs = require('fs');
  const path = require('path');
  
  try {
    const menuServicePath = path.join(__dirname, 'Natural_English_front/src/services/menuService.ts');
    const content = fs.readFileSync(menuServicePath, 'utf8');
    
    // 查找WebSocket URL构建代码
    const lines = content.split('\n');
    let foundUrlConstruction = false;
    let hasDoubleSlash = false;
    
    for (let i = 0; i < lines.length; i++) {
       const line = lines[i];
       if (line.includes('wsUrl') || (line.includes('baseUrl') && line.includes('this.config.url'))) {
         foundUrlConstruction = true;
         console.log(`📝 第${i + 1}行: ${line.trim()}`);
         
         if (line.includes('//menu/')) {
           hasDoubleSlash = true;
           console.log('❌ 发现双斜杠问题');
         }
       }
     }
    
    if (foundUrlConstruction) {
      if (!hasDoubleSlash) {
        console.log('✅ URL构建代码已修复，无双斜杠问题');
        return true;
      } else {
        console.log('❌ URL构建代码仍有双斜杠问题');
        return false;
      }
    } else {
      console.log('⚠️  未找到WebSocket URL构建代码');
      return false;
    }
    
  } catch (error) {
    console.log('❌ 读取文件失败:', error.message);
    return false;
  }
}

// 主测试函数
async function runTests() {
  try {
    // 验证代码修复
    const codeFixed = verifyUrlFix();
    
    // 测试端点可达性
    const endpointReachable = await testWebSocketEndpoint();
    
    // 输出总结
    console.log('\n' + '=' .repeat(50));
    console.log('📊 WebSocket修复验证总结:');
    console.log('');
    console.log(`🔧 前端配置修复: ${codeFixed ? '✅ 已修复' : '❌ 未修复'}`);
    console.log(`🔗 权限WebSocket端点: ${endpointReachable ? '✅ 可达' : '❌ 不可达'}`);
    
    if (codeFixed && endpointReachable) {
      console.log('\n🎯 修复验证结论: ✅ WebSocket修复成功！');
      console.log('   - 前端现在连接到权限WebSocket服务 (/ws/permissions/)');
      console.log('   - WebSocket端点可正常访问');
      console.log('   - 前端应该能够正常连接');
    } else if (codeFixed && !endpointReachable) {
      console.log('\n🎯 修复验证结论: ⚠️  前端配置已修复，但后端权限WebSocket服务可能未启动');
    } else if (!codeFixed) {
      console.log('\n🎯 修复验证结论: ❌ 前端配置修复不完整');
    }
    
    console.log('\n💡 建议:');
    if (!endpointReachable) {
      console.log('   - 确保后端服务在8000端口运行');
      console.log('   - 检查WebSocket路由配置');
    }
    if (codeFixed) {
      console.log('   - 刷新前端页面测试WebSocket连接');
      console.log('   - 查看浏览器控制台确认连接状态');
    }
    
  } catch (error) {
    console.error('❌ 测试执行失败:', error);
  }
}

// 运行测试
runTests().catch(console.error);