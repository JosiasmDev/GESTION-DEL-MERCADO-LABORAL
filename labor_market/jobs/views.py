from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from data_integration.models import JobOffer

class JobListView(LoginRequiredMixin, ListView):
    model = JobOffer
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_active=True).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs_count'] = self.get_queryset().count()
        return context

class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = JobOffer
    success_url = reverse_lazy('jobs:job_list')
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.is_active = False
            self.object.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@method_decorator(require_POST, name='dispatch')
class JobBulkDeleteView(LoginRequiredMixin, ListView):
    model = JobOffer
    template_name = 'jobs/job_list.html'
    
    def post(self, request, *args, **kwargs):
        try:
            count = JobOffer.objects.filter(is_active=True).update(is_active=False)
            return JsonResponse({'status': 'success', 'count': count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
