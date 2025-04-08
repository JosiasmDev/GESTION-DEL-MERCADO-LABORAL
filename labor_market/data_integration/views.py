from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.core.management import call_command
from .models import JobOffer  # Añadir esta importación

# Create your views here.

class ImportJobsView(UserPassesTestMixin, TemplateView):
    template_name = 'data_integration/import_jobs.html'
    
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        try:
            call_command('import_jobs')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class JobStatsView(UserPassesTestMixin, TemplateView):
    template_name = 'data_integration/job_stats.html'
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_jobs'] = JobOffer.objects.count()
        context['active_jobs'] = JobOffer.objects.filter(is_active=True).count()
        return context
