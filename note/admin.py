from django.contrib import admin
from .models import Note, Tag, Genre

class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'created_at', 'updated_at')  # 表示するカラム
    search_fields = ('title', 'content')  # 検索できるフィールド
    list_filter = ('created_at', 'updated_at', 'genre')  # フィルタリングするフィールド
    filter_horizontal = ('tags',)  # ManyToManyField のフィルタリングを横並びで表示
    readonly_fields = ('created_at', 'updated_at')  # 編集不可のフィールド

    # 編集画面のカスタマイズ
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'genre')  # タイトル、コンテンツ、ジャンルを設定
        }),
        ('タグ', {
            'fields': ('tags',)  # タグを設定
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),  # 作成・更新日時（表示のみ）
        }),
    )

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)  # タグ名を表示
    search_fields = ('name',)  # タグ名で検索可能

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_path')  # ジャンル名と画像パスを表示
    search_fields = ('name',)  # ジャンル名で検索可能
    list_filter = ('name',)  # ジャンル名でフィルタリング可能

# モデルを管理画面に登録
admin.site.register(Note, NoteAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Genre, GenreAdmin)
