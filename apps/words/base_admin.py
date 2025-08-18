from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
import csv
import io
from django.urls import path

class BaseBatchImportAdmin(admin.ModelAdmin):
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('batch_import/', self.admin_site.admin_view(self.process_batch_import), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_batch_import'),
        ]
        return my_urls + urls

    def get_batch_import_template(self):
        """
        返回批量导入功能使用的模板。
        子类可以重写此方法以提供自定义模板。
        """
        return 'admin/words/batch_import.html'

    def get_batch_import_context(self, request):
        """
        为批量导入页面的GET请求提供额外的上下文。
        子类可以重写此方法以添加自定义上下文。
        """
        return {'opts': self.model._meta}
    
    def changelist_view(self, request, extra_context=None):
        """重写changelist视图以添加批量导入按钮"""
        extra_context = extra_context or {}
        
        # 生成批量导入URL
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        batch_import_url = reverse(f'admin:{app_label}_{model_name}_batch_import')
        extra_context['batch_import_url'] = batch_import_url
        
        return super().changelist_view(request, extra_context=extra_context)

    def process_batch_import(self, request):
        """
        处理批量导入的核心逻辑。
        - 处理GET请求，渲染上传页面。
        - 处理POST请求，验证文件并调用 perform_import。
        """
        if request.method == 'POST' and 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, '文件格式错误，请上传CSV格式的文件。')
                return redirect('.')

            try:
                decoded_file = csv_file.read().decode('utf-8-sig')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                # 调用 perform_import，它可能返回一个自定义的HTTP响应
                response = self.perform_import(request, reader)
                if response:
                    return response

            except Exception as e:
                messages.error(request, f'处理文件时出错: {e}')

            # 如果 perform_import 没有返回响应，则重定向到上一页
            return redirect('..')

        # 处理GET请求
        template_name = self.get_batch_import_template()
        context = self.get_batch_import_context(request)
        return render(request, template_name, context)

    def perform_import(self, request, reader):
        """
        执行导入的核心操作。
        子类必须重写此方法以实现具体的导入逻辑。
        """
        raise NotImplementedError("子类必须实现 perform_import 方法。")