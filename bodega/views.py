from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from alumnos.models import Alumno
from historial.models import Prestamo
from inventario.models import Herramienta


@login_required
def inicio(request):
    contexto = {
        'total_herramientas': Herramienta.objects.count(),
        'total_alumnos': Alumno.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(devuelto=False).count(),
        'prestamos_recientes': Prestamo.objects.filter(devuelto=False)[:5],
    }
    return render(request, 'inicio.html', contexto)
