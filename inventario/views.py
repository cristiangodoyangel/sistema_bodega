from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import HerramientaForm
from .models import Herramienta


class HerramientaListView(LoginRequiredMixin, ListView):
    model = Herramienta
    template_name = 'inventario/herramienta_list.html'
    context_object_name = 'herramientas'


class HerramientaCreateView(LoginRequiredMixin, CreateView):
    model = Herramienta
    form_class = HerramientaForm
    template_name = 'inventario/herramienta_form.html'
    success_url = reverse_lazy('herramienta_lista')


class HerramientaUpdateView(LoginRequiredMixin, UpdateView):
    model = Herramienta
    form_class = HerramientaForm
    template_name = 'inventario/herramienta_form.html'
    success_url = reverse_lazy('herramienta_lista')


class HerramientaDeleteView(LoginRequiredMixin, DeleteView):
    model = Herramienta
    template_name = 'inventario/herramienta_confirm_delete.html'
    success_url = reverse_lazy('herramienta_lista')
