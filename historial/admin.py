from django.contrib import admin

from .models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('herramienta', 'alumno', 'cantidad', 'fecha_prestamo', 'devuelto')
    list_filter = ('devuelto', 'herramienta')
    search_fields = ('alumno__nombre', 'alumno__apellido', 'herramienta__nombre')
