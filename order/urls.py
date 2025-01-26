from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import RedirectView
from .views import (
    HomeView,
    PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, get_projects, PostBillingCreateView,
    AddCommentView, DeleteCommentView,advance_status,
    CompanyListView, CompanyCreateView, CompanyDetailView, CompanyDeleteView,
    ProjectListView, ProjectCreateView, ProjectDetailView, ProjectDeleteView, ProjectUpdateView,
    ApprovalListView, ApprovalCreateView, ApprovalDetailView, ApprovalUpdateView, ApprovalDeleteView, EventListView
)

from . import views

app_name = 'order'  # 名前空間を設定

urlpatterns = [
    # トップページ
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/login/', RedirectView.as_view(url='/login/')),  # /accounts/login/ を /login/ にリダイレクト
    
    # ポスト関連
    path('post/', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/add/', PostCreateView.as_view(), name='post_add'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('api/projects/<int:company_id>/', get_projects, name='get_projects'),
    path('post/<int:pk>/billing/add/', PostBillingCreateView.as_view(), name='create_billing_record'),
    path('posts/<int:pk>/add_comment/', AddCommentView.as_view(), name='add_comment'),
    path('comments/<int:pk>/delete/', DeleteCommentView.as_view(), name='delete_comment'),
    path('posts/<int:pk>/advance_status/', advance_status, name='advance_status'),

    # 会社一覧
    path('company/', CompanyListView.as_view(), name='company_list'),
    path('company/add/', CompanyCreateView.as_view(), name='company_add'),
    path('company/<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('company/<int:pk>/delete/', CompanyDeleteView.as_view(), name='company_delete'),
    
    # 稟議書一覧
    path('approval/', ApprovalListView.as_view(), name='approval_list'),
    path('approval/add/', ApprovalCreateView.as_view(), name='approval_add'),
    path('approval/<int:pk>/', ApprovalDetailView.as_view(), name='approval_detail'),
    path('approval/<int:pk>/edit/', ApprovalUpdateView.as_view(), name='approval_edit'),
    path('approval/<int:pk>/delete/', ApprovalDeleteView.as_view(), name='approval_delete'),

    # プロジェクト一覧
    path('project/', ProjectListView.as_view(), name='project_list'),
    path('project/add/', ProjectCreateView.as_view(), name='project_add'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),

    path('events/', EventListView.as_view(), name='event_list'),  # 追加

    path('register/', views.register, name='register'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
