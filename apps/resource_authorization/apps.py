from django.apps import AppConfig


class ResourceAuthorizationConfig(AppConfig):
    """资源授权系统应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.resource_authorization'
    verbose_name = '资源授权系统'
    
    def ready(self):
        """应用准备就绪时的初始化操作"""
        # 导入信号处理器
        try:
            from . import signals
        except ImportError:
            pass
