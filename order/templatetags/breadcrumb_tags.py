from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag
def get_breadcrumbs(request):
    """
    URLパスを分割してパンクズリストを生成します。
    """
    path = request.path.strip('/').split('/')
    breadcrumbs = []
    for i in range(len(path)):
        url = '/' + '/'.join(path[:i+1]) + '/'
        breadcrumbs.append({'name': path[i].capitalize(), 'url': url})
    return breadcrumbs
