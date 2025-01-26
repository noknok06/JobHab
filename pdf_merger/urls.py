from django.urls import path
from .views import MultipleFileUploadPage
from pdf_merger import views


app_name = 'pdf_merger'

urlpatterns = [
    path('', MultipleFileUploadPage.as_view(), name='multiple_file_upload'),
]
