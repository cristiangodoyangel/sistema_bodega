# Sistema de Bodega — Liceo A-26 Oscar Bonilla

Guía paso a paso para construir el sistema de préstamo de herramientas del pañol.
Django + SQLite, sin dependencias extra. Tres apps: `inventario`, `alumnos`, `historial`.

## Qué hace el sistema
- Registra **herramientas** (inventario).
- Registra **alumnos** de 3° y 4° medio.
- Registra **préstamos** (alumno + herramienta + cantidad) y devoluciones.
- Valida que no se presten más herramientas de las disponibles.
- Todo protegido con **login** (auth nativo de Django).

## Colores
- Azul marino `#0F2A4A` — navbar, cabeceras.
- Amarillo `#F5B700` — botones, acentos.
- Blanco `#FFFFFF` — fondo y tarjetas.

---

## Requisitos
- Python 3.10 o superior.
- Django 5.2 (`pip install Django`).

## Estructura final
```
sistema_bodega/
├── manage.py
├── bodega/          # proyecto (settings, urls, wsgi, asgi, views)
├── inventario/      # app: herramientas
├── alumnos/         # app: estudiantes
├── historial/       # app: préstamos
├── templates/       # base.html, inicio.html, login.html
├── static/css/      # estilos.css
└── db.sqlite3
```

---

## Paso 1 — Crear proyecto y entorno virtual

```powershell
# crear carpeta y entrar
mkdir sistema_bodega
cd sistema_bodega

# entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# instalar Django
pip install Django

# crear proyecto (el punto = crear en la carpeta actual)
django-admin startproject bodega .
```

## Paso 2 — Crear las 3 apps

```powershell
python manage.py startapp inventario
python manage.py startapp alumnos
python manage.py startapp historial
```

## Paso 3 — Configurar `bodega/settings.py`

Editar el archivo y dejar los siguientes valores.

Registrar las apps en `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventario',
    'alumnos',
    'historial',
]
```

Carpeta de templates global:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Idioma, zona horaria y archivos estáticos:
```python
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

Login (redirigir a páginas correctas):
```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'login'
```

---

## Paso 4 — Modelos

### `alumnos/models.py`
```python
from django.db import models


class Alumno(models.Model):
    TERCERO = '3'
    CUARTO = '4'
    CURSO_CHOICES = [
        (TERCERO, '3° Medio'),
        (CUARTO, '4° Medio'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    curso = models.CharField(max_length=1, choices=CURSO_CHOICES, default=TERCERO)

    class Meta:
        ordering = ['curso', 'apellido', 'nombre']
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.get_curso_display()})'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'
```

### `inventario/models.py`
```python
from django.db import models


class Herramienta(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    cantidad_total = models.PositiveIntegerField(default=1)
    ubicacion = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'

    def __str__(self):
        return self.nombre

    @property
    def disponibles(self):
        prestados = sum(
            p.cantidad for p in self.prestamos.filter(devuelto=False)
        )
        return self.cantidad_total - prestados
```

### `historial/models.py`
```python
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from alumnos.models import Alumno
from inventario.models import Herramienta


class Prestamo(models.Model):
    alumno = models.ForeignKey(
        Alumno, on_delete=models.PROTECT, related_name='prestamos'
    )
    herramienta = models.ForeignKey(
        Herramienta, on_delete=models.PROTECT, related_name='prestamos'
    )
    cantidad = models.PositiveIntegerField(default=1)
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_prestamo']
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    def __str__(self):
        estado = 'devuelto' if self.devuelto else 'prestado'
        return f'{self.herramienta} -> {self.alumno} ({estado})'

    def clean(self):
        if self.cantidad < 1:
            raise ValidationError('La cantidad debe ser al menos 1.')
        if not self.devuelto:
            prestados = sum(
                p.cantidad
                for p in self.herramienta.prestamos.filter(devuelto=False)
            )
            disponibles = self.herramienta.cantidad_total - prestados
            if self.cantidad > disponibles:
                raise ValidationError(
                    f'No hay stock suficiente. Disponibles: {disponibles}.'
                )

    def devolver(self):
        self.devuelto = True
        self.fecha_devolucion = timezone.now()
        self.save()
```

> **Explicación:** `Herramienta.disponibles` calcula stock restando los préstamos no devueltos.
> `Prestamo.clean()` valida el stock al guardar. `devolver()` marca la devolución.

---

## Paso 5 — Migraciones

```powershell
python manage.py makemigrations
python manage.py migrate
```

---

## Paso 6 — Admin (para gestionar desde `/admin/`)

### `alumnos/admin.py`
```python
from django.contrib import admin

from .models import Alumno


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'curso')
    list_filter = ('curso',)
    search_fields = ('nombre', 'apellido')
