#!/bin/bash
# CSS 架构迁移脚本
# 用于将传统 CSS 迁移到 SCSS + BEM 架构

set -e

echo "🚀 开始 CSS 架构迁移..."

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <文件路径> 或 $0 --all"
    echo "示例: $0 components/Layout.vue"
    echo "示例: $0 --all (迁移所有组件)"
    exit 1
fi

# 迁移单个文件
migrate_file() {
    local file="$1"
    echo "📝 迁移文件: $file"
    
    # 备份原文件
    cp "$file" "${file}.backup"
    
    # 更新 style 标签
    sed -i '' 's/<style scoped>/<style lang="scss" scoped>/g' "$file"
    sed -i '' 's/<style>/<style lang="scss">/g' "$file"
    
    # 替换颜色值
    sed -i '' 's/#3b82f6/$color-primary-500/g' "$file"
    sed -i '' 's/#1d4ed8/$color-primary-600/g' "$file"
    sed -i '' 's/#2563eb/$color-primary-500/g' "$file"
    sed -i '' 's/#6b7280/$color-gray-600/g' "$file"
    sed -i '' 's/#9ca3af/$color-gray-400/g' "$file"
    sed -i '' 's/#d1d5db/$color-gray-300/g' "$file"
    sed -i '' 's/#e5e7eb/$color-gray-200/g' "$file"
    sed -i '' 's/#f3f4f6/$color-gray-100/g' "$file"
    sed -i '' 's/#ffffff/$color-white/g' "$file"
    sed -i '' 's/#000000/$color-black/g' "$file"
    sed -i '' 's/#ef4444/$color-red-500/g' "$file"
    sed -i '' 's/#10b981/$color-green-500/g' "$file"
    sed -i '' 's/#f59e0b/$color-yellow-500/g' "$file"
    
    # 替换间距值
    sed -i '' 's/: 4px/: $spacing-1/g' "$file"
    sed -i '' 's/: 8px/: $spacing-2/g' "$file"
    sed -i '' 's/: 12px/: $spacing-3/g' "$file"
    sed -i '' 's/: 16px/: $spacing-4/g' "$file"
    sed -i '' 's/: 20px/: $spacing-5/g' "$file"
    sed -i '' 's/: 24px/: $spacing-6/g' "$file"
    sed -i '' 's/: 32px/: $spacing-8/g' "$file"
    sed -i '' 's/: 40px/: $spacing-10/g' "$file"
    sed -i '' 's/: 48px/: $spacing-12/g' "$file"
    
    # 替换圆角值
    sed -i '' 's/border-radius: 2px/border-radius: $border-radius-sm/g' "$file"
    sed -i '' 's/border-radius: 4px/border-radius: $border-radius-md/g' "$file"
    sed -i '' 's/border-radius: 6px/border-radius: $border-radius-lg/g' "$file"
    sed -i '' 's/border-radius: 8px/border-radius: $border-radius-xl/g' "$file"
    sed -i '' 's/border-radius: 12px/border-radius: $border-radius-2xl/g' "$file"
    sed -i '' 's/border-radius: 9999px/border-radius: $border-radius-full/g' "$file"
    
    # 替换字体大小
    sed -i '' 's/font-size: 12px/font-size: $font-size-xs/g' "$file"
    sed -i '' 's/font-size: 14px/font-size: $font-size-sm/g' "$file"
    sed -i '' 's/font-size: 16px/font-size: $font-size-base/g' "$file"
    sed -i '' 's/font-size: 18px/font-size: $font-size-lg/g' "$file"
    sed -i '' 's/font-size: 20px/font-size: $font-size-xl/g' "$file"
    sed -i '' 's/font-size: 24px/font-size: $font-size-2xl/g' "$file"
    
    # 替换字体粗细
    sed -i '' 's/font-weight: 300/font-weight: $font-weight-light/g' "$file"
    sed -i '' 's/font-weight: 400/font-weight: $font-weight-normal/g' "$file"
    sed -i '' 's/font-weight: 500/font-weight: $font-weight-medium/g' "$file"
    sed -i '' 's/font-weight: 600/font-weight: $font-weight-semibold/g' "$file"
    sed -i '' 's/font-weight: 700/font-weight: $font-weight-bold/g' "$file"
    
    # 替换媒体查询为响应式 mixins
    sed -i '' 's/@media (min-width: 768px)/@include respond-to("md")/g' "$file"
    sed -i '' 's/@media (min-width: 1024px)/@include respond-to("lg")/g' "$file"
    sed -i '' 's/@media (min-width: 1280px)/@include respond-to("xl")/g' "$file"
    
    echo "✅ 完成迁移: $file"
}



# 主逻辑
if [ "$1" = "--all" ]; then
    echo "🔍 查找所有需要迁移的 Vue 组件..."
    
    # 查找所有包含 <style> 标签的 Vue 文件
    files=$(grep -r "<style" components --include="*.vue" -l 2>/dev/null || true)
    
    if [ -z "$files" ]; then
        echo "❌ 未找到需要迁移的组件"
        exit 1
    fi
    
    echo "📋 找到以下组件需要迁移:"
    echo "$files" | while read -r file; do
        echo "  - $file"
    done
    
    echo ""
    read -p "是否继续迁移所有组件? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "❌ 迁移已取消"
        exit 1
    fi
    
    # 迁移所有文件
    echo "$files" | while read -r file; do
        if [ -f "$file" ]; then
            migrate_file "$file"
        fi
    done
else
    # 迁移单个文件
    file="$1"
    if [ ! -f "$file" ]; then
        echo "❌ 文件不存在: $file"
        exit 1
    fi
    
    migrate_file "$file"
fi

echo ""
echo "🎉 迁移完成!"
echo "📝 备份文件已创建 (*.backup)"
echo "🔧 请手动检查并调整以下内容:"
echo "  1. 应用 BEM 命名规范"
echo "  2. 使用 @include bem-element() 和 @include bem-modifier()"
echo "  3. 替换复杂样式为 mixins"
echo "  4. 测试组件功能"
echo ""
echo "📚 参考文档:"
echo "  - CSS_ARCHITECTURE_GUIDE.md"
echo "  - MIGRATION_GUIDE.md"