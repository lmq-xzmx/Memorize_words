from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """获取字典中指定键的值"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_extension_data(extension_data, extension_id):
    """获取增项数据"""
    if isinstance(extension_data, dict):
        return extension_data.get(extension_id)
    return None