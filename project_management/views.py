from django.conf import settings
import json
from .forms import TaskForm
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, TemplateView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
import datetime
from .forms import JoinProjectForm, TicketForm, CommentForm, CategoryForm, TicketSearchForm
from .models import UserProject, Ticket, TicketComment, TicketFavorite, Attachment, Category, CommentImage, Task
from order.models import Project, Company
from django.db.models import Count, Q
from datetime import date, timedelta
from django.db.models.functions import TruncWeek, TruncDay
from django.db.models import Case, When, Value, CharField, Q

STATUS_UNPROCESSED = 10
STATUS_HOLD = 20
STATUS_INWORK = 30
STATUS_OUTWORK = 40
STATUS_FINISH = 50

from datetime import date, timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncWeek
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json

@login_required
def ticket_events(request):
    # ユーザーが関与するプロジェクトのチケットを取得
    user_projects = UserProject.objects.filter(user=request.user).values_list('project_id', flat=True)
    tickets = Ticket.objects.filter(project_id__in=user_projects)

    # プロジェクトに色を動的に割り当て
    projects = {project.id: project.name for project in Project.objects.filter(id__in=user_projects)}
    project_colors = generate_project_colors(projects)

    events = []
    for ticket in tickets:
        events.append({
            'title': ticket.title,
            'start': ticket.start_date.isoformat() if ticket.start_date else None,
            'end': (ticket.end_date + timedelta(days=1)).isoformat() if ticket.end_date else None,
            'url': reverse_lazy('project_management:ticket_detail', kwargs={'pk': ticket.id}),
            'status_id': ticket.status_id,  # ステータスID
            'detail': ticket.detail,  # チケット詳細
            'project_id': ticket.project.id,  # プロジェクトID
            'extendedProps': {
                'project_color': ticket.project.color  # プロジェクトの色を追加
            }
        })

    return JsonResponse(events, safe=False)

def generate_project_colors(projects):
    """プロジェクトに動的に色を割り当て"""
    colors = [
        '#FFAAAA', '#AAAAFF', '#AAFFAA', '#FFD700', '#FF6347', '#8A2BE2', 
        '#98FB98', '#D2691E', '#FF4500', '#32CD32', '#FF1493', '#8B0000'
    ]
    
    project_colors = {}
    color_idx = 0
    
    for project_id, project_name in projects.items():
        project_colors[project_id] = colors[color_idx % len(colors)]  # 色を循環させる
        color_idx += 1
        
    return project_colors
@login_required
def home(request):
    user = request.user

    # ユーザーが関与するプロジェクト
    user_projects = (
        UserProject.objects.filter(user=user)
        .select_related('project')
    )
    favorite_tickets = (
        TicketFavorite.objects.filter(user=user)
        .select_related('ticket', 'ticket__project')
    )
    # ステータスの定数利用
    ticket_status_counts = (
        Ticket.objects.filter(project__in=user_projects.values('project'))
        .values('status_id')
        .annotate(count=Count('status_id'))
    )
    # 初期化されたステータスカウント辞書
    status_counts = {
        status: 0 for status in [STATUS_UNPROCESSED, STATUS_HOLD, STATUS_INWORK, STATUS_OUTWORK, STATUS_FINISH]
    }
    for item in ticket_status_counts:
        status_counts[item['status_id']] = item['count']

    # プロジェクト ID のリストを取得
    project_ids = user_projects.values_list('project_id', flat=True)

    # 最近更新されたチケット
    recent_updates = (
        Ticket.objects.filter(project_id__in=project_ids)
        .select_related('project')
        .order_by('-updated_at')[:10]
    )

    overdue_tickets = (
        Ticket.objects.filter(
            project_id__in=project_ids,
        ).annotate(
            label=Case(
                When(start_date__lt=date.today(), then=Value('danger')),  # 過去 + 未処理
                default=Value(''),
                output_field=CharField(),
            )
        )
    )

    three_days_ago = date.today() + timedelta(days=3)

    # 週ごとのPost作成数を集計
    weekly_post_counts = (
        Ticket.objects.annotate(week=TruncWeek('created_at'))  # 作成日時を週単位に切り捨て
        .values('week')  # 週ごとにグループ化
        .annotate(count=Count('id'))  # 作成数をカウント
        .order_by('week')  # 週の昇順でソート
    )

    # グラフ用データの生成
    graph_data = {
        "weeks": [item['week'].strftime('%Y-%m-%d') for item in weekly_post_counts],
        "counts": [item['count'] for item in weekly_post_counts],
    }

    # JSONデータに変換
    graph_data_json = json.dumps(graph_data)

    context = {
        'user_projects': user_projects,
        'favorite_tickets': favorite_tickets,
        'status_counts': status_counts,
        'recent_updates': recent_updates,  # 名前を変更して明確化
        'upcoming_deadline_tickets': overdue_tickets,
        'graph_data_json': graph_data_json,  # テンプレートで利用するグラフデータ
        'three_days_ago': three_days_ago,
        'today': date.today,
    }
    return render(request, 'project_management/home.html', context)


