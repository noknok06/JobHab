from django.contrib import admin
from order.models import Project
from .models import UserProject, Ticket, TicketComment, TicketFavorite, Attachment, Category, Company
from django.conf import settings
from django.utils import timezone
User = settings.AUTH_USER_MODEL  # Userを参照する

# Custom admin for UserProject
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')
    search_fields = ('user__email', 'project__name')

# Custom admin for Ticket
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status_id', 'assignee', 'category', 'start_date', 'end_date', 'project', 'updated_at', 'deadline', 'created_at') 
    list_filter = ('status_id', 'assignee', 'category', 'project')
    search_fields = ('title', 'assignee__email', 'category__name', 'project__name')
    readonly_fields = ('updated_at',)
    
    # Display a formatted version of the status ID
    def formatted_status(self, obj):
        return f"Status: {obj.status_id}"
    formatted_status.short_description = 'Formatted Status'

    # Highlight overdue tickets
    def overdue(self, obj):
        return obj.deadline and obj.deadline < timezone.now()
    overdue.boolean = True
    overdue.short_description = 'Overdue'

# Custom admin for TicketComment
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'comment', 'create_date', 'attachment_file')
    search_fields = ('ticket__title', 'user__email', 'comment')
    list_filter = ('ticket', 'user')

# Custom admin for TicketFavorite
class TicketFavoriteAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user')
    search_fields = ('ticket__title', 'user__email')

# Custom admin for Attachment
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'attachment_file')
    search_fields = ('ticket__title', 'attachment_file')

# Custom admin for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')
    search_fields = ('name', 'project__name')

# Register the admin classes
admin.site.register(UserProject, UserProjectAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketComment, TicketCommentAdmin)
admin.site.register(TicketFavorite, TicketFavoriteAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Category, CategoryAdmin)
