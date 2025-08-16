#!/bin/bash

# 前端启动脚本 - 强制使用3000端口
# 如果端口被占用，会尝试终止占用进程并重新启动

PORT=3000
PROJECT_DIR="/Users/xzmx/Downloads/my-project/Memorize_words/Natural_English_front"

echo "=== 前端启动脚本 ==="
echo "目标端口: $PORT"
echo "项目目录: $PROJECT_DIR"

# 切换到项目目录
cd "$PROJECT_DIR" || {
    echo "错误: 无法切换到项目目录 $PROJECT_DIR"
    exit 1
}

# 检查端口占用情况
echo "检查端口 $PORT 占用情况..."
PID=$(lsof -ti:$PORT)

if [ ! -z "$PID" ]; then
    echo "端口 $PORT 被进程 $PID 占用"
    echo "正在终止占用进程..."
    kill -9 $PID
    sleep 2
    
    # 再次检查
    PID=$(lsof -ti:$PORT)
    if [ ! -z "$PID" ]; then
        echo "警告: 端口 $PORT 仍被占用，强制终止..."
        sudo kill -9 $PID 2>/dev/null
        sleep 1
    fi
fi

# 检查Node.js是否已安装
if ! command -v node &> /dev/null; then
    echo "错误: Node.js未安装，请先安装Node.js"
    exit 1
fi

# 检查npm是否已安装
if ! command -v npm &> /dev/null; then
    echo "错误: npm未安装，请先安装npm"
    exit 1
fi

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "错误: 未找到package.json文件"
    exit 1
fi

# 检查node_modules是否存在，如果不存在则安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装项目依赖..."
    npm install
fi

# 清理缓存（可选）
if [ "$1" = "--fresh" ]; then
    echo "清理缓存..."
    npm run clear-cache 2>/dev/null || echo "缓存清理脚本不存在，跳过"
fi

# 设置环境变量强制使用指定端口
export PORT=$PORT
export VITE_PORT=$PORT

# 启动前端开发服务器
echo "启动前端开发服务器在端口 $PORT..."
echo "访问地址: http://localhost:$PORT"
echo "按 Ctrl+C 停止服务器"
echo "========================"

# 强制使用指定端口启动
npm run dev -- --port $PORT --host 0.0.0.0