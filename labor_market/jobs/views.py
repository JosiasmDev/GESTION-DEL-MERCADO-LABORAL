from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from data_integration.models import JobOffer

class JobListView(LoginRequiredMixin, ListView):
    model = JobOffer
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_active=True).order_by('-date_posted')
