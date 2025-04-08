from django.urls import path
from . import views

app_name = 'data_integration'

urlpatterns = [
    path('import/', views.ImportJobsView.as_view(), name='import_jobs'),
    path('stats/', views.JobStatsView.as_view(), name='job_stats'),
]
