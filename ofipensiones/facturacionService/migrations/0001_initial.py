# Generated by Django 5.1.3 on 2024-12-02 21:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReciboCobro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('nmonto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('detalle', models.TextField()),
                ('estudianteId', models.CharField(max_length=150)),
                ('detalles_cobro', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='ReciboPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('nmonto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('detalle', models.TextField()),
                ('recibo_cobro', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='facturacionService.recibocobro')),
            ],
        ),
    ]
