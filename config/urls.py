from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hab import views as hab_views

urlpatterns = [
    path('', include('accounts.urls')),
    path('hab/', hab_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('project_management/', include('project_management.urls')),  # project_managementのURL
    path('order/', include('order.urls')),  # orderのURL
    path('pdf_merger/', include('pdf_merger.urls')),  # orderのURL
    path('logger/', include('logger.urls')),
    path('company/', include('company.urls')),
    path('note/', include('note.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 開発環境でMEDIAファイルを配信する設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
