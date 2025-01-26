from django.db import models
from django.utils.translation import gettext_lazy as _
from order.models import Project, Company  # 発注情報、プロジェクト、会社情報
from project_management.models import Ticket  # タスク情報

class Inquiry(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='inquiries',
        verbose_name=_('会社')
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_('プロジェクト'),
        related_name='inquiries', null=True, blank=True
    )
    category = models.CharField(
        max_length=255,
        verbose_name=_('問い合わせ分類')
    )
    question = models.TextField(
        verbose_name=_('質問内容')
    )
    question_date = models.DateField(
        verbose_name=_('質問日')
    )
    answer_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('回答日')
    )
    answer = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('回答内容')
    )

    def __str__(self):
        return f"Inquiry for {self.company.name} ({self.category})"



class Todo(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='todos',
        verbose_name=_('会社')
    )
    task = models.CharField(max_length=255, verbose_name=_('作業内容'))  # 作業内容
    is_completed = models.BooleanField(default=False, verbose_name=_('対応済'))  # チェックボックス

    def __str__(self):
        return self.task