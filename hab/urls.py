# hab/urls.py
from django.urls import path, include
from hab import views

app_name = 'hab'  # 名前空間を設定

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/login/', RedirectView.as_view(url='/login/')),  # /accounts/login/ を /login/ にリダイレクト
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),  # accountsアプリをインクルード
    # 他のURLパターン...
]
