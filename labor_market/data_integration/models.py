from django.db import models
from django.core.validators import MinValueValidator

class Skill(models.Model):
    name = models.CharField('Nombre', max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        ordering = ['name']

    def __str__(self):
        return self.name

class JobOffer(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Tiempo Completo'),
        ('part_time', 'Tiempo Parcial'),
        ('contract', 'Contrato'),
        ('temporary', 'Temporal'),
        ('internship', 'Prácticas'),
    ]

    title = models.CharField('Título', max_length=200)
    company = models.CharField('Empresa', max_length=200)
    location = models.CharField('Ubicación', max_length=200)
    description = models.TextField('Descripción')
    requirements = models.TextField('Requisitos')
    skills = models.ManyToManyField(
        Skill,
        related_name='job_offers',
        verbose_name='Habilidades requeridas'
    )
    salary_min = models.DecimalField(
        'Salario mínimo',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    salary_max = models.DecimalField(
        'Salario máximo',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    employment_type = models.CharField(
        'Tipo de empleo',
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES
    )
    date_posted = models.DateTimeField('Fecha de publicación', auto_now_add=True)
    is_active = models.BooleanField('Activa', default=True)
    external_id = models.CharField(
        'ID Externa',
        max_length=100,
        blank=True,
        help_text='ID de la oferta en el sistema externo'
    )
    url = models.URLField('URL de la oferta', blank=True)

    class Meta:
        verbose_name = 'Oferta de Trabajo'
        verbose_name_plural = 'Ofertas de Trabajo'
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['title', 'company']),
            models.Index(fields=['location']),
            models.Index(fields=['date_posted']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company}"

    def clean(self):
        if self.salary_max < self.salary_min:
            raise ValidationError('El salario máximo no puede ser menor que el mínimo')
