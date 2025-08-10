from django.apps import AppConfig
import os


class NlpEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.nlp_engine'
    verbose_name = 'NLP Engine'
    
    def ready(self):
        """应用启动时初始化NLTK数据路径"""
        self.setup_nltk_data_path()
    
    def setup_nltk_data_path(self):
        """设置NLTK数据路径到项目内部"""
        try:
            import nltk
            from django.conf import settings
            
            # 获取项目内的NLTK数据路径
            project_nltk_data = os.path.join(
                settings.BASE_DIR, 
                'apps', 
                'nlp_engine', 
                'nltk_data'
            )
            
            # 将项目内的NLTK数据路径添加到NLTK搜索路径的最前面
            if project_nltk_data not in nltk.data.path:
                nltk.data.path.insert(0, project_nltk_data)
            
            print(f"NLTK数据路径已设置为: {project_nltk_data}")
        except ImportError:
            print("NLTK未安装，跳过数据路径设置")
        except Exception as e:
            print(f"设置NLTK数据路径时出错: {e}")