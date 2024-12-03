from django.urls import path
from . import views

urlpatterns = [
    path('facturacion/listar-recibos-cobro/', views.getRecibosCobro, name='listar_recibos_cobro'),
    path('facturacion/listar-recibos-pago/', views.getRecibosPago, name='listar_recibos_pago'),
    ]