class CategoryListView(ListView):
    model = Category
    template_name = 'project_management/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(project_id=self.kwargs['project_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['project_id'])
        return context

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'project_management/category_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_id'] = self.kwargs['project_id']
        return kwargs

    def get_success_url(self):
        return reverse_lazy('project_management:category_list', kwargs={'project_id': self.kwargs['project_id']})

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'project_management/category_form.html'

    def get_success_url(self):
        return redirect('project_management:category_list', project_id=self.kwargs['project_id'])

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'project_management/category_confirm_delete.html'
    context_object_name = 'categories'

    def get_success_url(self):
        # Correctly pass project_id to the URL
        return reverse_lazy('project_management:category_list', kwargs={'project_id': self.kwargs['project_id']})

    def get_queryset(self):
        # Ensure that the queryset is filtered by project_id
        return Category.objects.filter(project_id=self.kwargs['project_id'])

@method_decorator(login_required, name='dispatch')
class UserProjectListView(ListView):
    model = UserProject
    template_name = 'project_management/user_project_list.html'
    context_object_name = 'user_projects'

    def get_queryset(self):
        return UserProject.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        # Get all projects the user is involved with
        user_projects = UserProject.objects.filter(user=self.request.user)

        project_status_counts = {}

        # Loop through each project and calculate ticket status counts
        for user_project in user_projects:
            project = user_project.project

            active_count = Ticket.objects.filter(project=project, status_id=STATUS_UNPROCESSED).count()
            inwork_count = Ticket.objects.filter(project=project, status_id=STATUS_INWORK).count()
            outwork_count = Ticket.objects.filter(project=project, status_id=STATUS_OUTWORK).count()

            project_status_counts[project.id] = {
                'name': project.name,
                'active_count': active_count,
                'inwork_count': inwork_count,
                'outwork_count': outwork_count,
            }

        # Pass the project status counts to the context
        context['project_status_counts'] = project_status_counts

        # 新しくループしやすい形で情報を追加
        context['project_list'] = [
            {
                'project': user_project.project,
                'active_count': project_status_counts[user_project.project.id]['active_count'],
                'inwork_count': project_status_counts[user_project.project.id]['inwork_count'],
                'outwork_count': project_status_counts[user_project.project.id]['outwork_count']
            }
            for user_project in user_projects
        ]

        return context

@method_decorator(login_required, name='dispatch')
class ProjectSearchView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '')
        if search_query:
            projects = Project.objects.filter(name__icontains=search_query)
        else:
            projects = Project.objects.all()

        results = [{'id': project.id, 'name': project.name} for project in projects]
        return JsonResponse(results, safe=False)
    
class JoinProjectView(CreateView):
    model = UserProject
    fields = ['project']
    template_name = 'project_management/join_project.html'

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, id=project_id)

        # 既に参加していないか確認
        if not UserProject.objects.filter(user=request.user, project=project).exists():
            UserProject.objects.create(user=request.user, project=project)
            messages.success(request, 'You have successfully joined the project.')
        else:
            messages.warning(request, 'You are already a member of this project.')

        return redirect('project_management:user_project_list')

def search_projects(request):
    query = request.GET.get('q', '')
    if query:
        projects = Project.objects.filter(name__icontains=query)
        project_list = [{'id': project.id, 'name': project.name} for project in projects]
        return JsonResponse({'projects': project_list})
    return JsonResponse({'projects': []})

@method_decorator(login_required, name='dispatch')
class LeaveProjectView(DeleteView):
    model = UserProject
    template_name = 'project_management/user_project_confirm_delete.html'
    context_object_name = 'user_project'

    def get(self, request, project_id):
        user = request.user
        # 現在のユーザーと指定されたプロジェクトIDに基づいてUserProjectインスタンスを取得
        user_project = get_object_or_404(UserProject, user=user, project_id=project_id)
        
        # UserProjectインスタンスを削除
        user_project.delete()
        
        # `user_project_list`にリダイレクト
        return redirect('project_management:user_project_list')
    
    def get_success_url(self):
        return reverse_lazy('project_management:user_project_list')

    def get_queryset(self):
        # Ensure that the queryset is filtered by the current user and project
        return UserProject.objects.filter(user=self.request.user, project_id=self.kwargs['project_id'])
    
