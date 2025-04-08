from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'fecha_registro')
    list_filter = ('tipo_usuario', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('tipo_usuario', 'telefono', 'direccion')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'departamento', 'fecha_actualizacion')
    list_filter = ('role', 'departamento')
    search_fields = ('user__username', 'departamento')
