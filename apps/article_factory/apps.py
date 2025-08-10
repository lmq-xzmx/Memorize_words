from django.apps import AppConfig


class ArticleFactoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.article_factory'
    verbose_name = '文章解析工厂'