class ProjectCreateView(CreateView):
    model = Project
    template_name = 'project_management/create_project.html'
    fields = ['name', 'description', 'start_date', 'end_date']
    success_url = reverse_lazy('project_management:home')  # プロジェクト作成後にリダイレクトするURL

# def project_detail(request, pk):
#     project = get_object_or_404(Project, pk=pk)
#     return render(request, 'project_detail.html', {'project': project})

class ProjectListView(ListView):
    model = Project
    template_name = 'project_management/project_list.html'  # 修正
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.all()

class TicketListView(ListView):
    model = Ticket
    template_name = 'project_management/ticket_list.html'
    context_object_name = 'tickets'
    form_class = TicketSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['form'] = self.get_form()
        context['today'] = datetime.datetime.today()  # 今日の日付を追加

        # 各チケットのタスクTrue/Falseカウントを設定
        for ticket in context['tickets']:
            ticket.true_count = ticket.tasks.filter(completed=True).count()
            ticket.total_count = ticket.tasks.count()
        
        return context

    def get_form(self):
        return self.form_class(self.request.GET or None)

    def get_queryset(self):
        queryset = Ticket.objects.filter(project_id=self.kwargs['pk'])
        # Sort by project name in ascending order
        queryset = queryset.order_by('start_date')
        form = self.get_form()

        if form.is_valid():
            title = form.cleaned_data.get('title')
            status = form.cleaned_data.get('status')
            category = form.cleaned_data.get('category')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            deadline = form.cleaned_data.get('deadline')
            
            if title:
                queryset = queryset.filter(title__icontains=title)
            if status:
                queryset = queryset.filter(status_id=status)
            if category:
                queryset = queryset.filter(category__name__contains=category)
            if start_date:
                queryset = queryset.filter(start_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(end_date__lte=end_date)
            if deadline:
                queryset = queryset.filter(deadline__lte=deadline)

        return queryset

class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'project_management/create_ticket.html'

    def form_valid(self, form):
        # プロジェクトIDからProjectインスタンスを取得
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project  # Projectインスタンスを設定
        response = super().form_valid(form)
        # 添付ファイルの処理
        files = self.request.FILES.getlist('attachment_file')
        for file in files:
            Attachment.objects.create(ticket=self.object, attachment_file=file)
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # プロジェクトIDからProjectインスタンスを取得
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        kwargs['project'] = project  # Projectをフォームに渡す
        return kwargs

    def get_success_url(self):
        return reverse_lazy('project_management:ticket_list', kwargs={'pk': self.kwargs.get('project_id')})

class TicketDetailView(DetailView):
    model = Ticket
    template_name = 'project_management/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['form'] = CommentForm()  # Comment form for adding comments
        context['task_form'] = TaskForm()  # Form for adding tasks
        context['tasks'] = self.object.tasks.all()  # Fetch tasks related to the ticket
        context['is_favorite'] = TicketFavorite.objects.filter(ticket=self.object, user=user).exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        if 'comment_form' in request.POST:
            # コメントの追加
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.ticket = self.object
                comment.user = user
                comment.save()
                return redirect('project_management:ticket_detail', pk=self.object.pk)
        
        # Handle task form submission (new task)
        elif 'task_form' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                new_task = task_form.save(commit=False)
                new_task.ticket = self.object
                new_task.save()
                return redirect('project_management:ticket_detail', pk=self.object.pk)

        # Handle task completion toggle
        elif 'complete_task' in request.POST:
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id)
            # 完了状態をPOSTリクエストから取得して更新
            task.completed = request.POST.get('complete_task') == '1'
            task.save()
            return redirect('project_management:ticket_detail', pk=self.object.pk)
        
        # Handle task deletion
        elif 'delete_task' in request.POST:
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id)
            task.delete()
            return redirect('project_management:ticket_detail', pk=self.object.pk)

        # Handle favorite toggle
        elif 'is_favorite' in request.POST:
            # お気に入りの切り替え
            is_favorite = request.POST.get('is_favorite') == 'true'
            if is_favorite:
                TicketFavorite.objects.get_or_create(ticket=self.object, user=user)
            else:
                TicketFavorite.objects.filter(ticket=self.object, user=user).delete()
            
            return redirect('project_management:ticket_detail', pk=self.object.pk)
        
        return self.render_to_response(self.get_context_data())

