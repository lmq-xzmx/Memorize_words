from django.apps import AppConfig


class TeachingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.teaching'
    verbose_name = '教学管理'
    
    def ready(self):
        """应用准备就绪时执行"""
        # 导入信号处理器
        try:
            import apps.teaching.signals  # noqa
        except ImportError:
            pass