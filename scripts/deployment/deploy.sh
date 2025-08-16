#!/bin/bash

# 部署脚本 - Natural English Learning System
# 使用方法: ./deploy.sh [环境] [选项]
# 环境: dev, staging, production
# 选项: --build, --no-cache, --monitoring

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 默认参数
ENVIRONMENT="dev"
BUILD_FLAG=""
MONITORING_FLAG=""
NO_CACHE_FLAG=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        dev|staging|production)
            ENVIRONMENT="$1"
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --no-cache)
            NO_CACHE_FLAG="--no-cache"
            shift
            ;;
        --monitoring)
            MONITORING_FLAG="--profile monitoring"
            shift
            ;;
        -h|--help)
            echo "使用方法: $0 [环境] [选项]"
            echo "环境: dev, staging, production"
            echo "选项:"
            echo "  --build      强制重新构建镜像"
            echo "  --no-cache   构建时不使用缓存"
            echo "  --monitoring 启用监控服务"
            echo "  -h, --help   显示帮助信息"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

log_info "开始部署 Natural English Learning System"
log_info "环境: $ENVIRONMENT"
log_info "构建选项: $BUILD_FLAG $NO_CACHE_FLAG"
log_info "监控选项: $MONITORING_FLAG"

# 检查必要的工具
check_dependencies() {
    log_info "检查依赖工具..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装或不在 PATH 中"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 环境配置
setup_environment() {
    log_info "设置 $ENVIRONMENT 环境配置..."
    
    # 创建必要的目录
    mkdir -p logs/nginx logs/backend logs/nginx-lb
    mkdir -p ssl monitoring/grafana/provisioning
    
    # 根据环境设置不同的配置
    case $ENVIRONMENT in
        "dev")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.dev.yml"
            ;;
        "staging")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.staging.yml"
            ;;
        "production")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
            ;;
    esac
    
    log_success "环境配置完成"
}

# 构建前端应用
build_frontend() {
    log_info "构建前端应用..."
    
    cd Natural_English_front
    
    # 安装依赖
    if [ ! -d "node_modules" ] || [ "$BUILD_FLAG" = "--build" ]; then
        log_info "安装前端依赖..."
        npm ci
    fi
    
    # 运行测试
    log_info "运行前端测试..."
    npm run test:ci
    
    # 构建应用
    log_info "构建前端应用..."
    npm run build
    
    cd ..
    log_success "前端构建完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 10
    
    # 检查前端服务
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "前端服务健康检查通过"
    else
        log_error "前端服务健康检查失败"
        return 1
    fi
    
    # 检查后端服务（如果存在）
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_success "后端服务健康检查通过"
    else
        log_warning "后端服务健康检查失败或服务不存在"
    fi
    
    log_success "健康检查完成"
}

# 部署服务
deploy_services() {
    log_info "部署服务..."
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose down
    
    # 清理未使用的镜像（生产环境）
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "清理未使用的Docker镜像..."
        docker image prune -f
    fi
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d $BUILD_FLAG $NO_CACHE_FLAG $MONITORING_FLAG
    
    log_success "服务部署完成"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署信息:"
    echo "================================"
    echo "环境: $ENVIRONMENT"
    echo "前端地址: http://localhost"
    echo "后端地址: http://localhost:8080"
    
    if [ "$MONITORING_FLAG" != "" ]; then
        echo "Prometheus: http://localhost:9090"
        echo "Grafana: http://localhost:3001 (admin/admin)"
    fi
    
    echo "================================"
    
    # 显示运行中的容器
    log_info "运行中的服务:"
    docker-compose ps
}

# 主函数
main() {
    check_dependencies
    setup_environment
    
    if [ "$BUILD_FLAG" = "--build" ]; then
        build_frontend
    fi
    
    deploy_services
    health_check
    show_deployment_info
    
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，正在清理..."; docker-compose down; exit 1' ERR

# 执行主函数
main