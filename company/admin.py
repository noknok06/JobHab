from django.contrib import admin
from .models import Inquiry, Todo
from order.models import Project, Company  # 発注情報、プロジェクト、会社情報

class InquiryAdmin(admin.ModelAdmin):
    list_display = ('company', 'project', 'category', 'question_date', 'answer_date')
    list_filter = ('company', 'category', 'question_date', 'answer_date')
    search_fields = ('company__name', 'project__name', 'category', 'question')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            if request.user.is_superuser:
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            if 'company_id' in request.GET:
                kwargs["queryset"] = Project.objects.filter(company_id=request.GET.get('company_id'))
            else:
                kwargs["queryset"] = Project.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('company', 'task', 'is_completed')
    list_filter = ('company', 'is_completed')
    search_fields = ('task', 'company__name')
                     
admin.site.register(Inquiry, InquiryAdmin)
