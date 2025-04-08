from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Project(models.Model):
    name = models.CharField('Nombre', max_length=200)
    description = models.TextField('Descripción', blank=True)
    start_date = models.DateField('Fecha de inicio')
    end_date = models.DateField('Fecha de fin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects_created'
    )

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-start_date']

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio')

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
        (4, 'Urgente'),
    ]

    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción')
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    priority = models.IntegerField(
        'Prioridad',
        choices=PRIORITY_CHOICES,
        default=2
    )
    deadline = models.DateTimeField('Fecha límite')
    skills = models.CharField('Habilidades requeridas', max_length=200, blank=True)
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        verbose_name='Asignados'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-priority', 'deadline']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
