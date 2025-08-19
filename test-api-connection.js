#!/usr/bin/env node

/**
 * API连接测试脚本
 * 验证前端配置修复后的API连接状态
 */

const https = require('http');

// 测试API端点
const testEndpoints = [
  {
    name: '菜单配置API',
    url: 'http://127.0.0.1:8000/api/permissions/frontend-menu-config/',
    method: 'GET'
  },
  {
    name: '后端健康检查',
    url: 'http://127.0.0.1:8000/api/',
    method: 'GET'
  }
];

// 测试单个端点
function testEndpoint(endpoint) {
  return new Promise((resolve) => {
    const url = new URL(endpoint.url);
    
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: endpoint.method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'API-Test-Script/1.0'
      },
      timeout: 5000
    };

    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          name: endpoint.name,
          url: endpoint.url,
          status: res.statusCode,
          success: res.statusCode >= 200 && res.statusCode < 300,
          data: data.length > 0 ? data.substring(0, 200) + '...' : 'No data',
          headers: res.headers
        });
      });
    });

    req.on('error', (error) => {
      resolve({
        name: endpoint.name,
        url: endpoint.url,
        status: 'ERROR',
        success: false,
        error: error.message
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        name: endpoint.name,
        url: endpoint.url,
        status: 'TIMEOUT',
        success: false,
        error: 'Request timeout'
      });
    });

    req.end();
  });
}

// 运行所有测试
async function runTests() {
  console.log('🚀 开始API连接测试...');
  console.log('=' * 50);
  
  const results = [];
  
  for (const endpoint of testEndpoints) {
    console.log(`\n📡 测试: ${endpoint.name}`);
    console.log(`🔗 URL: ${endpoint.url}`);
    
    const result = await testEndpoint(endpoint);
    results.push(result);
    
    if (result.success) {
      console.log(`✅ 成功 - 状态码: ${result.status}`);
      if (result.data) {
        console.log(`📄 响应预览: ${result.data}`);
      }
    } else {
      console.log(`❌ 失败 - 状态: ${result.status}`);
      if (result.error) {
        console.log(`🚨 错误: ${result.error}`);
      }
    }
  }
  
  // 总结报告
  console.log('\n' + '=' * 50);
  console.log('📊 测试总结:');
  
  const successCount = results.filter(r => r.success).length;
  const totalCount = results.length;
  
  console.log(`✅ 成功: ${successCount}/${totalCount}`);
  console.log(`❌ 失败: ${totalCount - successCount}/${totalCount}`);
  
  if (successCount === totalCount) {
    console.log('\n🎉 所有API连接测试通过！前端配置修复成功！');
  } else {
    console.log('\n⚠️  部分API连接存在问题，需要进一步检查。');
  }
  
  return results;
}

// 执行测试
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { testEndpoint, runTests };