```

### `inventario/admin.py`
```python
from django.contrib import admin

from .models import Herramienta


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_total', 'disponibles', 'ubicacion')
    search_fields = ('nombre', 'ubicacion')
```

### `historial/admin.py`
```python
from django.contrib import admin

from .models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('herramienta', 'alumno', 'cantidad', 'fecha_prestamo', 'devuelto')
    list_filter = ('devuelto', 'herramienta')
    search_fields = ('alumno__nombre', 'alumno__apellido', 'herramienta__nombre')
```

---

## Paso 7 — Forms

### `alumnos/forms.py`
```python
from django import forms

from .models import Alumno


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'curso']
```

### `inventario/forms.py`
```python
from django import forms

from .models import Herramienta


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['nombre', 'descripcion', 'cantidad_total', 'ubicacion']
```

### `historial/forms.py`
```python
from django import forms

from .models import Prestamo


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['alumno', 'herramienta', 'cantidad']
```

---

## Paso 8 — Vistas

### `alumnos/views.py`
```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import AlumnoForm
from .models import Alumno


class AlumnoListView(LoginRequiredMixin, ListView):
    model = Alumno
    template_name = 'alumnos/alumno_list.html'
    context_object_name = 'alumnos'


class AlumnoCreateView(LoginRequiredMixin, CreateView):
    model = Alumno
    form_class = AlumnoForm
    template_name = 'alumnos/alumno_form.html'
    success_url = reverse_lazy('alumno_lista')


class AlumnoUpdateView(LoginRequiredMixin, UpdateView):
    model = Alumno
    form_class = AlumnoForm
    template_name = 'alumnos/alumno_form.html'
    success_url = reverse_lazy('alumno_lista')


class AlumnoDeleteView(LoginRequiredMixin, DeleteView):
    model = Alumno
    template_name = 'alumnos/alumno_confirm_delete.html'
    success_url = reverse_lazy('alumno_lista')
