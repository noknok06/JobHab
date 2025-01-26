import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """ファイルのフルパスからベース名を返すフィルタ"""
    return os.path.basename(value)
