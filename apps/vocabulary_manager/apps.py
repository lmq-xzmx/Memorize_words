from django.apps import AppConfig


class VocabularyManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vocabulary_manager'
    verbose_name = '成长中心'
    
    def ready(self):
        """应用准备就绪时的初始化"""
        try:
            import apps.vocabulary_manager.signals
        except ImportError:
            pass
