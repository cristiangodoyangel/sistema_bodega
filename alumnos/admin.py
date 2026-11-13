from django.contrib import admin

from .models import Alumno


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'curso')
    list_filter = ('curso',)
    search_fields = ('nombre', 'apellido')
