from django.urls import path

from . import views

urlpatterns = [
    path('', views.PrestamoListView.as_view(), name='prestamo_lista'),
    path('nuevo/', views.PrestamoCreateView.as_view(), name='prestamo_nuevo'),
    path('<int:pk>/devolver/', views.devolver_prestamo, name='prestamo_devolver'),
]
