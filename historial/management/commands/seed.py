from django.core.management.base import BaseCommand

from alumnos.models import Alumno
from inventario.models import Herramienta


class Command(BaseCommand):
    help = 'Carga datos de ejemplo (alumnos y herramientas).'

    def handle(self, *args, **kwargs):
        alumnos = [
            ('AARON MISAEL', 'ALFARO PÉREZ'),
            ('SEBASTIÁN ALFONSO', 'ÁLVAREZ MENDOZA'),
            ('BENJAMÍN ALEXANDER', 'BAUTISTA CÓRDOVA'),
            ('FRANCISCA MARÍA', 'BLANCO ROMO'),
            ('KURT BAYRON', 'BRAVO RODAS'),
            ('JACOB IKER', 'CASTILLO RIQUELME'),
            ('MIGUEL-ANGEL', 'CERDA AILLAL'),
            ('BENJAMÍN GLEEN', 'CONTRERAS FLORES'),
            ('MATÍAS IGNACIO', 'CORTÉS MONTALVÁN'),
            ('CRISTHIAN NICOLÁS', 'CORTÉS VARELA'),
            ('ELÍAS YAIR', 'DÍAZ LARA'),
            ('SEBASTIÁN JESÚS', 'DONOSO TAPIA'),
            ('IGNACIO BASTIÁN', 'FERNÁNDEZ ESPINOZA'),
            ('JUAN EDUARDO', 'GÓMEZ CASTILLO'),
            ('JHON ALEXANDER', 'GONZALEZ PARRA'),
            ('AARON ANDRÉS', 'GORDILLO RIVERA'),
            ('ENOC', 'IÑIGUEZ VARGAS'),
            ('BRYAN DARÍO', 'JIMÉNEZ HERNÁNDEZ'),
            ('LEONARDO', 'LARA CALIZAYA'),
            ('JORGE LEONARDO', 'LÓPEZ GUATUME'),
            ('NICOLÁS EDWARD', 'MARABOLÍ DÍAZ'),
            ('DYLAN JOSUETH', 'MEDINA PERÉZ'),
            ('JORGE JOHN DIALIZANDRO', 'MOLINA GUZMÁN'),
            ('AMARAL TRINIDAD', 'MORGADO GÓMEZ'),
            ('AMARO ANDRÉS', 'MUNDACA MUÑOZ'),
            ('MATÍAS IGNACIO', 'NÚÑEZ RIVERA'),
            ('MARTÍN IGNACIO', 'PÁEZ IGLESIAS'),
            ('GERARD ALEXI', 'PERALTA VARGAS'),
            ('GASPAR ALONSO', 'SAAVEDRA ALFARO'),
            ('MELANIE FRANCOISE', 'TAPIA BRICEÑO'),
            ('ARANTZA JAVIERA', 'VILLALOBOS GONZÁLEZ'),
            ('MILEY ASHLEY', 'HINOSTROZA ADAUTO'),
            ('MICHELLE ALEJANDRA', 'FLORES MOLINA'),
        ]
        for nombre, apellido in alumnos:
            Alumno.objects.get_or_create(
                nombre=nombre, apellido=apellido, curso='3ro A - MI'
            )

        herramientas = [
            ('Esmeril', 'Esmeril angular / de banco', '', 1),
            ('Máquina de soldar', 'Soldadora eléctrica (arco manual / inverter)', '', 3),
            ('Regla metálica', 'Regla graduada de acero inoxidable', '', 50),
            ('Flexómetro', 'Cinta métrica retráctil', '', 20),
            ('Escuadra', 'Escuadra metálica / de talón', '', 5),
            ('Torno', 'Torno mecánico paralelo', '', 10),
            ('Llave de esmeril', 'Llave de puntos para esmeril angular', '', 13),
            ('Reloj comparador', 'Comparador de carátula', '', 6),
            ('Micrómetro', 'Tornillo micrométrico / Palmer', '', 11),
            ('Cotona', 'Delantal / Guardapolvo de trabajo', '', 10),
            ('Casco', 'Casco de seguridad industrial', 'Estándar', 8),
            ('Pie de metro (metálico)', 'Calibrador Vernier de acero', '', 50),
            ('Pie de metro (plástico)', 'Calibrador Vernier de plástico / polímero', '', 5),
            ('Fresadora', 'Máquina fresadora', '', 6),
            ('Pantalón de soldar', 'Pantalón de descarne para soldador', '', 10),
            ('Tester', 'Multímetro digital / analógico', '', 2),
            ('Llave punta corona', 'Llave combinada (boca fija y estrella)', '12 mm', 3),
            ('Llave punta corona', 'Llave combinada (boca fija y estrella)', '16 mm', 2),
            ('Llave punta corona', 'Llave combinada (boca fija y estrella)', '8 mm', 2),
            ('Alicate', 'Alicate universal', '', 5),
            ('Alicate de punta', 'Alicate de punta larga / semiredonda', '', 5),
            ('Taladro', 'Taladro eléctrico con cable', '', 1),
            ('Taladro inalámbrico', 'Taladro atornillador a batería', '', 2),
            ('Soldadora oxicorte', 'Equipo de soldadura y corte oxiacetilénico', '', 2),
            ('Martillo carpintero', 'Martillo de uña / galponero', '', 5),
            ('Nivel', 'Nivel de burbuja / de mano', '', 4),
            ('Máscara de soldar', 'Careta de soldar (fotosensible o vidrio fijo)', 'Estándar', 2),
            ('Lentes', 'Lentes / Antiparras de seguridad', 'Estándar', 10),
            ('Gorro de soldar', 'Capucha / Pasamontañas ignífugo de soldador', 'Estándar', 10),
            ('Chaqueta', 'Chaqueta de descarne para soldador', '', 5),
        ]
        for comun, tecnico, medida, cantidad in herramientas:
            Herramienta.objects.get_or_create(
                nombre_comun=comun,
                nombre_tecnico=tecnico,
                medida=medida,
                defaults={'cantidad': cantidad},
            )

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados.'))
