from django.urls import path

from . import views

urlpatterns = [
    path('', views.AlumnoListView.as_view(), name='alumno_lista'),
    path('nuevo/', views.AlumnoCreateView.as_view(), name='alumno_nuevo'),
    path('<int:pk>/editar/', views.AlumnoUpdateView.as_view(), name='alumno_editar'),
    path('<int:pk>/eliminar/', views.AlumnoDeleteView.as_view(), name='alumno_eliminar'),
]
