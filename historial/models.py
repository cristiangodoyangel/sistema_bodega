from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from alumnos.models import Alumno
from inventario.models import Herramienta


class Prestamo(models.Model):
    alumno = models.ForeignKey(
        Alumno, on_delete=models.PROTECT, related_name='prestamos'
    )
    herramienta = models.ForeignKey(
        Herramienta, on_delete=models.PROTECT, related_name='prestamos'
    )
    cantidad = models.PositiveIntegerField(default=1)
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_prestamo']
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    def __str__(self):
        estado = 'devuelto' if self.devuelto else 'prestado'
        return f'{self.herramienta} -> {self.alumno} ({estado})'

    def clean(self):
        if self.cantidad < 1:
            raise ValidationError('La cantidad debe ser al menos 1.')
        if not self.devuelto:
            prestados = sum(
                p.cantidad
                for p in self.herramienta.prestamos.filter(devuelto=False)
            )
            disponibles = self.herramienta.cantidad - prestados
            if self.cantidad > disponibles:
                raise ValidationError(
                    f'No hay stock suficiente. Disponibles: {disponibles}.'
                )

    def devolver(self):
        self.devuelto = True
        self.fecha_devolucion = timezone.now()
        self.save()
