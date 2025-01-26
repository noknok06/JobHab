from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Project, Company, Approval, PostBilling

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 日付フィールドにDateInputウィジェットを追加
        date_fields = ['order_date', 'contract_start_date', 'contract_end_date', 'expected_booking_date']
        for field in date_fields:
            self.fields[field].widget = forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5のカレンダー対応
                    'class': 'form-control'
                }
            )

class PostAttachmentForm(forms.Form):
    files = forms.FileField(
        widget=forms.FileInput(),  # 複数ファイルを許可
        label="添付ファイル",
        required=False
    )

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'status', 'companies', 'approvals', 'remarks', 'color']  # `color`を追加
        widgets = {
            'name': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'companies': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'approvals': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),  # カラーピッカーを追加
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'master_contract': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = '__all__'
        widgets = {
            'companies': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'name': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 日付フィールドにDateInputウィジェットを追加
        date_fields = ['draft_date', 'start_date', 'end_date']
        for field in date_fields:
            self.fields[field].widget = forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5のカレンダー対応
                    'class': 'form-control'
                }
            )


class PostBillingForm(forms.ModelForm):
    class Meta:
        model = PostBilling
        fields = ['remarks', 'invoice_file']  # 'billing_date' はフォームから除外
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),  # 備考フィールドをテキストエリアに
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="メールアドレス")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'ユーザー名',
            'password1': 'パスワード',
            'password2': 'パスワード（確認）',
        }