from django.apps import AppConfig


class WordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.words'
    verbose_name = '单词工厂'
    
    def ready(self):
        """应用启动时的初始化操作"""
        try:
            import apps.words.signals
        except ImportError:
            pass