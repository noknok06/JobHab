# views.py

from django.views.generic import TemplateView, ListView
from django.views import View
from .models import Post, Company, Project, PostBilling, Approval, PostBilling, PostComment
from .forms import PostForm, PostAttachmentForm, ProjectForm, ApprovalForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Case, When, BooleanField
from django.utils.timezone import now
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.utils.http import urlencode
from .models import Event
from .utils import get_dashboard_data, get_approval_warnings
from django.utils.safestring import mark_safe
from .forms import UserRegisterForm
        
# トップページ
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在の日付と先月の年月を取得
        today = date.today()
        current_year = today.year
        current_month = today.month
        first_day_of_this_month = date(current_year, current_month, 1)
        last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
        last_month = last_day_of_last_month.month
        last_year = last_day_of_last_month.year

        # 共通クエリセット
        posts = Post.objects.all()

        # アノテート: 請求済フラグを追加
        posts = posts.annotate(
            is_billed=Case(
                When(billings__is_checked=True, then=True),
                default=False,
                output_field=BooleanField(),
            )
        )

        # 最近のポスト (作成日降順)
        context['recent_posts'] = posts.order_by('-order_date')[:5]

        # 今月の計上予定
        context['this_month_posts'] = posts.filter(
            expected_booking_date__year=current_year,
            expected_booking_date__month=current_month
        ).order_by('expected_booking_date')

        # 先月の請求予定
        context['last_month_posts'] = posts.filter(
            expected_booking_date__year=last_year,
            expected_booking_date__month=last_month
        ).order_by('expected_booking_date')

        # ステータスが新規または見積確認中のポスト
        context['new_or_reviewing_posts'] = posts.filter(
            status__in=['新規', '見積確認中']
        ).order_by('-order_date')

        # ステータスが完了かつ請求状況が未請求のポスト
        context['unbilled_completed_posts'] = posts.filter(
            status='完了',
            is_billed=False
        )
        dashboard_data = get_dashboard_data()
        
        # posts_summary をJSONにシリアライズしてマークセーフにする
        context['posts_summary_json'] = mark_safe(json.dumps(dashboard_data['posts_summary']))
        context['recent_due_dates'] = dashboard_data['recent_due_dates']

        # 稟議書の警告データを取得 (終了日が2か月以内のもの)
        context['approval_warnings'] = get_approval_warnings()

        return context
    
def get_projects(request, company_id):
    projects = Project.objects.filter(company_id=company_id).values('id', 'name')
    return JsonResponse(list(projects), safe=False)

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()

        # ステータスフィルタリング
        statuses = self.request.GET.getlist('status')
        if statuses:
            queryset = queryset.filter(status__in=statuses)

        # 請求状況フィルタリング
        is_billed = self.request.GET.get('is_billed')
        if is_billed:
            if is_billed == 'billed':
                queryset = queryset.filter(billings__is_checked=True).distinct()
            elif is_billed == 'unbilled':
                queryset = queryset.filter(~Q(billings__is_checked=True)).distinct()

        # 請求状況をアノテート
        queryset = queryset.annotate(
            is_billed=Case(
                When(billings__is_checked=True, then=True),
                default=False,
                output_field=BooleanField(),
            )
        ).distinct()  # 最後にdistinctを使って重複を排除

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 絞り込み用の選択肢をコンテキストに追加
        context['status_options'] = ['新規', '見積確認中', '発注済', '完了', '却下']
        context['is_billed_options'] = {'billed': '請求済', 'unbilled': '未請求'}
        context['selected_statuses'] = self.request.GET.getlist('status')

        # 現在の選択状態を反映
        context['selected_statuses'] = self.request.GET.getlist('status') or ['新規', '見積確認中']

        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['billing_history'] = self.object.billings.all()
        return context

