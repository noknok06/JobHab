# order/models.py

from django.conf import settings
from django.db import models
from datetime import date, datetime, timedelta
import os

# ファイルアップロード用のパス生成関数
def attachment_file_upload_path(instance, filename):
    timestamp = datetime.now().strftime('%Y/%m/%d')
    return os.path.join(f'attachments/{timestamp}', filename)


class Company(models.Model):
    STATUS_CHOICES = [
        ('管理対象', '管理対象'),
        ('管理対象外', '管理対象外'),
    ]

    name = models.CharField(max_length=255, verbose_name="会社名")
    info = models.TextField(blank=True, null=True, verbose_name="会社情報")
    remarks = models.TextField(blank=True, null=True, verbose_name="備考")
    master_contract = models.FileField(upload_to='contracts/', blank=True, null=True, verbose_name="基本契約書")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="ステータス")
    image = models.ImageField(upload_to='company_images/' ,blank=True, null=True)

    class Meta:
        verbose_name = "会社"
        verbose_name_plural = "会社一覧"
        ordering = ['name']

    def __str__(self):
        return self.name


def approval_file_upload_path(instance, filename):
    timestamp = datetime.now().strftime('%Y/%m/%d')
    return os.path.join(f'approvals/{timestamp}', filename)


class Approval(models.Model):
    REPEAT_CHOICES = [
        ('毎年', '毎年'),
        ('半年に一度', '半年に一度'),
        ('一度きり', '一度きり'),
    ]

    companies = models.ManyToManyField(Company, verbose_name="関連会社", blank=True)
    name = models.CharField(max_length=255, verbose_name="稟議書名", null=True, blank=True)
    draft_date = models.DateField(verbose_name="起案日", null=True, blank=True)
    start_date = models.DateField(verbose_name="開始日", null=True, blank=True)
    end_date = models.DateField(verbose_name="終了日", null=True, blank=True)
    repeat_flag = models.CharField(max_length=50, choices=REPEAT_CHOICES, verbose_name="繰り返しフラグ", null=True, blank=True)
    attached_file = models.FileField(upload_to=approval_file_upload_path, verbose_name="添付ファイル", null=True, blank=True)
    remarks = models.TextField(blank=True, null=True, verbose_name="備考")

    class Meta:
        verbose_name = "稟議管理"
        verbose_name_plural = "稟議管理一覧"
        ordering = ['start_date']

    def __str__(self):
        return self.name if self.name else "未定義の稟議書"


class Project(models.Model):
    STATUS_CHOICES = [
        ('管理対象', '管理対象'),
        ('管理対象外', '管理対象外'),
    ]

    companies = models.ManyToManyField(Company, related_name='projects', verbose_name="関連会社")
    name = models.CharField(max_length=255, verbose_name="プロジェクト名")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="ステータス")
    approvals = models.ManyToManyField(Approval, related_name='approvals', verbose_name="関連稟議書", blank=True)
    remarks = models.TextField(blank=True, null=True, verbose_name="備考")
    start_date = models.DateField(verbose_name="開始日", blank=True, null=True)  # 開始日
    end_date = models.DateField(verbose_name="終了日", blank=True, null=True)    # 終了日
    color = models.CharField(max_length=7, verbose_name="カレンダー色", blank=True, null=True)  # 追加されたフィールド

    class Meta:
        verbose_name = "プロジェクト"
        verbose_name_plural = "プロジェクト一覧"
        ordering = ['name']

    def __str__(self):
        return self.name