```

### `inventario/views.py`
```python
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
```

### `historial/views.py`
```python
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
```

### `bodega/views.py` (panel de inicio)
```python
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
```

---

## Paso 9 — URLs

### `alumnos/urls.py`
```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.AlumnoListView.as_view(), name='alumno_lista'),
    path('nuevo/', views.AlumnoCreateView.as_view(), name='alumno_nuevo'),
    path('<int:pk>/editar/', views.AlumnoUpdateView.as_view(), name='alumno_editar'),
    path('<int:pk>/eliminar/', views.AlumnoDeleteView.as_view(), name='alumno_eliminar'),
]
```

### `inventario/urls.py`
```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.HerramientaListView.as_view(), name='herramienta_lista'),
    path('nueva/', views.HerramientaCreateView.as_view(), name='herramienta_nueva'),
    path('<int:pk>/editar/', views.HerramientaUpdateView.as_view(), name='herramienta_editar'),
    path('<int:pk>/eliminar/', views.HerramientaDeleteView.as_view(), name='herramienta_eliminar'),
]
```

### `historial/urls.py`
```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.PrestamoListView.as_view(), name='prestamo_lista'),
    path('nuevo/', views.PrestamoCreateView.as_view(), name='prestamo_nuevo'),
    path('<int:pk>/devolver/', views.devolver_prestamo, name='prestamo_devolver'),
]
```

### `bodega/urls.py` (proyecto)
```python
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.inicio, name='inicio'),
    path('inventario/', include('inventario.urls')),
    path('alumnos/', include('alumnos.urls')),
    path('historial/', include('historial.urls')),
]
```

---

## Paso 10 — Templates

Crear la carpeta `templates/` en la raíz del proyecto.

### `templates/base.html`
```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block titulo %}Bodega{% endblock %} · Liceo A-26 Oscar Bonilla</title>
    <link rel="stylesheet" href="{% static 'css/estilos.css' %}">
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar">
        <a href="{% url 'inicio' %}" class="brand">
            <span class="logo">B</span>
            <span>Bodega · Liceo A-26</span>
        </a>
        <div class="nav-links">
            <a href="{% url 'inicio' %}" class="{% if 'inicio' == request.resolver_match.url_name %}activo{% endif %}">Inicio</a>
            <a href="{% url 'herramienta_lista' %}" class="{% if 'herramienta' in request.resolver_match.url_name %}activo{% endif %}">Inventario</a>
            <a href="{% url 'alumno_lista' %}" class="{% if 'alumno' in request.resolver_match.url_name %}activo{% endif %}">Alumnos</a>
            <a href="{% url 'prestamo_lista' %}" class="{% if 'prestamo' in request.resolver_match.url_name %}activo{% endif %}">Historial</a>
            <form action="{% url 'logout' %}" method="post" style="margin:0">
                {% csrf_token %}
                <button type="submit" class="btn btn-pequeno salir">Salir</button>
            </form>
        </div>
    </nav>
    {% endif %}

    <main class="contenido">
        {% if messages %}
        <div class="mensajes">
            {% for message in messages %}
            <div class="alerta {% if message.tags == 'success' %}exito{% else %}error{% endif %}">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% block contenido %}{% endblock %}
    </main>

    <footer class="pie">
        Liceo A-26 <span>Oscar Bonilla</span> · Sistema de Bodega
    </footer>
</body>
</html>
```

### `templates/login.html`
```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar sesión · Bodega Liceo A-26</title>
    <link rel="stylesheet" href="{% static 'css/estilos.css' %}">
</head>
<body>
    <div class="login-pagina">
        <div class="login-caja">
            <div class="logo-grande">B</div>
            <h1>Bodega Liceo A-26</h1>
            <p>Oscar Bonilla · Acceso al pañol</p>

            {% if form.errors %}
            <div class="alerta error">Usuario o contraseña incorrectos.</div>
            {% endif %}

            <form method="post">
                {% csrf_token %}
                <div class="campo">
                    <label for="id_username">Usuario</label>
                    <input type="text" name="username" id="id_username" autofocus required>
                </div>
                <div class="campo">
                    <label for="id_password">Contraseña</label>
                    <input type="password" name="password" id="id_password" required>
                </div>
                <button type="submit" class="btn btn-primario" style="width:100%">Entrar</button>
            </form>
        </div>
    </div>
</body>
</html>
```

### `templates/inicio.html`
```html
{% extends 'base.html' %}

{% block titulo %}Inicio{% endblock %}

{% block contenido %}
<div class="encabezado">
    <div>
        <h1>Panel de Bodega</h1>
        <p class="subtitulo">Préstamo de herramientas a los cursos de 3° y 4° medio.</p>
    </div>
    <a href="{% url 'prestamo_nuevo' %}" class="btn btn-primario">+ Nuevo préstamo</a>
</div>

<div class="cards">
    <div class="card">
        <div class="numero">{{ total_herramientas }}</div>
        <div class="etiqueta">Herramientas registradas</div>
    </div>
    <div class="card">
        <div class="numero">{{ total_alumnos }}</div>
        <div class="etiqueta">Alumnos registrados</div>
    </div>
    <div class="card">
        <div class="numero">{{ prestamos_activos }}</div>
        <div class="etiqueta">Préstamos activos</div>
    </div>
</div>

