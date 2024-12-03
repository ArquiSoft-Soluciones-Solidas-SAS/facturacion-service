from django.db import models

class ReciboCobro(models.Model):
    fecha = models.DateField()
    nmonto = models.DecimalField(max_digits=12, decimal_places=2)
    detalle = models.TextField()
    estudianteId = models.CharField(max_length=150)
    detalles_cobro = models.JSONField()

    def calcular_monto_total(self):
        return sum(detalle.valor for detalle in self.detalles_cobro.all())

    def __str__(self):
        return f"Recibo {self.id} - {self.nmonto}"

class ReciboPago(models.Model):
    recibo_cobro = models.OneToOneField(ReciboCobro, on_delete=models.CASCADE, null=True)
    fecha = models.DateField()
    nmonto = models.DecimalField(max_digits=10, decimal_places=2)
    detalle = models.TextField()

    def __str__(self):
        return f"Recibo Pago {self.id} - {self.nmonto}"
