from django.db import models
from ckeditor.fields import RichTextField

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image_path = models.CharField(max_length=255, help_text="BootstrapのアイコンIDや画像パスを入力してください")

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()  # リッチテキスト用のウィジェット
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)  # タグを複数設定可能に
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes', help_text="ノートに紐づくジャンルを選択してください")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
