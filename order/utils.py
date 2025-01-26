# order/utils.py

from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Post, Approval
from django.db.models import Q

def get_dashboard_data():
    # Postステータス別の件数と合計金額を集計
    posts_summary_qs = Post.objects.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).filter(status__in=["新規","見積確認中","発注済"])
    
    # posts_summary を辞書形式に変換
    posts_summary = {item['status']: item['count'] for item in posts_summary_qs}
    
    # 近日中の契約終了日を取得（例: 今日から30日以内）
    recent_due_dates = Post.objects.filter(
        contract_end_date__gte=timezone.now().date(),
        contract_end_date__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('contract_end_date')[:5]  # 上位5件を取得
    
    # 稟議書の警告データを取得
    approval_warnings = get_approval_warnings()

    return {
        "posts_summary": posts_summary,
        "recent_due_dates": recent_due_dates,
        "approval_warnings": approval_warnings,
    }

def get_approval_warnings():
    """
    終了日が2か月以内の稟議書を取得
    """
    today = timezone.now().date()
    
    # 2か月以内に終了する稟議書をフィルター
    warnings = Approval.objects.filter(
        # 毎年の条件
        Q(repeat_flag='毎年') & Q(
            end_date__isnull=False,  # 終了日が設定されている
            end_date__lte=today + timedelta(days=45),  # 終了日が45日以内
            end_date__gte=today  # 終了日が今日以降
        ) |
        # 半年に一度の条件
        Q(repeat_flag='半年に一度') & Q(
            draft_date__isnull=False,  # 起案日が設定されている
            draft_date__lte=today + timedelta(days=180 - 45),  # 起案日から半年後の45日前まで
            draft_date__gte=today - timedelta(days=60),  # 半年以内の範囲
            end_date__gte=today  # 終了日が今日以降
        )
    ).order_by('draft_date')  # 終了日順にソート

    # 重複を排除するためのセット
    seen_ids = set()
    unique_warnings = []

    for warning in warnings:
        # 各warningがuniqueな場合のみリストに追加
        if warning.id not in seen_ids:
            unique_warnings.append(warning)
            seen_ids.add(warning.id)

    # 必要な情報を辞書形式に変換
    warning_list = [
        {
            'id': warning.id,
            'name': warning.name,
            'draft_date': warning.draft_date,
            'start_date': warning.start_date,
            'end_date': warning.end_date,
            'companies': ', '.join([company.name for company in warning.companies.all()])
        }
        for warning in unique_warnings
    ]
    
    return warning_list