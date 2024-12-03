from collections import defaultdict
from decimal import Decimal

import factory
from django.contrib.auth.models import User
from django.db import transaction

from .models import ReciboPago, ReciboCobro
from django.utils import timezone
from django.conf import settings
import requests
import random
from datetime import date

# Enumeración de meses
MESES = [
    ("Enero", 1),
    ("Febrero", 2),
    ("Marzo", 3),
    ("Abril", 4),
    ("Mayo", 5),
    ("Junio", 6),
    ("Julio", 7),
    ("Agosto", 8),
    ("Septiembre", 9),
    ("Octubre", 10),
    ("Noviembre", 11),
    ("Diciembre", 12),
]


def obtener_estudiantes():
    r = requests.get(settings.PATH_ESTUDIANTES + "/listar-estudiantes/",
                     headers={"Accept": "application/json"})
    if r.status_code != 200:
        print("Error al obtener los estudiantes.")
        return []
    estudiantes = r.json()["estudiantes"]
    print("Estudiantes obtenidos exitosamente.")
    return estudiantes


def obtener_detalles_cobro():
    r = requests.get(settings.PATH_CRONOGRAMAS + f"/cronogramas-cursos/detalles/", headers={"Accept": "application/json"})
    if r.status_code != 200:
        print(
            f"Error al obtener los detalles de cobro.")
        return []
    detalles = r.json()["detalles"]
    print(
        f"Detalles de cobro obtenidos exitosamente del curso.")
    return detalles


def generar_recibos_cobro_hasta_actualidad():
    """
    Genera recibos de cobro para todos los estudiantes de las instituciones
    hasta el mes actual (octubre).
    """
    # Obtener la fecha actual
    fecha_actual = timezone.now().date()
    mes_actual = fecha_actual.month  # Obtener el mes actual

    # Obtener todos los estudiantes de todas las instituciones
    estudiantes = obtener_estudiantes()
    detalles_cobro_data = obtener_detalles_cobro()  # Lista de detalles de cobro


    # Iniciar una transacción
    for estudiante in estudiantes:
        # Recorrer cada mes en la enumeración
        for mes_nombre, mes_num in MESES:
            # Solo generar recibos hasta el mes actual
            if mes_num > mes_actual:
                break  # Salir del bucle si el mes es posterior al actual

            # Filtrar los detalles de cobro para ese mes y curso del estudiante
            detalles_cobro = [
                detalle for detalle in detalles_cobro_data
                if detalle["mes"] == mes_nombre and detalle["cursoId"] == estudiante["cursoEstudianteId"]
            ]
            print("detalles cobro del estudiante con id " + estudiante["id"] + " y mes " + mes_nombre + " encontrados, son de tamaño: " + str(len(detalles_cobro)))

            # Solo continuar si hay detalles de cobro para ese mes
            if not detalles_cobro:
                print(f"No hay detalles de cobro para el estudiante {estudiante['nombreEstudiante']} en el mes {mes_nombre}.")
                continue

            # Transformar los detalles a la estructura requerida
            detalles = []
            for detalle in detalles_cobro:
                detalles.append({
                    "id": str(detalle["id"]),
                    "mes": detalle["mes"],
                    "valor": str(detalle["valor"]),
                    "fechaCausacion": detalle["fechaCausacion"],
                    "fechaLimite": detalle["fechaLimite"],
                    "frecuencia": detalle.get("frecuencia", "N/A")
                })

            # Calcular el monto total de los detalles de cobro
            total_monto = sum(Decimal(detalle["valor"]) for detalle in detalles)
            total_monto = Decimal(total_monto).quantize(Decimal('0.01'))  # Redondea a 2 decimales

            if total_monto <= 0:  # Verificar que el monto total sea mayor que 0
                print(f"No se generará recibo para el estudiante {estudiante['nombreEstudiante']} para el mes {mes_nombre} debido a un monto total inválido.")
                continue

            # Crear un nuevo recibo de cobro
            try:
                recibo = ReciboCobro.objects.create(
                    fecha=fecha_actual,
                    nmonto=total_monto,
                    detalle=(
                        f"Recibo de cobro para el mes de {mes_nombre}, que le corresponde a {estudiante['nombreEstudiante']}, "
                        f"del curso con id {estudiante['cursoEstudianteId']}, "
                        f"de la institución {estudiante['nombreInstitucion']}."
                    ),
                    estudianteId=estudiante["id"],
                    detalles_cobro=detalles
                )
                print(f"Recibo {recibo.id} generado para el estudiante {estudiante['nombreEstudiante']} para el mes {mes_nombre}.")
            except Exception as e:
                print(f"Error al crear el recibo: {e}")




