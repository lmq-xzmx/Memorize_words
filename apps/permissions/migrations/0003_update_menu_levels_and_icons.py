# Generated manually

from django.db import migrations

def update_menu_levels_and_icons(apps, schema_editor):
    """更新菜单级别和图标"""
    MenuModuleConfig = apps.get_model('permissions', 'MenuModuleConfig')
    
    # 定义菜单级别和图标映射
    menu_updates = [
        # 根目录级别 - 底部导航栏主要功能
        {'key': 'word', 'menu_level': 'root', 'icon': '⚔️', 'name': '斩词'},
        {'key': 'tools', 'menu_level': 'root', 'icon': '🛠️', 'name': '工具'},
        {'key': 'fashion', 'menu_level': 'root', 'icon': '🌟', 'name': '时尚'},
        {'key': 'dashboard', 'menu_level': 'root', 'icon': '🏠', 'name': '首页'},
        
        # 一级目录 - 工具菜单下的主要分类
        {'key': 'dev-center', 'menu_level': 'level1', 'icon': '🛠️', 'name': '开发中心'},
        {'key': 'community', 'menu_level': 'level1', 'icon': '👥', 'name': '社区互动'},
        {'key': 'fashion-trends', 'menu_level': 'level1', 'icon': '🌟', 'name': '时尚趋势'},
        
        # 二级目录 - 开发中心下的具体工具
        {'key': 'word-reading', 'menu_level': 'level2', 'icon': '📖', 'name': '单词阅读'},
        {'key': 'word-learning', 'menu_level': 'level2', 'icon': '📚', 'name': '单词学习'},
        {'key': 'word-spelling', 'menu_level': 'level2', 'icon': '✍️', 'name': '拼写练习'},
        {'key': 'word-flashcard', 'menu_level': 'level2', 'icon': '🃏', 'name': '闪卡学习'},
        {'key': 'word-detail', 'menu_level': 'level2', 'icon': '📝', 'name': '单词详情'},
        {'key': 'word-root-analysis', 'menu_level': 'level2', 'icon': '🌱', 'name': '词根分解'},
        {'key': 'pattern-memory', 'menu_level': 'level2', 'icon': '🧠', 'name': '模式匹配记忆'},
        {'key': 'story-reading', 'menu_level': 'level2', 'icon': '📚', 'name': '故事阅读'},
        {'key': 'word-challenge', 'menu_level': 'level2', 'icon': '⚔️', 'name': '单词挑战'},
        {'key': 'word-review', 'menu_level': 'level2', 'icon': '🔄', 'name': '单词复习'},
        {'key': 'word-selection', 'menu_level': 'level2', 'icon': '✅', 'name': '单词选择'},
    ]
    
    # 更新现有菜单或创建新菜单
    for menu_data in menu_updates:
        menu, created = MenuModuleConfig.objects.get_or_create(
            key=menu_data['key'],
            defaults={
                'name': menu_data['name'],
                'menu_level': menu_data['menu_level'],
                'icon': menu_data['icon'],
                'url': f"/{menu_data['key'].replace('-', '/')}",
                'sort_order': 0,
                'is_active': True,
                'description': f"{menu_data['name']}功能模块"
            }
        )
        
        if not created:
            # 更新现有菜单的级别和图标
            menu.menu_level = menu_data['menu_level']
            menu.icon = menu_data['icon']
            menu.name = menu_data['name']
            menu.save()

def reverse_update_menu_levels_and_icons(apps, schema_editor):
    """回滚操作"""
    MenuModuleConfig = apps.get_model('permissions', 'MenuModuleConfig')
    # 将所有菜单级别重置为默认值
    MenuModuleConfig.objects.all().update(menu_level='root')

class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_menumoduleconfig_menu_level'),
    ]

    operations = [
        migrations.RunPython(
            update_menu_levels_and_icons,
            reverse_update_menu_levels_and_icons
        ),
    ]