def advance_status(request, pk):
    post = get_object_or_404(Post, pk=pk)
    status_order = ['新規', '見積確認中', '発注済', '完了', '却下']
    current_status_index = status_order.index(post.status) if post.status in status_order else -1

    if current_status_index < len(status_order) - 1:
        post.status = status_order[current_status_index + 1]
        post.save()

        # 新しいステータスとそのクラスを返す
        return JsonResponse({
            'success': True,
            'new_status': post.status,
            'new_status_class': 'success'  # ここはステータスに合わせてクラスを設定
        })
    return JsonResponse({'success': False})

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # attachment_formの初期化
        if self.request.method == 'POST':
            context['attachment_form'] = PostAttachmentForm(self.request.POST, self.request.FILES)
        else:
            context['attachment_form'] = PostAttachmentForm()
        return context

    def form_valid(self, form):
        # contextからattachment_formを取得
        context = self.get_context_data()
        attachment_form = context.get('attachment_form')
        
        self.object = form.save()  # Postオブジェクトを保存

        if attachment_form and attachment_form.is_valid():
            # 添付ファイルの保存処理
            for file in self.request.FILES.getlist('files'):
                if file:
                    self.object.attachments.create(file=file)

        messages.success(self.request, "ポストが作成されました！")
        return redirect('order:post_list')  # 適切なリダイレクト先を設定
    
# ポスト更新
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm  # PostFormを使用する
    template_name = 'post_form.html'
    success_url = reverse_lazy('order:post_list')
 
    def get_success_url(self):
        post_id = self.kwargs.get('pk')
        return reverse_lazy('order:post_detail', kwargs={'pk': post_id})

# ポスト削除
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('order:post_list')

