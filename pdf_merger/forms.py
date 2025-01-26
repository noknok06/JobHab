from django import forms

# 複数のファイルをアップロードするウィジェットクラスを作成
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# 複数のファイルをアップロードするフィールドクラスを作成
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# 複数のファイルをアップロードするフォームクラスを作成
class MultipleFileUploadForm(forms.Form):
    files = MultipleFileField(label="複数のファイルを選択")


    # ファイルの拡張子をチェックするバリデーション
    def clean_files(self):
        files = self.files.getlist("files")  # アップロードされたファイルのリストを取得
        allowed_extensions = [".pdf"]       # 許可するファイル形式
        invalid_files = []                  # 不正なファイルを追跡

        # アップロードされた各ファイルを確認
        for file in files:
            if not file.name.lower().endswith(tuple(allowed_extensions)):
                invalid_files.append(file.name)

        # 不正なファイルがある場合はエラーを発生させる
        if invalid_files:
            raise forms.ValidationError(
                f"以下のファイルはPDF形式ではありません: {', '.join(invalid_files)}"
            )

        return files