<div class="panel">
    <h2 class="titulo-seccion">Préstamos activos</h2>
    {% if prestamos_recientes %}
    <table>
        <thead>
            <tr>
                <th>Herramienta</th>
                <th>Alumno</th>
                <th>Cantidad</th>
                <th>Fecha</th>
            </tr>
        </thead>
        <tbody>
            {% for p in prestamos_recientes %}
            <tr>
                <td>{{ p.herramienta.nombre }}</td>
                <td>{{ p.alumno }}</td>
                <td>{{ p.cantidad }}</td>
                <td>{{ p.fecha_prestamo|date:"d/m/Y H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="vacio">No hay préstamos activos por el momento.</p>
    {% endif %}
</div>
{% endblock %}
```

### Templates de `inventario/` (dentro de `inventario/templates/inventario/`)

`herramienta_list.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Inventario{% endblock %}

{% block contenido %}
<div class="encabezado">
    <div>
        <h1>Inventario</h1>
        <p class="subtitulo">Herramientas disponibles en el pañol.</p>
    </div>
    <a href="{% url 'herramienta_nueva' %}" class="btn btn-primario">+ Nueva herramienta</a>
</div>

<div class="panel">
    {% if herramientas %}
    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Total</th>
                <th>Disponibles</th>
                <th>Ubicación</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {% for h in herramientas %}
            <tr>
                <td>{{ h.nombre }}</td>
                <td>{{ h.cantidad_total }}</td>
                <td>
                    {% if h.disponibles > 0 %}
                    <span class="badge ok">{{ h.disponibles }}</span>
                    {% else %}
                    <span class="badge sin-stock">Sin stock</span>
                    {% endif %}
                </td>
                <td>{{ h.ubicacion|default:"—" }}</td>
                <td>
                    <div class="acciones">
                        <a href="{% url 'herramienta_editar' h.pk %}" class="btn btn-secundario btn-pequeno">Editar</a>
                        <a href="{% url 'herramienta_eliminar' h.pk %}" class="btn btn-peligro btn-pequeno">Eliminar</a>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="vacio">No hay herramientas registradas.</p>
    {% endif %}
</div>
{% endblock %}
```

`herramienta_form.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Herramienta{% endblock %}

{% block contenido %}
<div class="encabezado">
    <h1>{% if object %}Editar herramienta{% else %}Nueva herramienta{% endif %}</h1>
</div>

<div class="panel formulario">
    <form method="post">
        {% csrf_token %}
        {% for campo in form %}
        <div class="campo">
            <label for="{{ campo.id_for_label }}">{{ campo.label }}</label>
            {{ campo }}
            {% if campo.errors %}{{ campo.errors }}{% endif %}
        </div>
        {% endfor %}
        <div class="botones">
            <button type="submit" class="btn btn-primario">Guardar</button>
            <a href="{% url 'herramienta_lista' %}" class="btn btn-secundario">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

`herramienta_confirm_delete.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Eliminar herramienta{% endblock %}

{% block contenido %}
<div class="panel" style="max-width:520px">
    <h2 class="titulo-seccion">Eliminar herramienta</h2>
    <p>¿Seguro que deseas eliminar <strong>{{ object.nombre }}</strong>?</p>
    <form method="post">
        {% csrf_token %}
        <div class="botones">
            <button type="submit" class="btn btn-peligro">Sí, eliminar</button>
            <a href="{% url 'herramienta_lista' %}" class="btn btn-secundario">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

### Templates de `alumnos/` (dentro de `alumnos/templates/alumnos/`)

`alumno_list.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Alumnos{% endblock %}

{% block contenido %}
<div class="encabezado">
    <div>
        <h1>Alumnos</h1>
        <p class="subtitulo">Estudiantes de 3° y 4° medio.</p>
    </div>
    <a href="{% url 'alumno_nuevo' %}" class="btn btn-primario">+ Nuevo alumno</a>
</div>

<div class="panel">
    {% if alumnos %}
    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Apellido</th>
                <th>Curso</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {% for a in alumnos %}
            <tr>
                <td>{{ a.nombre }}</td>
                <td>{{ a.apellido }}</td>
                <td><span class="badge devuelto">{{ a.get_curso_display }}</span></td>
                <td>
                    <div class="acciones">
                        <a href="{% url 'alumno_editar' a.pk %}" class="btn btn-secundario btn-pequeno">Editar</a>
                        <a href="{% url 'alumno_eliminar' a.pk %}" class="btn btn-peligro btn-pequeno">Eliminar</a>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="vacio">No hay alumnos registrados.</p>
    {% endif %}
</div>
{% endblock %}
```

`alumno_form.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Alumno{% endblock %}

{% block contenido %}
<div class="encabezado">
    <h1>{% if object %}Editar alumno{% else %}Nuevo alumno{% endif %}</h1>
</div>

<div class="panel formulario">
    <form method="post">
        {% csrf_token %}
        {% for campo in form %}
        <div class="campo">
            <label for="{{ campo.id_for_label }}">{{ campo.label }}</label>
            {{ campo }}
            {% if campo.errors %}{{ campo.errors }}{% endif %}
        </div>
        {% endfor %}
        <div class="botones">
            <button type="submit" class="btn btn-primario">Guardar</button>
            <a href="{% url 'alumno_lista' %}" class="btn btn-secundario">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

`alumno_confirm_delete.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Eliminar alumno{% endblock %}

{% block contenido %}
<div class="panel" style="max-width:520px">
    <h2 class="titulo-seccion">Eliminar alumno</h2>
    <p>¿Seguro que deseas eliminar a <strong>{{ object }}</strong>?</p>
    <form method="post">
        {% csrf_token %}
        <div class="botones">
            <button type="submit" class="btn btn-peligro">Sí, eliminar</button>
            <a href="{% url 'alumno_lista' %}" class="btn btn-secundario">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

### Templates de `historial/` (dentro de `historial/templates/historial/`)

`prestamo_list.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Historial{% endblock %}

{% block contenido %}
<div class="encabezado">
    <div>
        <h1>Historial de préstamos</h1>
        <p class="subtitulo">Registro de préstamos y devoluciones.</p>
    </div>
    <a href="{% url 'prestamo_nuevo' %}" class="btn btn-primario">+ Nuevo préstamo</a>
</div>

<div class="panel">
    <h2 class="titulo-seccion">Préstamos activos</h2>
    {% if activos %}
    <table>
        <thead>
            <tr>
                <th>Herramienta</th>
                <th>Alumno</th>
                <th>Cantidad</th>
                <th>Fecha</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {% for p in activos %}
            <tr>
                <td>{{ p.herramienta.nombre }}</td>
                <td>{{ p.alumno }}</td>
                <td>{{ p.cantidad }}</td>
                <td>{{ p.fecha_prestamo|date:"d/m/Y H:i" }}</td>
                <td>
                    <form action="{% url 'prestamo_devolver' p.pk %}" method="post" style="margin:0">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-secundario btn-pequeno">Devolver</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="vacio">No hay préstamos activos.</p>
    {% endif %}
</div>

<div class="panel">
    <h2 class="titulo-seccion">Devueltos</h2>
    {% if devueltos %}
    <table>
        <thead>
            <tr>
                <th>Herramienta</th>
                <th>Alumno</th>
                <th>Cantidad</th>
                <th>Prestado</th>
                <th>Devuelto</th>
            </tr>
        </thead>
        <tbody>
            {% for p in devueltos %}
            <tr>
                <td>{{ p.herramienta.nombre }}</td>
                <td>{{ p.alumno }}</td>
                <td>{{ p.cantidad }}</td>
                <td>{{ p.fecha_prestamo|date:"d/m/Y H:i" }}</td>
                <td>{{ p.fecha_devolucion|date:"d/m/Y H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="vacio">Aún no hay devoluciones registradas.</p>
    {% endif %}
</div>
{% endblock %}
```

`prestamo_form.html`:
```html
{% extends 'base.html' %}

{% block titulo %}Nuevo préstamo{% endblock %}

{% block contenido %}
<div class="encabezado">
    <h1>Nuevo préstamo</h1>
</div>

<div class="panel formulario">
    <form method="post">
        {% csrf_token %}
        {% for campo in form %}
        <div class="campo">
            <label for="{{ campo.id_for_label }}">{{ campo.label }}</label>
            {{ campo }}
            {% if campo.errors %}{{ campo.errors }}{% endif %}
        </div>
        {% endfor %}
        <div class="botones">
            <button type="submit" class="btn btn-primario">Registrar préstamo</button>
            <a href="{% url 'prestamo_lista' %}" class="btn btn-secundario">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

---

## Paso 11 — CSS

Crear la carpeta `static/css/` y el archivo `estilos.css`:

```css
:root {
    --azul: #0F2A4A;
    --azul-oscuro: #0a1d35;
    --amarillo: #F5B700;
    --amarillo-suave: #fff4cf;
    --blanco: #ffffff;
    --gris: #f4f6f9;
    --gris-texto: #5a6572;
    --borde: #e3e8ef;
    --verde: #1e8e5a;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--gris);
    color: #22303f;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

a {
    text-decoration: none;
    color: inherit;
}

.navbar {
    background: var(--azul);
    color: var(--blanco);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    height: 64px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 18px;
}

.brand .logo {
    background: var(--amarillo);
    color: var(--azul);
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}

.nav-links {
    display: flex;
    gap: 6px;
    align-items: center;
}

.nav-links a {
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    color: #dfe6ef;
    transition: background 0.15s ease, color 0.15s ease;
}

.nav-links a:hover {
    background: rgba(255, 255, 255, 0.12);
    color: var(--blanco);
}

.nav-links a.activo {
    background: var(--amarillo);
    color: var(--azul);
}

.nav-links .salir {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.25);
}

.nav-links .salir:hover {
    background: #c0392b;
    border-color: #c0392b;
}

.contenido {
    flex: 1;
    width: 100%;
    max-width: 1080px;
    margin: 0 auto;
    padding: 28px 20px 48px;
}

.encabezado {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
    flex-wrap: wrap;
    gap: 12px;
}

.encabezado h1 {
    margin: 0;
    font-size: 26px;
    color: var(--azul);
}

.subtitulo {
    color: var(--gris-texto);
    margin: 4px 0 0;
}

.titulo-seccion {
    color: var(--azul);
    border-left: 5px solid var(--amarillo);
    padding-left: 12px;
    margin: 0 0 16px;
    font-size: 20px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 18px;
    margin-bottom: 30px;
}

.card {
    background: var(--blanco);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    border-top: 4px solid var(--amarillo);
}

.card .numero {
    font-size: 34px;
    font-weight: 800;
    color: var(--azul);
}

.card .etiqueta {
    color: var(--gris-texto);
    font-size: 14px;
    margin-top: 4px;
}

.panel {
    background: var(--blanco);
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    margin-bottom: 24px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    text-align: left;
    background: var(--azul);
    color: var(--blanco);
    padding: 11px 14px;
    font-size: 13px;
    font-weight: 600;
}

td {
    padding: 11px 14px;
    border-bottom: 1px solid var(--borde);
    font-size: 14px;
}

tr:hover td {
    background: #fafbfd;
}

.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge.prestado {
    background: var(--amarillo-suave);
    color: #8a6400;
}

.badge.devuelto {
    background: #e4f4ec;
    color: var(--verde);
}

.badge.sin-stock {
    background: #fdecea;
    color: #c0392b;
}

.badge.ok {
    background: #e4f4ec;
    color: var(--verde);
}

.btn {
    display: inline-block;
    padding: 9px 16px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.05s ease, filter 0.15s ease;
}

.btn:active {
    transform: scale(0.97);
}

.btn-primario {
    background: var(--amarillo);
    color: var(--azul);
}

.btn-primario:hover {
    filter: brightness(1.05);
}

.btn-secundario {
    background: var(--azul);
    color: var(--blanco);
}

.btn-secundario:hover {
    filter: brightness(1.15);
}

.btn-peligro {
    background: #c0392b;
    color: var(--blanco);
}

.btn-pequeno {
    padding: 5px 12px;
    font-size: 13px;
}

.acciones {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.formulario {
    max-width: 520px;
}

.campo {
    margin-bottom: 16px;
}

.campo label {
    display: block;
    font-weight: 600;
    font-size: 13px;
    color: var(--azul);
    margin-bottom: 6px;
}

.campo input,
.campo select,
.campo textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--borde);
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    background: var(--blanco);
}

.campo input:focus,
.campo select:focus,
.campo textarea:focus {
    outline: 2px solid var(--amarillo);
    border-color: var(--amarillo);
}

.errorlist {
    color: #c0392b;
    font-size: 13px;
    margin: 6px 0 0;
    padding-left: 18px;
}

.mensajes {
    margin-bottom: 18px;
}

.alerta {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 10px;
    font-size: 14px;
}

.alerta.exito {
    background: #e4f4ec;
    color: var(--verde);
    border-left: 4px solid var(--verde);
}

.alerta.error {
    background: #fdecea;
    color: #c0392b;
    border-left: 4px solid #c0392b;
}

.vacio {
    text-align: center;
    color: var(--gris-texto);
    padding: 30px;
}

.login-pagina {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, var(--azul) 0%, var(--azul-oscuro) 100%);
    padding: 20px;
}

.login-caja {
    background: var(--blanco);
    border-radius: 14px;
    padding: 34px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.login-caja .logo-grande {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    background: var(--amarillo);
    color: var(--azul);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 14px;
}

.login-caja h1 {
    margin: 0 0 4px;
    color: var(--azul);
    font-size: 22px;
}

.login-caja p {
    margin: 0 0 22px;
    color: var(--gris-texto);
    font-size: 14px;
}

.botones {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.pie {
    background: var(--azul);
    color: #b8c4d4;
    text-align: center;
    padding: 16px;
    font-size: 13px;
}

.pie span {
    color: var(--amarillo);
}
```

---

## Paso 12 — Datos de ejemplo (opcional)

Crear `historial/management/commands/seed.py` (con las carpetas `management/` y `commands/`, cada una con `__init__.py` vacío):

```python
from django.core.management.base import BaseCommand

from alumnos.models import Alumno
from inventario.models import Herramienta


class Command(BaseCommand):
    help = 'Carga datos de ejemplo (alumnos y herramientas).'

    def handle(self, *args, **kwargs):
        alumnos = [
            ('Matías', 'Rojas', '3'),
            ('Camila', 'Fuentes', '3'),
            ('Benjamín', 'Soto', '3'),
            ('Javiera', 'Muñoz', '3'),
            ('Diego', 'Araya', '4'),
            ('Francisca', 'Castro', '4'),
            ('Ignacio', 'Vargas', '4'),
            ('Antonia', 'Silva', '4'),
        ]
        for nombre, apellido, curso in alumnos:
            Alumno.objects.get_or_create(
                nombre=nombre, apellido=apellido, curso=curso
            )

        herramientas = [
            ('Taladro percutor', 'Taladro eléctrico con percusión.', 3, 'Estante A1'),
            ('Llave inglesa', 'Llave ajustable 12 pulgadas.', 6, 'Estante A2'),
            ('Martillo', 'Martillo de carpintero.', 8, 'Estante A2'),
            ('Serrucho', 'Sierra manual para madera.', 4, 'Estante B1'),
            ('Caja de herramientas', 'Set completo básico.', 5, 'Estante B2'),
            ('Cinta métrica', 'Huíncha de 5 metros.', 10, 'Estante B2'),
        ]
        for nombre, descripcion, total, ubicacion in herramientas:
            Herramienta.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'cantidad_total': total,
                    'ubicacion': ubicacion,
                },
            )

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados.'))
```

---

## Paso 13 — Crear superusuario y cargar datos

```powershell
python manage.py createsuperuser
# pedirá usuario, email y contraseña

python manage.py seed   # opcional: datos de ejemplo
```

---

## Paso 14 — Probar

```powershell
python manage.py runserver
```

Abrir en el navegador:
- Login: http://127.0.0.1:8000/accounts/login/
- Panel: http://127.0.0.1:8000/
- Inventario: /inventario/
- Alumnos: /alumnos/
- Historial: /historial/
- Admin: /admin/

---

## Flujo de uso
1. Ingresar herramientas en Inventario (o `/admin/`).
2. Ingresar alumnos.
3. En Historial → "Nuevo préstamo": elegir alumno, herramienta y cantidad.
4. Si no hay stock, el sistema muestra el error.
5. Al devolver, botón "Devolver" en préstamos activos: marca fecha y libera stock.

## Notas
- `on_delete=PROTECT` impide borrar un alumno o herramienta con préstamos asociados.
- El stock se calcula con `disponibles`, no se guarda (evita datos duplicados).
- Sin dependencias extra: solo Django + SQLite + CSS propio.
