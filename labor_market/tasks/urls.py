from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
]
