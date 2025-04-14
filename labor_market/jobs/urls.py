from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('delete/<int:pk>/', views.JobDeleteView.as_view(), name='job_delete'),
    path('delete-all/', views.JobBulkDeleteView.as_view(), name='job_bulk_delete'),
]
