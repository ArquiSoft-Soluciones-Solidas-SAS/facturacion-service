from django.urls import path
from . import views

urlpatterns = [
    path('listar-recibos-cobro/', views.getRecibosCobro, name='listar_recibos_cobro'),
    path('listar-recibos-pago/', views.getRecibosPago, name='listar_recibos_pago'),
    ]