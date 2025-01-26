# admin.py

from django.contrib import admin
from .models import (
    Company, Project, Approval, AccountingSubject,
    Tag, Post, PostAttachment, PostBilling, PostComment
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'master_contract')
    search_fields = ('name', 'info', 'remarks')
    list_filter = ('status',)
    ordering = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    search_fields = ('name',)
    list_filter = ('status',)
    ordering = ('name',)


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_companies', 'start_date', 'end_date', 'repeat_flag', 'attached_file')
    search_fields = ('name', 'companies__name')  # 'companies' に合わせて修正
    list_filter = ('repeat_flag', 'start_date', 'end_date')
    ordering = ('start_date',)

    def display_companies(self, obj):
        """関連会社をカンマ区切りで表示"""
        return ", ".join([company.name for company in obj.companies.all()])
    display_companies.short_description = '関連会社'  # 管理画面での列名


@admin.register(AccountingSubject)
class AccountingSubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class PostAttachmentInline(admin.TabularInline):
    model = PostAttachment
    extra = 1


class PostBillingInline(admin.TabularInline):
    model = PostBilling
    extra = 1


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'project', 'status', 'contract_start_date', 'contract_end_date', 'amount')
    search_fields = ('title', 'remarks', 'company__name', 'project__name')
    list_filter = ('status', 'contract_method', 'contract_start_date', 'contract_end_date')
    ordering = ('contract_start_date',)
    inlines = [PostAttachmentInline, PostBillingInline, PostCommentInline]


@admin.register(PostAttachment)
class PostAttachmentAdmin(admin.ModelAdmin):
    list_display = ('post', 'file', 'uploaded_at')
    search_fields = ('post__title', 'file')
    ordering = ('-uploaded_at',)


@admin.register(PostBilling)
class PostBillingAdmin(admin.ModelAdmin):
    list_display = ('post', 'billing_date', 'is_checked', 'remarks')
    search_fields = ('post__title', 'remarks')
    list_filter = ('is_checked',)
    ordering = ('-billing_date',)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'updated_at')
    search_fields = ('post__title', 'user__username', 'comment_text')
    ordering = ('-created_at',)
