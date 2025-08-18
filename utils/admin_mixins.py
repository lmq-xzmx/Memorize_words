from django.contrib.admin.views.main import ChangeList
from django.contrib import admin


class DynamicPaginationChangeList(ChangeList):
    """
    自定义ChangeList类，支持通过URL参数动态设置每页显示数量
    """
    def __init__(self, request, model, list_display, list_display_links, 
                 list_filter, date_hierarchy, search_fields, list_select_related, 
                 list_per_page, list_max_show_all, list_editable, model_admin, 
                 sortable_by, search_help_text):
        
        # 从URL参数中获取每页显示数量
        page_param = request.GET.get('list_per_page', None)
        if page_param is not None:
            try:
                # 覆盖list_per_page参数，需要在super调用之前设置
                list_per_page = int(page_param)
                # 确保值在合理范围内
                if list_per_page < 1:
                    list_per_page = 10
                elif list_per_page > 1000:
                    list_per_page = 1000
            except (ValueError, TypeError):
                # 如果参数无效，使用默认值
                pass
        
        super().__init__(request, model, list_display, list_display_links, 
                        list_filter, date_hierarchy, search_fields, list_select_related, 
                        list_per_page, list_max_show_all, list_editable, model_admin, 
                        sortable_by, search_help_text)

    def get_filters_params(self, params=None):
        """
        返回所有参数，除了IGNORED_PARAMS和'list_per_page'
        这样可以确保list_per_page参数不会干扰其他过滤器
        """
        lookup_params = super().get_filters_params(params)
        if 'list_per_page' in lookup_params:
            del lookup_params['list_per_page']
        return lookup_params


class AdminDynamicPaginationMixin:
    """
    Django Admin动态分页混合类
    为Admin类添加动态分页功能，允许用户通过下拉菜单选择每页显示数量
    """
    
    # 默认的每页显示数量选项
    pagination_choices = [5, 10, 20, 25, 50, 100, 200]
    
    def get_changelist(self, request, **kwargs):
        """
        返回自定义的ChangeList类
        """
        return DynamicPaginationChangeList
    
    def changelist_view(self, request, extra_context=None):
        """
        重写changelist_view以支持动态分页
        """
        # 从URL参数中获取每页显示数量
        page_param = request.GET.get('list_per_page', None)
        if page_param is not None:
            try:
                page_size = int(page_param)
                # 确保值在合理范围内
                if 1 <= page_size <= 1000:
                    self.list_per_page = page_size
            except (ValueError, TypeError):
                # 如果参数无效，使用默认值
                pass
        
        # 添加分页选项到上下文
        if extra_context is None:
            extra_context = {}
        
        extra_context.update({
            'pagination_choices': self.pagination_choices,
            'current_per_page': getattr(self, 'list_per_page', 100)
        })
        
        return super().changelist_view(request, extra_context)