class TicketDeleteView(DeleteView):
    model = Ticket
    success_url = reverse_lazy('project_management:ticket_list')  # 削除後にリダイレクトするURL

    def get_success_url(self):
        return reverse_lazy('project_management:ticket_list', kwargs={'pk': self.object.project.id})  # プロジェクトのチケットリストにリダイレクト

class TicketUpdateView(UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'project_management/edit_ticket.html'

    def get_object(self, queryset=None):
        ticket = super().get_object(queryset)
        self.project = ticket.project
        return ticket


    def form_valid(self, form):
        response = super().form_valid(form)
        
        # 添付ファイルの処理
        attachment_files = self.request.FILES.getlist('attachment_files')
        for file in attachment_files:
            Attachment.objects.create(ticket=self.object, attachment_file=file)
        
        return response

    def get_success_url(self):
        return reverse_lazy('project_management:ticket_list', kwargs={'pk': self.project.pk})

class AttachmentDeleteView(DeleteView):
    model = Attachment
    success_url = reverse_lazy('project_management:ticket_detail')  # リダイレクト先の設定

    def get_success_url(self):
        # チケットのIDを取得して、詳細ページにリダイレクト
        ticket_id = self.kwargs.get('ticket_id')
        return reverse_lazy('project_management:ticket_detail', kwargs={'pk': ticket_id})

    def get_object(self, queryset=None):
        # ファイルの削除前にチケットとファイルの存在を確認
        attachment = super().get_object(queryset)
        ticket_id = self.kwargs.get('ticket_id')
        get_object_or_404(Ticket, id=ticket_id, attachments=attachment)
        return attachment
    
class ProjectChartView(DetailView):
    model = Project
    template_name = 'project_management/project_chart.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # プロジェクトに関連するチケットを取得し、日付が設定されていないレコードを除外
        tickets = Ticket.objects.filter(
            project=project,
            start_date__isnull=False,
            end_date__isnull=False
        ).order_by('start_date')

        # チケットをIDごとに辞書に格納
        ticket_dict = {ticket.pk: ticket for ticket in tickets}
        
        # 親子関係のツリーを構築
        tree = {}
        for ticket in tickets:
            parent_id = ticket.parent_id
            if parent_id not in tree:
                tree[parent_id] = []
            tree[parent_id].append(ticket)

        # 深さ優先探索でソートされたリストを作成
        def build_sorted_list(parent_id=None):
            sorted_list = []
            if parent_id in tree:
                for ticket in tree[parent_id]:
                    sorted_list.append(ticket)
                    sorted_list.extend(build_sorted_list(ticket.pk))
            return sorted_list

        sorted_tickets = build_sorted_list()

        # ガントチャート用のデータを JSON 形式に変換
        chart_data = []
        for ticket in sorted_tickets:
            try:
                start_date = ticket.start_date.isoformat()
                end_date = ticket.end_date.isoformat()
                category = ticket.category.name if ticket.category is not None else ""
                parent = ticket.parent.title if ticket.parent is not None else ""
                
                # companies のリストを取得して名前をリスト化
                companies = [company.name for company in ticket.companies.all()] if ticket.companies.exists() else []

                # 空文字や無効な日付を除外
                if start_date and end_date:
                    chart_data.append({
                        'title': ticket.title,
                        'start': start_date,
                        'end': end_date,
                        'status_id': ticket.status_id,
                        'category_name': category,
                        'parent': parent,
                        'companies':companies,
                        'ticket_id': ticket.pk
                    })
            except ValueError:
                continue
        
        context['chart_data'] = json.dumps(chart_data)  # JSON 形式でデータを渡す
        return context
class ProjectAllChartView(TemplateView):
    template_name = 'project_management/project_all_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在のユーザーが参加しているプロジェクトを取得
        user_projects = UserProject.objects.filter(user=self.request.user).values_list('project_id', flat=True)

        # ユーザーが参加しているプロジェクトに関連するチケットを取得
        tickets = Ticket.objects.filter(
            project_id__in=user_projects,
            start_date__isnull=False,
            end_date__isnull=False
        ).order_by('start_date')

        # チケットをIDごとに辞書に格納
        ticket_dict = {ticket.pk: ticket for ticket in tickets}
        
        # 親子関係のツリーを構築
        tree = {}
        for ticket in tickets:
            parent_id = ticket.parent_id
            if parent_id not in tree:
                tree[parent_id] = []
            tree[parent_id].append(ticket)

        # 深さ優先探索でソートされたリストを作成
        def build_sorted_list(parent_id=None):
            sorted_list = []
            if parent_id in tree:
                for ticket in tree[parent_id]:
                    sorted_list.append(ticket)
                    sorted_list.extend(build_sorted_list(ticket.pk))
            return sorted_list

        sorted_tickets = build_sorted_list()

        # ガントチャート用のデータを JSON 形式に変換
        chart_data = []
        for ticket in sorted_tickets:
            try:
                start_date = ticket.start_date.isoformat()
                end_date = ticket.end_date.isoformat()
                category = ticket.category.name if ticket.category is not None else ""
                
                parent = ticket.parent.title if ticket.parent is not None else ""
                
                # companies のリストを取得して名前をリスト化
                companies = [company.name for company in ticket.companies.all()] if ticket.companies.exists() else []

                # 空文字や無効な日付を除外
                if start_date and end_date:
                    chart_data.append({
                        'title': ticket.title,
                        'start': start_date,
                        'end': end_date,
                        'status_id': ticket.status_id,
                        'ticket_id': ticket.pk,
                        'project_id': ticket.project_id,
                        'parent': parent,
                        'project_name': ticket.project.name,
                        'companies':companies,
                        'category_name': category
                    })
            except ValueError:
                continue
        
        context['chart_data'] = json.dumps(chart_data)  # JSON 形式でデータを渡す
        return context

        
@require_POST
def update_task(request):
    data = json.loads(request.body)
    ticket_id = data.get('id')
    start_date = data.get('start_date')
    # 文字列をdatetimeオブジェクトに変換
    date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    # 1日進める
    new_date_obj = date_obj + datetime.timedelta(days=1)
    # 再び文字列に戻す
    start_date = new_date_obj.strftime("%Y-%m-%d")
    end_date = data.get('end_date')
    
    # チケットの更新
    try:
        ticket = Ticket.objects.get(title=ticket_id)
        ticket.start_date = start_date
        ticket.end_date = end_date
        ticket.save()
        return JsonResponse({'status': 'success'})
    except Ticket.DoesNotExist:
        messages.error('Failed to change date.')
        return JsonResponse({'status': 'error', 'message': 'Ticket not found'})

def create_ticket(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.project = project
            ticket.save()
            form.save_m2m()  # ManyToManyField の保存
            return redirect('project_management:ticket_list', project_id=project.id)
    else:
        form = TicketForm()

    return render(request, 'project_management:ticket_form.html', {'form': form, 'project': project})


class TicketsView(ListView):
    model = Ticket
    template_name = 'project_management/tickets.html'
    context_object_name = 'tickets'
    form_class = TicketSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['companies'] = Company.objects.all()
        context['today'] = datetime.date.today()  # 今日の日付を追加
        return context

    def get_form(self):
        return self.form_class(self.request.GET or None)

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        user_projects = UserProject.objects.filter(user=self.request.user)
        project_ids = user_projects.values_list('project_id', flat=True)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            # cleaned_data = cleaned_data.filter(project_id__in=project_ids)
            if cleaned_data.get('title'):
                queryset = queryset.filter(title__icontains=cleaned_data['title'])
            
            # Handle status as a list
            status = self.request.GET.getlist('status')
            if status:
                queryset = queryset.filter(status_id__in=status)
            
            if cleaned_data.get('category'):
                queryset = queryset.filter(category__name__icontains=cleaned_data['category'])
            
            if cleaned_data.get('start_date'):
                queryset = queryset.filter(start_date__gte=cleaned_data['start_date'])
            
            if cleaned_data.get('end_date'):
                queryset = queryset.filter(end_date__lte=cleaned_data['end_date'])
            
            if cleaned_data.get('deadline'):
                queryset = queryset.filter(deadline__lte=cleaned_data['deadline'])
                
            # Handle company_ids as a list
            company_ids = self.request.GET.getlist('company_ids')
            if company_ids:
                queryset = queryset.filter(companies__id__in=company_ids).distinct()

        # Sort by project name in ascending order
        queryset = queryset.order_by('project__name','start_date')

        return queryset


def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # 保存処理（CommentImageは画像保存用のモデル）
        image_instance = CommentImage.objects.create(image=image)
        return JsonResponse({'success': True, 'url': image_instance.image.url})
    return JsonResponse({'success': False})    


def toggle_task_completion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            completed = data.get('completed')

            # タスクを取得
            task = Task.objects.get(id=task_id)
            task.completed = completed
            task.save()

            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
