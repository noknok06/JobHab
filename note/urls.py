from django.urls import path
from .views import NoteListView, NoteCreateView, NoteUpdateView, NoteDeleteView, NoteDetailView
from note import views

app_name = 'note'

urlpatterns = [
    path('', NoteListView.as_view(), name='note_list'),
    path('create/', NoteCreateView.as_view(), name='note_create'),
    path('<int:pk>/edit/', NoteUpdateView.as_view(), name='note_edit'),
    path('<int:pk>/delete/', NoteDeleteView.as_view(), name='note_delete'),
    path('<int:pk>/', NoteDetailView.as_view(), name='note_detail'),
    path('<int:pk>/pdf/', views.note_pdf_view, name='note_pdf'),
]
