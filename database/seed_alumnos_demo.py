"""
Seed de alumnos demo: 5 alumnos con 3 notas cada uno y ausencias cargadas
para 3 de ellos.

Es idempotente y NO pisa datos existentes:
- Un alumno por DNI que ya existe no se toca.
- Notas y ausencias solo se insertan si el alumno no tiene ninguna.

Correr desde la raiz del repo:
    python database/seed_alumnos_demo.py

Los alumnos demo loguean con contrasena "demo123" (se hashea en guardar()).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database.setup
database.setup.inicio()
from database import migraciones
migraciones.migraciones()
from database.seed import cargar_datos_iniciales
cargar_datos_iniciales()

from models.alumno import Alumno
from models.curso import Curso
from models.nota import Nota
from models.ausencia import Ausencia


CONTRASENA_DEMO = "demo123"

ALUMNOS = [
    {
        "dni": "45000001", "nombre": "Sofia", "apellido": "Gonzalez",
        "direccion": "Av. Principal 123", "telefono": "11110001",
        "fecha_nacimiento": "2011-03-14", "curso": "N1G1",
    },
    {
        "dni": "45000002", "nombre": "Mateo", "apellido": "Rodriguez",
        "direccion": "Calle Belgrano 456", "telefono": "11110002",
        "fecha_nacimiento": "2011-07-22", "curso": "N1G2",
    },
    {
        "dni": "45000003", "nombre": "Valentina", "apellido": "Fernandez",
        "direccion": "San Martin 789", "telefono": "11110003",
        "fecha_nacimiento": "2010-11-05", "curso": "N2G1",
    },
    {
        "dni": "45000004", "nombre": "Lautaro", "apellido": "Lopez",
        "direccion": "Rivadavia 321", "telefono": "11110004",
        "fecha_nacimiento": "2010-02-18", "curso": "N2G2",
    },
    {
        "dni": "45000005", "nombre": "Camila", "apellido": "Martinez",
        "direccion": "Colon 654", "telefono": "11110005",
        "fecha_nacimiento": "2009-09-30", "curso": "N3G1",
    },
]

# 3 notas por alumno: misma materia en todos, nota distinta por alumno.
NOTAS = [
    ("Matematica", 7, "Regular."),
    ("Lengua", 8, "Buen desempeño."),
    ("Ingles", 9, "Muy buen nivel."),
]

# Ausencias: SOLO 3 de los 5 alumnos. Listas de (fecha, justificada).
AUSENCIAS = {
    "45000001": [
        ("2026-08-05", 0),
        ("2026-08-19", 1),
        ("2026-09-02", 0),
    ],
    "45000002": [
        ("2026-08-12", 1),
        ("2026-09-09", 0),
    ],
    "45000003": [
        ("2026-08-26", 0),
        ("2026-09-16", 1),
    ],
}


def _id_curso(nombre_curso):
    for curso in Curso.obtener_todos():
        if curso.curso == nombre_curso:
            return curso.curso_id
    return None


def sembrar_alumnos_demo():
    """Inserta (si no existen) alumnos, sus notas y las ausencias pedidas."""
    creados = 0
    notas_creadas = 0
    ausencias_creadas = 0

    for datos in ALUMNOS:
        dni = datos["dni"]

        if Alumno.obtener_por_dni(dni) is None:
            alumno = Alumno(
                dni=dni,
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                direccion=datos["direccion"],
                fecha_nacimiento=datos["fecha_nacimiento"],
                telefono=datos["telefono"],
                password=CONTRASENA_DEMO,
                curso_id=_id_curso(datos["curso"]),
                autorizado=1,
            )
            alumno.guardar()
            creados += 1

        if not Nota.obtener_por_alumno(dni):
            for materia, valor, comentario in NOTAS:
                Nota(dni, materia, valor, comentario).guardar()
                notas_creadas += 1

        if not Ausencia.obtener_por_alumno(dni):
            for fecha, justificada in AUSENCIAS.get(dni, []):
                Ausencia(dni, fecha, justificada).guardar()
                ausencias_creadas += 1

    print(f"Alumnos creados: {creados}.")
    print(f"Notas cargadas: {notas_creadas}.")
    print(f"Ausencias cargadas: {ausencias_creadas}.")


if __name__ == "__main__":
    sembrar_alumnos_demo()