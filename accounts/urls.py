# accounts/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),  # registerのビューも定義
    path('logout/', LogoutView.as_view(), name='logout'),
]
