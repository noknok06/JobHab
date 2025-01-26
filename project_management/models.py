from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from order.models import Project, Company

# CustomUserの代わりに、settingsで設定されたユーザーモデルを参照
User = settings.AUTH_USER_MODEL

STATUS_UNPROCESSED = 10
STATUS_HOLD = 20
STATUS_INWORK = 30
STATUS_OUTWORK = 40
STATUS_FINISH = 50

class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('ユーザー'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('プロジェクト'))

    class Meta:
        unique_together = ('user', 'project')
        verbose_name = _('ユーザープロジェクト')
        verbose_name_plural = _('ユーザープロジェクト')
        
    def __str__(self):
        return f"{self.user} - {self.project}"

class Ticket(models.Model):
    STATUS_CHOICES = [
        (STATUS_UNPROCESSED, _('未処理')),
        (STATUS_HOLD, _('保留')),
        (STATUS_INWORK, _('社内確認中')),
        (STATUS_OUTWORK, _('ベンダー作業中')),
        (STATUS_FINISH, _('完了')),
    ]
    title = models.CharField(max_length=255, verbose_name=_('タイトル'))
    detail = models.TextField(blank=True, null=True, verbose_name=_('詳細'))
    status_id = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_UNPROCESSED, verbose_name=_('ステータス'))
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('担当者'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('カテゴリ'))
    start_date = models.DateField(blank=True, null=True, verbose_name=_('開始日'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('終了日'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('プロジェクト'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新日'))
    deadline = models.DateField(blank=True, null=True, verbose_name=_('締切日'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='sub_tickets', verbose_name=_('親チケット'))
    companies = models.ManyToManyField(Company, blank=True, verbose_name=_('関連会社'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('登録日')) 

    class Meta:
        verbose_name = _('チケット')
        verbose_name_plural = _('チケット')

    def __str__(self):
        return self.title

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name=_('チケット'))
    comment = models.TextField(verbose_name=_('コメント'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('ユーザー'))
    attachment_file = models.FileField(upload_to='comment_attachments/', blank=True, null=True, verbose_name=_('添付ファイル'))
    create_date = models.DateTimeField(auto_now_add=True, verbose_name=_('作成日'))

    class Meta:
        verbose_name = _('チケットコメント')
        verbose_name_plural = _('チケットコメント')

class TicketFavorite(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name=_('チケット'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('ユーザー'))

    class Meta:
        verbose_name = _('お気に入りチケット')
        verbose_name_plural = _('お気に入りチケット')

class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='attachments', on_delete=models.CASCADE, verbose_name=_('チケット'))
    attachment_file = models.FileField(upload_to='attachments/', verbose_name=_('添付ファイル'))

    class Meta:
        verbose_name = _('添付ファイル')
        verbose_name_plural = _('添付ファイル')

    def __str__(self):
        return self.attachment_file.name

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('名前'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('プロジェクト'))

    class Meta:
        verbose_name = _('カテゴリ')
        verbose_name_plural = _('カテゴリ')

    def __str__(self):
        return self.name

class CommentImage(models.Model):
    image = models.ImageField(upload_to='comment_images/', verbose_name=_('画像'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('アップロード日'))

    class Meta:
        verbose_name = _('コメント画像')
        verbose_name_plural = _('コメント画像')

class Task(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='tasks', verbose_name=_('チケット'))
    task = models.CharField(max_length=255, verbose_name=_('タスク'))
    completed = models.BooleanField(default=False, verbose_name=_('完了'))

    class Meta:
        verbose_name = _('タスク')
        verbose_name_plural = _('タスク')

    def __str__(self):
        return self.task
