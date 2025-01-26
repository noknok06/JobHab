from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    apps = [
        {'name': 'Order Management', 'url': '/order/', 'icon': 'fas fa-shopping-cart'},
        {'name': 'Project Management', 'url': '/project_management/', 'icon': 'fas fa-tasks'},
        {'name': 'PDF Merger', 'url': '/pdf_merger/', 'icon': 'fas fa-file-pdf'},
        {'name': 'Login Manager', 'url': '/login_manager/', 'icon': 'fas fa-user-cog'},
        {'name': 'Logger', 'url': '/logger/', 'icon': 'fas fa-clipboard-list'},
    ]
    return render(request, 'hab/home.html', {'apps': apps})
