from django.db import models


class Herramienta(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    cantidad_total = models.PositiveIntegerField(default=1)
    ubicacion = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'

    def __str__(self):
        return self.nombre

    @property
    def disponibles(self):
        prestados = sum(
            p.cantidad for p in self.prestamos.filter(devuelto=False)
        )
        return self.cantidad_total - prestados
