from django.contrib import admin
from django.contrib.admin import AdminSite

# vocabulary_manager应用已迁移到teaching应用统一管理
# from apps.vocabulary_manager.admin import *

# 自定义Admin站点信息
admin.site.site_header = 'Natural English 管理后台'
admin.site.site_title = 'Natural English Admin'
admin.site.index_title = '欢迎使用 Natural English 管理系统'