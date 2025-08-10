from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.permissions'
    verbose_name = '权限管理'
    
    def ready(self):
        """应用准备就绪时执行"""
        # 导入信号处理器
        try:
            import apps.permissions.signals  # noqa
        except ImportError:
            pass