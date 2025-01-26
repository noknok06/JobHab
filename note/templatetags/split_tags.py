# note/templatetags/split_tags.py
from django import template

register = template.Library()

@register.filter
def split_tags(value):
    """カンマ区切りでタグを分割するフィルタ"""
    return value.split(',') if value else []
