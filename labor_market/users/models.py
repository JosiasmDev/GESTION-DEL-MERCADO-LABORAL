from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[
            ('empresa', 'Empresa'),
            ('candidato', 'Candidato'),
            ('admin', 'Administrador'),
        ],
        default='candidato'
    )
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField(
        'UserProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user'
    )

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gestor', 'Gestor'),
        ('colaborador', 'Colaborador'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='colaborador'
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        permissions = [
            ("can_manage_users", "Puede gestionar usuarios"),
            ("can_create_projects", "Puede crear proyectos"),
            ("can_view_analytics", "Puede ver análisis"),
        ]

    def __str__(self):
        return f'Perfil de {self.user.username} - {self.get_role_display()}'
