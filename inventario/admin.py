from django.contrib import admin

from .models import Herramienta


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre_comun', 'nombre_tecnico', 'medida', 'cantidad', 'disponibles', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre_comun', 'nombre_tecnico')
