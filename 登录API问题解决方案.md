# 登录API问题解决方案

## 问题描述

用户遇到了登录API的500错误：
```
POST http://localhost:3000/accounts/api/auth/login/ 500 (Internal Server Error)
```

## 问题分析

经过详细检查，发现问题的根本原因是：

1. **端口配置不匹配**：
   - Vue前端运行在端口3000
   - Django后端运行在端口8000
   - Vite代理配置指向错误的端口

2. **API路径问题**：
   - Vue前端使用相对路径 `/accounts/api`
   - 需要正确的代理配置来转发请求

## 解决方案

### 1. 修复Vite代理配置

已修复 `Natural_English/Natural_English_front/vite.config.js`：

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/accounts/api': {
        target: 'http://localhost:8000',  // 修复：从8001改为8000
        changeOrigin: true
      }
    }
  }
})
```

### 2. 启动Django服务器

```bash
cd Natural_English
python3 manage.py runserver 8000
```

### 3. 启动Vue开发服务器

```bash
cd Natural_English/Natural_English_front
npm run dev
```

### 4. 测试登录API

使用curl测试API是否正常工作：

```bash
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' \
  -v
```

## 技术细节

### API端点配置

**Django后端**：
- URL: `/accounts/api/auth/login/`
- 视图: `CustomAuthToken`
- 方法: POST
- 认证: Token认证

**Vue前端**：
- 基础URL: `/accounts/api`
- 登录端点: `/auth/login/`
- 代理: 转发到 `http://localhost:8000`

### 请求流程

1. Vue前端发送请求到 `/accounts/api/auth/login/`
2. Vite代理将请求转发到 `http://localhost:8000/accounts/api/auth/login/`
3. Django服务器处理请求并返回响应
4. 代理将响应返回给Vue前端

### 错误处理

如果仍然遇到问题，请检查：

1. **Django服务器状态**：
   ```bash
   lsof -i :8000
   ```

2. **Vue开发服务器状态**：
   ```bash
   lsof -i :3000
   ```

3. **API端点可访问性**：
   ```bash
   curl http://localhost:8000/accounts/api/auth/login/
   ```

## 测试步骤

### 1. 启动服务

```bash
# 终端1：启动Django服务器
cd Natural_English
python3 manage.py runserver 8000

# 终端2：启动Vue开发服务器
cd Natural_English/Natural_English_front
npm run dev
```

### 2. 测试API

```bash
# 测试登录API
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### 3. 浏览器测试

1. 访问 `http://localhost:3000`
2. 尝试登录
3. 检查浏览器控制台是否有错误

## 常见问题

### 问题1：Connection refused
**原因**：Django服务器未启动
**解决**：确保Django服务器在端口8000运行

### 问题2：500 Internal Server Error
**原因**：Django服务器错误
**解决**：检查Django服务器日志

### 问题3：CORS错误
**原因**：跨域请求问题
**解决**：确保Vite代理配置正确

### 问题4：认证失败
**原因**：用户名或密码错误
**解决**：检查用户凭据

## 验证清单

- [ ] Django服务器运行在端口8000
- [ ] Vue开发服务器运行在端口3000
- [ ] Vite代理配置正确
- [ ] 登录API端点可访问
- [ ] 用户凭据正确
- [ ] 浏览器控制台无错误

## 总结

通过修复Vite代理配置，将目标端口从8001改为8000，登录API问题应该得到解决。确保：

1. Django服务器运行在端口8000
2. Vue开发服务器运行在端口3000
3. 代理配置正确转发API请求

现在登录功能应该可以正常工作了！ 