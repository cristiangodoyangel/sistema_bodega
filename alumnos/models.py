from django.db import models


class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    curso = models.CharField(max_length=50)

    class Meta:
        ordering = ['curso', 'apellido', 'nombre']
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.curso})'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'
