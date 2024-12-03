from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from facturacionService.models import ReciboCobro, ReciboPago


@csrf_exempt
def getRecibosCobro(request):
    recibos = ReciboCobro.objects.all()
    resultado = []
    for recibo in recibos:
        resultado.append({
            "id": str(recibo.id),
            "fecha": recibo.fecha,
            "monto" : recibo.nmonto,
            "detalle": recibo.detalle,
            "estudianteId": str(recibo.estudianteId),
            "detallesCobro": [str(detalle.id) for detalle in recibo.detalles_cobro]
        })
    return JsonResponse({"recibos_cobro": resultado})

@csrf_exempt
def getRecibosPago(request):
    recibos = ReciboPago.objects.all()
    resultado = []
    for recibo in recibos:
        resultado.append({
            "id": str(recibo.id),
            "fecha": recibo.fecha,
            "monto" : recibo.nmonto,
            "detalle": recibo.detalle,
            "reciboCobroId": str(recibo.recibo_cobro_id),
        })
    return JsonResponse({"recibos_pago": resultado})
