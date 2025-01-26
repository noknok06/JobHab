# project_management/urls.py

from django.urls import path
from . import views
from .views import ProjectCreateView, JoinProjectView, TicketListView, TicketCreateView, TicketDetailView, ProjectListView, TicketUpdateView, AttachmentDeleteView, ProjectSearchView
from .views import CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView, ProjectChartView, ProjectAllChartView, UserProjectListView, LeaveProjectView, TicketsView, TicketDeleteView
from .views import upload_image

app_name = 'project_management'  # 名前空間を設定

urlpatterns = [
    path('', views.home, name='home'),  # ホームページのURL (例として)

    # project
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:project_id>/create_ticket/', TicketCreateView.as_view(), name='ticket_create'), 
    path('projects/<int:project_id>/categories/', CategoryListView.as_view(), name='category_list'),
    path('projects/<int:project_id>/categories/add/', CategoryCreateView.as_view(), name='category_create'),
    path('projects/<int:project_id>/categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('projects/<int:project_id>/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('projects/<int:pk>/chart/', ProjectChartView.as_view(), name='project_chart'),

    path('project_all_chart/', ProjectAllChartView.as_view(), name='project_all_chart'),
    path('tickets/events/', views.ticket_events, name='ticket_events'),

    # user_project_list
    path('user_project_list/', UserProjectListView.as_view(), name='user_project_list'),
    path('user_project_list_tk/<int:pk>/', TicketListView.as_view(), name='ticket_list'),
    path('join_user_project/', JoinProjectView.as_view(), name='join_project'), 
    path('leave_user_project/<int:project_id>/', LeaveProjectView.as_view(), name='leave_project'),

    # ticket
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),  # チケット詳細ページのURL
    path('ticket/<int:pk>/edit/', TicketUpdateView.as_view(), name='edit_ticket'),
    path('tickets/<int:pk>/delete/', TicketDeleteView.as_view(), name='delete_ticket'),
    path('tickets/', TicketsView.as_view(), name='tickets'),

    path('update-task/', views.update_task, name='update_task'),
    path('attachment/<int:pk>/delete/<int:ticket_id>/', AttachmentDeleteView.as_view(), name='delete_attachment'),
    path('upload_image/', upload_image, name='upload_image'),
    path('search_projects/', views.search_projects, name='search_projects'),
    path('toggle-task-completion/', views.toggle_task_completion, name='toggle_task_completion'),
]