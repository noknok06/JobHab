from django.contrib import admin
from .models import ActionLog

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'action', 'timestamp')
    list_filter = ('action', 'model_name')
    search_fields = ('details',)