class AccountingSubject(models.Model):
    name = models.CharField(max_length=255, verbose_name="科目名")
    description = models.TextField(blank=True, null=True, verbose_name="説明")
    is_active = models.BooleanField(default=True, verbose_name="有効")

    class Meta:
        verbose_name = "計上科目"
        verbose_name_plural = "計上科目一覧"
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="タグ名")

    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ一覧"
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('新規', '新規'),
        ('見積確認中', '見積確認中'),
        ('発注済', '発注済'),
        ('完了', '完了'),
        ('却下', '却下'),
    ]

    CONTRACT_CHOICES = [
        ('一度きり', '一度きり'),
        ('毎月請求', '毎月請求'),
        ('特定期間', '特定期間'),
    ]

    parent_post = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', verbose_name="関連Post"
    )
    approval = models.ForeignKey(Approval, on_delete=models.CASCADE, verbose_name="稟議書", null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name="会社")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='新規', verbose_name="ステータス")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='post_set', verbose_name="プロジェクト")
    title = models.CharField(max_length=255, verbose_name="タイトル")
    contract_method = models.CharField(max_length=50, choices=CONTRACT_CHOICES, verbose_name="契約方法")
    remarks = models.TextField(blank=True, null=True, verbose_name="備考")
    order_date = models.DateField(verbose_name="注文日", null=True, blank=True)
    expected_booking_date = models.DateField(verbose_name="計上予定日", null=True, blank=True)
    contract_start_date = models.DateField(verbose_name="契約開始日", null=True, blank=True)
    contract_end_date = models.DateField(verbose_name="契約終了日", null=True, blank=True)
    accounting_subject = models.ForeignKey(
        AccountingSubject, on_delete=models.PROTECT, verbose_name="計上科目", null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="金額", default=0)
    estimate_file = models.FileField(upload_to='attachments/estimates/', verbose_name="見積書", null=True, blank=True)
    order_file = models.FileField(upload_to='attachments/orders/', verbose_name="注文書", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "発注・計上管理"
        verbose_name_plural = "発注・計上管理一覧"
        ordering = ['contract_start_date']

    def __str__(self):
        return self.title

    def is_billing_required(self):
        today = date.today()
        if self.contract_method == '一度きり':
            return self.status != '完了'
        elif self.contract_method in ['毎月請求', '特定期間']:
            if self.contract_start_date and self.contract_end_date:
                return self.contract_start_date <= today <= self.contract_end_date and self.status != '完了'
        return False

class PostAttachment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='attachments', verbose_name="関連Post"
    )
    file = models.FileField(upload_to='attachments/', verbose_name="添付ファイル")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="アップロード日時")

    class Meta:
        verbose_name = "Post添付ファイル"
        verbose_name_plural = "Post添付ファイル一覧"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file.name


class PostBilling(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='billings', verbose_name="関連Post"
    )
    billing_date = models.DateField(auto_now_add=True, verbose_name="請求日")
    is_checked = models.BooleanField(default=False, verbose_name="請求済みチェック")
    remarks = models.TextField(blank=True, null=True, verbose_name="備考")
    invoice_file = models.FileField(
        upload_to='invoices/', blank=True, null=True, verbose_name="請求書"
    )  # 添付ファイルフィールドを追加

    class Meta:
        verbose_name = "請求履歴"
        verbose_name_plural = "請求履歴一覧"
        ordering = ['-billing_date']

    def __str__(self):
        return f"Post ID: {self.post.id} - {self.billing_date} - {'済' if self.is_checked else '未済'}"

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="関連Post")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 修正箇所
    comment_text = models.TextField(verbose_name="コメント内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "Postコメント"
        verbose_name_plural = "Postコメント一覧"
        ordering = ['-created_at']

    def __str__(self):
        return f"Post ID: {self.post.id} - {self.comment_text[:20]}..."


class Event(models.Model):
    REPEAT_CHOICES = [
        ('毎年', '毎年'),
        ('半年に一度', '半年に一度'),
        ('一度きり', '一度きり'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="イベント名", null=True, blank=True)
    start_date = models.DateField(verbose_name="開始日", null=True, blank=True)
    end_date = models.DateField(verbose_name="終了日", null=True, blank=True)
    repeat_flag = models.CharField(max_length=50, choices=REPEAT_CHOICES, verbose_name="繰り返しフラグ", null=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="備考")

    class Meta:
        abstract = True  # 直接インスタンス化されない
    
    def get_repeat_rule(self):
        """ 繰り返しルールを取得 """
        if self.repeat_flag == '毎年':
            return rrule.rrule(rrule.YEARLY, dtstart=self.start_date, until='2030-01-01')
        elif self.repeat_flag == '半年に一度':
            return rrule.rrule(rrule.MONTHLY, dtstart=self.start_date, count=6)
        else:
            return [self.start_date]
    
    def to_event_dict(self):
        """ イベントデータを辞書として返す """
        repeat_rule = self.get_repeat_rule()
        events = []
        for dt in repeat_rule:
            events.append({
                'title': self.name,
                'start': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                'end': (dt + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),  # 1時間のイベント
                'description': self.description if self.description else '備考なし',
            })
        return events

