from django.urls import path
from .views import ActionLogListView

app_name = 'logger'  # 名前空間を設定

urlpatterns = [
    path('', ActionLogListView.as_view(), name='action_log_list'),
]
