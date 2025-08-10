from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """获取字典中指定键的值"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None