def generar_recibos_pago():
    """
    Genera recibos de pago para todos los estudiantes de todas las instituciones.
    """
    fecha_actual = date.today()

    # Obtener todos los cursos de todas las instituciones
    estudiantes = obtener_estudiantes()
    curso_count = defaultdict(list)
    for estudiante in estudiantes:
        curso_count[estudiante["cursoEstudianteId"]].append(estudiante)

    # Recorremos los cursos (identificados por cursoEstudianteId)
    for curso_id, estudiantes in curso_count.items():
        total_estudiantes = len(estudiantes)

        # Determinar el 70% que están al día y el 30% que no lo están
        if total_estudiantes == 0:
            continue  # Si no hay estudiantes en el curso, continuar con el siguiente

        num_al_dia = int(total_estudiantes * 0.7)
        estudiantes_al_dia = random.sample(estudiantes, num_al_dia)
        estudiantes_no_al_dia = [
            estudiante for estudiante in estudiantes if estudiante not in estudiantes_al_dia]

        with transaction.atomic():
            # Procesar estudiantes al día
            for estudiante in estudiantes_al_dia:
                # Obtener todos los recibos de cobro de este estudiante
                recibos_cobro = ReciboCobro.objects.filter(
                    estudianteId=estudiante["id"])

                for recibo_cobro in recibos_cobro:
                    # Crear el recibo de pago
                    ReciboPago.objects.create(
                        recibo_cobro=recibo_cobro,
                        fecha=fecha_actual,
                        nmonto=recibo_cobro.nmonto,
                        detalle=f"Pago total por el estudiante {estudiante['nombreEstudiante']}."
                    )
                    print(
                        f"Recibo de pago total generado para {estudiante['nombreEstudiante']}: {recibo_cobro.nmonto}")

            # Procesar estudiantes no al día
            for estudiante in estudiantes_no_al_dia:
                # Obtener todos los recibos de cobro del estudiante
                recibos_cobro = list(ReciboCobro.objects.filter(
                    estudianteId=estudiante["id"]).order_by('fecha'))

                # Determinar el número aleatorio de meses a pagar (1 a 6)
                meses_a_pagar = random.randint(1, 6)

                # Calcular el índice para seleccionar los recibos de cobro a pagar
                inicio = 0
                fin = meses_a_pagar

                # Asegurarse de que no exceda el número de recibos de cobro disponibles
                if fin > len(recibos_cobro):
                    fin = len(recibos_cobro)

                # Pagar recibos de cobro desde enero hasta el número aleatorio de meses
                for recibo_cobro in recibos_cobro[inicio:fin]:
                    # Crear el recibo de pago
                    ReciboPago.objects.create(
                        recibo_cobro=recibo_cobro,
                        fecha=fecha_actual,
                        nmonto=recibo_cobro.nmonto,
                        detalle=f"Pago de recibo cobro para {estudiante['nombreEstudiante']} desde enero hasta {fin}."
                    )
                    print(
                        f"Recibo de pago generado para {estudiante['nombreEstudiante']}: {recibo_cobro.nmonto}")
