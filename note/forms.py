from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Note, Tag, Genre

class NoteForm(forms.ModelForm):
    tags = forms.CharField(
        label='タグ',
        required=False,
        help_text="カンマ区切りで複数のタグを入力できます",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'タグを入力'})
    )

    content = forms.CharField(
        label='内容',
        widget=CKEditorWidget(attrs={'class': 'form-control', 'rows': 10})
    )

    class Meta:
        model = Note
        fields = ['title', 'content', 'genre', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditorWidget(attrs={'class': 'form-control', 'rows': 3}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        note = kwargs.get('instance')
        if note and note.pk:
            initial_tags = ', '.join(note.tags.values_list('name', flat=True))  # より簡潔な取得方法
            kwargs.setdefault('initial', {}).setdefault('tags', initial_tags)  # 既存の initial を上書きしない
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        note = super().save(commit=False)
        if commit:
            note.save()

        # タグの更新処理
        tags = self.cleaned_data['tags']
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]  # 空文字の除去
            existing_tags = list(note.tags.values_list('name', flat=True))  # 現在のタグ名リスト

            # 追加が必要なタグを取得
            new_tags = set(tag_list) - set(existing_tags)
            for tag_name in new_tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                note.tags.add(tag)

            # 削除が必要なタグを取得
            tags_to_remove = set(existing_tags) - set(tag_list)
            if tags_to_remove:
                note.tags.filter(name__in=tags_to_remove).delete()  # 関連付け解除

        return note


class NoteSearchForm(forms.Form):
    query = forms.CharField(label='キーワード検索', max_length=255, required=False)
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label="ジャンル",
        empty_label="ジャンルを選択"
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="タグ",
        empty_label="タグを選択"
    )
