from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import PrestamoForm
from .models import Prestamo


class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'historial/prestamo_list.html'
    context_object_name = 'prestamos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activos'] = Prestamo.objects.filter(devuelto=False)
        context['devueltos'] = Prestamo.objects.filter(devuelto=True)
        return context


class PrestamoCreateView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'historial/prestamo_form.html'
    success_url = reverse_lazy('prestamo_lista')


@login_required
def devolver_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if not prestamo.devuelto:
        prestamo.devolver()
        messages.success(request, f'{prestamo.herramienta} devuelta correctamente.')
    return redirect('prestamo_lista')