class PostBillingCreateView(LoginRequiredMixin, CreateView):
    model = PostBilling
    template_name = 'post_billing_form.html'
    fields = ['remarks', 'invoice_file']  # 備考と請求書ファイルをフォームに表示
    success_url = reverse_lazy('order:post_list')

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])  # 対象のPostを取得
        form.instance.post = post  # Postを関連付け
        form.instance.is_checked = True  # 請求済みフラグをTrueに設定
        form.instance.billing_date = timezone.now().date()  # 請求日を現在日付に設定

        # 添付ファイルを保存
        if 'invoice_file' in self.request.FILES:
            form.instance.invoice_file = self.request.FILES['invoice_file']

        messages.success(self.request, "請求処理が実施されました！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(pk=self.kwargs['pk'])
        return context
    
    def get_success_url(self):
        post_id = self.kwargs.get('pk')
        return reverse_lazy('order:post_detail', kwargs={'pk': post_id})


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)

            # リクエストボディの確認
            if not request.body:
                return JsonResponse({"error": "リクエストボディが空です。"}, status=400)

            data = json.loads(request.body)  # JSONを読み取る
            comment_text = data.get("comment_text")

            if not comment_text:
                return JsonResponse({"error": "コメントが空です。"}, status=400)

            # ユーザーが認証済みかどうか確認
            user = request.user if request.user.is_authenticated else None

            # コメント作成
            comment = PostComment.objects.create(
                post=post,
                user=user,
                comment_text=comment_text,
                created_at=now(),
            )

            return JsonResponse({
                "id": comment.id,
                "user": comment.user.email if comment.user else "匿名",
                "comment_text": comment.comment_text,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        except Post.DoesNotExist:
            return JsonResponse({"error": "指定されたポストが見つかりません。"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "リクエストボディが正しいJSON形式ではありません。"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(PostComment, pk=pk)
        comment.delete()
        return JsonResponse({'message': 'コメントを削除しました。'}, status=200)
            
# 会社一覧
class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'company_list.html'
    context_object_name = 'companies'

# 会社登録
class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = 'company_form.html'
    fields = ['name', 'info', 'remarks', 'master_contract', 'status']
    success_url = reverse_lazy('order:company_list')

# 会社詳細
class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company_detail.html'
    context_object_name = 'company'

# 会社削除
class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'company_confirm_delete.html'
    success_url = reverse_lazy('order:company_list')

# 稟議書一覧
class ApprovalListView(LoginRequiredMixin, ListView):
    model = Approval
    template_name = 'approval_list.html'
    context_object_name = 'approvals'

    # def get_queryset(self):
    #     """
    #     現在月の稟議書をフィルタリングして表示
    #     """
    #     today = date.today()
    #     return Approval.objects.filter(start_date__month=today.month, start_date__year=today.year)


# 稟議書登録
class ApprovalCreateView(LoginRequiredMixin, CreateView):
    model = Approval
    form_class = ApprovalForm  # PostFormを使用する
    template_name = 'approval_form.html'
    success_url = reverse_lazy('order:approval_list')

# 稟議書詳細
class ApprovalDetailView(LoginRequiredMixin, DetailView):
    model = Approval
    template_name = 'approval_detail.html'
    context_object_name = 'approval'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 関連するプロジェクトを取得
        context['related_projects'] = self.object.approvals.all()
        return context

class ApprovalUpdateView(LoginRequiredMixin, UpdateView):
    model = Approval
    form_class = ApprovalForm
    template_name = 'approval_form.html'
    success_url = reverse_lazy('order:approval_list')

# 稟議書削除
class ApprovalDeleteView(LoginRequiredMixin, DeleteView):
    model = Approval
    template_name = 'approval_confirm_delete.html'
    success_url = reverse_lazy('order:approval_list')

# プロジェクト一覧
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'

# プロジェクト登録
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = reverse_lazy('order:project_list')

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = reverse_lazy('order:project_list')

# プロジェクト詳細
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 合計金額を計算
        total_amount = self.object.post_set.aggregate(total=Sum('amount'))['total'] or 0
        context['total_amount'] = total_amount
        return context
    
# プロジェクト削除
class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    success_url = reverse_lazy('order:project_list')


def approval_events(request):
    # 今日の日付を取得
    today = date.today()

    # draft_dateが今日以降の稟議書をフィルタリング
    approvals = Approval.objects.all()

    # events_dataに必要な情報を格納
    events_data = [
        {
            "title": approval.name,  # 稟議書名
            "start": approval.draft_date.isoformat(),  # 起案日をイベントの開始日時とする
            "end": approval.end_date.isoformat() if approval.end_date else None,  # 終了日があれば設定
            "description": approval.remarks if approval.remarks else "備考なし"  # 備考欄
        }
        for approval in approvals
    ]

    # イベントデータをJSONレスポンスとして返す
    return JsonResponse(events_data, safe=False)


# イベントデータをJSON形式で返すビュー
class EventListView(LoginRequiredMixin, ListView):
    model = Approval
    template_name = 'approval_list.html'  # 実際には使わないので適当なテンプレートを設定
    context_object_name = 'approvals'

    def get(self, request, *args, **kwargs):
        today = date.today()

        # すべての稟議書を取得
        approvals = Approval.objects.all()

        events_data = []

        # 稟議書ごとにイベントデータを作成
        for approval in approvals:
            event = {
                "title": approval.name,
                "start": approval.draft_date.isoformat(),  # 起案日
                "end": approval.end_date.isoformat() if approval.end_date else None,
                "url": f"/order/approval/{approval.pk}/",
                "description": approval.remarks if approval.remarks else "備考なし",
            }

            if approval.repeat_flag == '毎年':
                # 現在の年の日付を計算
                current_year_event = event.copy()
                current_year_event_date = approval.draft_date.replace(year=today.year)
                current_year_event["start"] = current_year_event_date.isoformat()

                if approval.end_date:
                    current_year_event_end_date = approval.end_date.replace(year=today.year)
                    current_year_event["end"] = current_year_event_end_date.isoformat()

                events_data.append(current_year_event)

                # 将来の繰り返しイベント（4年分）を追加
                for i in range(1, 5):
                    next_year_event = event.copy()
                    next_year_event_date = approval.draft_date.replace(year=today.year + i)
                    next_year_event["start"] = next_year_event_date.isoformat()

                    if approval.end_date:
                        next_year_event_end_date = approval.end_date.replace(year=today.year + i)
                        next_year_event["end"] = next_year_event_end_date.isoformat()

                    events_data.append(next_year_event)
            else:
                events_data.append(event)


        # すべての稟議書を取得
        posts = Post.objects.all()

        # Postごとにイベントデータを作成
        # for post in posts:
        #     event = {
        #         "title": post.title,
        #         "start": post.contract_start_date,  # 起案日
        #         "end": post.contract_end_date if post.contract_end_date else None,
        #         "url": f"/post/{post.pk}/",
        #         "description": post.remarks if post.remarks else "備考なし",
        #     }
        #     events_data.append(event)

        return JsonResponse(events_data, safe=False)
    

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} さん、アカウントが作成されました！')
            return redirect('login')  # 登録後、ログイン画面にリダイレクト
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})