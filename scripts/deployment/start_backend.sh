#!/bin/bash

# Django后端启动脚本 - 强制使用8000端口
# 如果端口被占用，会尝试终止占用进程并重新启动

PORT=8000
PROJECT_DIR="/Users/xzmx/Downloads/my-project/Memorize_words"

echo "=== Django后端启动脚本 ==="
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

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
elif [ -d "env" ]; then
    echo "激活虚拟环境..."
    source env/bin/activate
else
    echo "警告: 未找到虚拟环境，使用系统Python"
fi

# 检查Django是否已安装
if ! python -c "import django" 2>/dev/null; then
    echo "错误: Django未安装，请先安装依赖"
    echo "运行: pip install -r requirements.txt"
    exit 1
fi

# 运行数据库迁移
echo "运行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 收集静态文件（生产环境）
if [ "$1" = "--production" ]; then
    echo "收集静态文件..."
    python manage.py collectstatic --noinput
fi

# 启动Django开发服务器
echo "启动Django开发服务器在端口 $PORT..."
echo "访问地址: http://127.0.0.1:$PORT"
echo "按 Ctrl+C 停止服务器"
echo "========================"

# 强制使用指定端口启动
python manage.py runserver 127.0.0.1:$PORT