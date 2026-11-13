from django.urls import path

from . import views

urlpatterns = [
    path('', views.HerramientaListView.as_view(), name='herramienta_lista'),
    path('nueva/', views.HerramientaCreateView.as_view(), name='herramienta_nueva'),
    path('<int:pk>/editar/', views.HerramientaUpdateView.as_view(), name='herramienta_editar'),
    path('<int:pk>/eliminar/', views.HerramientaDeleteView.as_view(), name='herramienta_eliminar'),
]
