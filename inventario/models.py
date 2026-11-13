from django.db import models


class Herramienta(models.Model):
    BUENO = 'bueno'
    REGULAR = 'regular'
    MALO = 'malo'
    ESTADO_CHOICES = [
        (BUENO, 'Bueno'),
        (REGULAR, 'Regular'),
        (MALO, 'Malo'),
    ]

    nombre_comun = models.CharField(max_length=120)
    nombre_tecnico = models.CharField(max_length=120, blank=True)
    medida = models.CharField(max_length=50, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(
        max_length=10, choices=ESTADO_CHOICES, default=BUENO
    )

    class Meta:
        ordering = ['nombre_comun']
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'

    def __str__(self):
        return self.nombre_comun

    @property
    def disponibles(self):
        prestados = sum(
            p.cantidad for p in self.prestamos.filter(devuelto=False)
        )
        return self.cantidad - prestados
