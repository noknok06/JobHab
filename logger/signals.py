from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import ActionLog
from logger.middleware import get_current_user  # ミドルウェアで現在のユーザーを取得

# 監視対象のアプリをリストで管理
WATCHED_APPS = ['order', 'project_management']

@receiver(post_save)
def log_create_or_update(sender, instance, created, **kwargs):
    if sender._meta.app_label not in WATCHED_APPS:  # 監視対象アプリ以外は無視
        return
    
    action = 'CREATE' if created else 'UPDATE'
    ActionLog.objects.create(
        user=get_current_user(),
        model_name=ContentType.objects.get_for_model(sender).model,
        action=action,
        details=str(instance)
    )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender._meta.app_label not in WATCHED_APPS:  # 監視対象アプリ以外は無視
        return
    
    ActionLog.objects.create(
        user=get_current_user(),
        model_name=ContentType.objects.get_for_model(sender).model,
        action='DELETE',
        details=str(instance)
    )
