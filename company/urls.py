from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('<int:company_id>/', views.company_detail, name='company_detail'),
    path('<int:company_id>/add/', views.InquiryCreateView.as_view(), name='inquiry_add'),
    path('<int:pk>/edit/', views.InquiryUpdateView.as_view(), name='inquiry_edit'),
    path('<int:company_id>/inquiry/add/', views.InquiryCreateView.as_view(), name='inquiry_add'),
    path('inquiry/<int:pk>/delete/', views.delete_inquiry, name='inquiry_delete'),
]
