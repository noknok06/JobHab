import io
from django.db import models
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Note, Tag
from django.shortcuts import get_object_or_404, render, redirect
from .forms import NoteForm, NoteSearchForm

import os
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa

class NoteListView(ListView):
    model = Note
    template_name = 'note/note_list.html'
    context_object_name = 'notes'
    form_class = NoteSearchForm

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        tag_filter = self.request.GET.get('tag')  # タグフィルターの取得

        # 検索
        if query:
            query_terms = query.split()
            filters = models.Q()
            for term in query_terms:
                filters |= (
                    models.Q(title__icontains=term) |
                    models.Q(content__icontains=term) |
                    models.Q(tags__name__icontains=term)
                )
            queryset = queryset.filter(filters)
        
        # タグによるフィルタリング
        if tag_filter:
            queryset = queryset.filter(tags__name=tag_filter)
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # タグ一覧を取得し、各タグに関連付けられているノートのカウントを計算し、タグ数が多い順にソート
        context['tags'] = Tag.objects.annotate(note_count=Count('notes')).order_by('-note_count')

        # 現在選択されているタグを取得
        context['selected_tag'] = self.request.GET.get('tag')

        return context

class NoteCreateView(CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('note:note_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '作成'
        return context

    def form_valid(self, form):
        note = form.save()  # ノートを保存

        # タグの処理
        tags = form.cleaned_data.get('tags', '').split(',')
        for tag_name in tags:
            tag_name = tag_name.strip()  # 余分なスペースを削除
            if tag_name:  # タグが空でない場合のみ処理
                tag, created = Tag.objects.get_or_create(name=tag_name)  # タグを作成または取得
                note.tags.add(tag)  # ノートにタグを追加

        return redirect(self.success_url)  # 成功後、リダイレクト


class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'note/note_form.html'
    success_url = reverse_lazy('note:note_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '編集'
        note = self.get_object()  # 現在のノートオブジェクトを取得
        # タグをカンマ区切りの文字列として表示
        context['tags'] = ', '.join([tag.name for tag in note.tags.all()])  # タグの名前をカンマ区切りで取得
        return context

    def form_valid(self, form):
        # フォームが正しい場合、まずノートを保存
        note = form.save()

        # タグの処理
        tags = self.request.POST.get('tags', '').split(',')
        note.tags.clear()  # 既存のタグをクリア

        for tag_name in tags:
            tag_name = tag_name.strip()  # 余分なスペースを削除
            if tag_name:  # タグが空でない場合のみ処理
                tag, created = Tag.objects.get_or_create(name=tag_name)  # タグを作成または取得
                note.tags.add(tag)  # ノートにタグを追加

        return redirect(self.success_url)  # 成功後、リダイレクト
        
class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'note/note_confirm_delete.html'
    success_url = reverse_lazy('note:note_list')

class NoteDetailView(DetailView):
    model = Note
    template_name = 'note/note_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.object

        # 同じタグまたはジャンルを持つ関連ノートを取得
        related_notes = Note.objects.filter(
            tags__in=note.tags.all()
        ).exclude(id=note.id).annotate(
            common_tags=Count('tags')
        ).order_by('-common_tags', '-created_at')[:5]  # タグ一致数が多い順

        context['related_notes'] = related_notes
        return context

def render_to_pdf(template_src, context_dict={}):
    # テンプレートをレンダリングして HTML を生成
    template = get_template(template_src)
    html = template.render(context_dict)

    # PDF 出力のためのレスポンス設定
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="note.pdf"'

    # PDFの作成
    result = io.BytesIO()  # バイナリストリーム
    pisa_status = pisa.pisaDocument(
        io.BytesIO(html.encode('utf-8')),  # HTML をエンコード
        result,  # 出力先
        link_callback=link_callback,  # 静的ファイル参照用のコールバック
        encoding='utf-8'  # 文字エンコーディングの指定
    )

    if pisa_status.err:
        return HttpResponse('PDF生成に失敗しました', status=400)

    # PDFの生成が成功した場合
    response.write(result.getvalue())
    return response

def note_pdf_view(request, pk):
    # Note モデルからデータを取得
    note = Note.objects.get(pk=pk)
    context = {'note': note, 'STATIC_URL': settings.STATIC_URL}
    # render_to_pdf を使って PDF を生成
    return render_to_pdf('note/note_pdf_template.html', context)

def link_callback(uri, rel):

    # 外部 URL（Google Fonts など）は無視する
    if uri.startswith('http'):
        return uri  # そのまま返す（または None にする）

    # 静的ファイルのパスを取得
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    path = os.path.join(sRoot, uri.replace(sUrl, ""))

    if not os.path.isfile(path):
        raise Exception('%s must start with %s' % (uri, sUrl))

    return path