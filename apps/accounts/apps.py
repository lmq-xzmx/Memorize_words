from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = '账号管理'
    
    def ready(self):
        """应用准备就绪时执行"""
        # 导入信号处理器
        try:
            import apps.accounts.signals  # noqa
        except ImportError:
            pass