from django.core.management.base import BaseCommand

from alumnos.models import Alumno
from inventario.models import Herramienta


class Command(BaseCommand):
    help = 'Carga datos de ejemplo (alumnos y herramientas).'

    def handle(self, *args, **kwargs):
        alumnos = [
            ('Matías', 'Rojas', '3'),
            ('Camila', 'Fuentes', '3'),
            ('Benjamín', 'Soto', '3'),
            ('Javiera', 'Muñoz', '3'),
            ('Diego', 'Araya', '4'),
            ('Francisca', 'Castro', '4'),
            ('Ignacio', 'Vargas', '4'),
            ('Antonia', 'Silva', '4'),
        ]
        for nombre, apellido, curso in alumnos:
            Alumno.objects.get_or_create(
                nombre=nombre, apellido=apellido, curso=curso
            )

        herramientas = [
            ('Taladro percutor', 'Taladro eléctrico con percusión.', 3, 'Estante A1'),
            ('Llave inglesa', 'Llave ajustable 12 pulgadas.', 6, 'Estante A2'),
            ('Martillo', 'Martillo de carpintero.', 8, 'Estante A2'),
            ('Serrucho', 'Sierra manual para madera.', 4, 'Estante B1'),
            ('Caja de herramientas', 'Set completo básico.', 5, 'Estante B2'),
            ('Cinta métrica', 'Huíncha de 5 metros.', 10, 'Estante B2'),
        ]
        for nombre, descripcion, total, ubicacion in herramientas:
            Herramienta.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'cantidad_total': total,
                    'ubicacion': ubicacion,
                },
            )

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados.'))
