from django.views.generic import ListView
from django.db import models
from django.utils.dateparse import parse_date
from .models import ActionLog

class ActionLogListView(ListView):
    model = ActionLog
    template_name = 'logger/action_log_list.html'
    context_object_name = 'action_logs'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user').order_by('-timestamp')
        search_query = self.request.GET.get('q')
        model_name_filter = self.request.GET.get('model_name')
        action_filter = self.request.GET.get('action')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if search_query:
            queryset = queryset.filter(
                models.Q(user__username__icontains=search_query) |
                models.Q(details__icontains=search_query)
            )
        if model_name_filter:
            queryset = queryset.filter(model_name=model_name_filter)
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=parse_date(end_date))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_names'] = ActionLog.objects.values_list('model_name', flat=True).distinct()
        context['actions'] = dict(ActionLog.ACTION_CHOICES)
        return context
