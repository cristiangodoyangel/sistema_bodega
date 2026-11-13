from django import forms

from .models import Herramienta


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['nombre', 'descripcion', 'cantidad_total', 'ubicacion']
