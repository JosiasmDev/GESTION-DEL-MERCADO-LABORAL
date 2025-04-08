from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'created_by')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name', 'description')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'deadline')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description')
    filter_horizontal = ('assignees',)
