from django.contrib import admin

from .models import Herramienta


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_total', 'disponibles', 'ubicacion')
    search_fields = ('nombre', 'ubicacion')
