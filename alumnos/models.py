from django.db import models


class Alumno(models.Model):
    TERCERO = '3'
    CUARTO = '4'
    CURSO_CHOICES = [
        (TERCERO, '3° Medio'),
        (CUARTO, '4° Medio'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    curso = models.CharField(max_length=1, choices=CURSO_CHOICES, default=TERCERO)

    class Meta:
        ordering = ['curso', 'apellido', 'nombre']
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.get_curso_display()})'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'
