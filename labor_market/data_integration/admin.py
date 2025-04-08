from django.contrib import admin
from .models import JobOffer, Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'employment_type', 'date_posted', 'is_active')
    list_filter = ('employment_type', 'is_active', 'location')
    search_fields = ('title', 'company', 'description')
    filter_horizontal = ('skills',)
    readonly_fields = ('date_posted',)
