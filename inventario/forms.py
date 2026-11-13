from django import forms

from .models import Herramienta


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['nombre_comun', 'nombre_tecnico', 'medida', 'cantidad', 'estado']
