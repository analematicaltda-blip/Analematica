from django.urls import path
from .iva import ReporteIVAView

urlpatterns = [
    path('iva/', ReporteIVAView.as_view(), name='reporte-iva'),
]
