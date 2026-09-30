"""
Seed de alumnos demo: 5 alumnos con notas, ausencias e intentos de acceso.

Es idempotente y NO pisa datos existentes:
- Un alumno por DNI que ya existe no se toca.
- Notas, ausencias y accesos solo se insertan si el alumno no tiene ninguno.

Los datos estan armados para poder probar las features sin inventar nada:
- Cada alumno tiene notas DISTINTAS: los promedios dan distintos y se puede
  ver el boletin (promedio por materia y general) de cada uno.
- Sofia Gonzalez (45000001) tiene 6 faltas sin justificar: dispara la
  alerta de la vista "Cargar / Ver Ausencias" (limite 5).
- Lautaro Lopez (45000004) no tiene ausencias: se ve el caso "sin faltas".
- Camila Martinez (45000005) queda SIN autorizar: aparece en "Pendientes de
  autorizar" del dashboard y se puede probar el flujo de autorizacion.
- Cada alumno tiene 1 acceso exitoso y 1 fallido: la vista "Historial de
  Accesos" tiene datos para mostrar.

Los alumnos demo loguean con contrasena "demo123" (se hashea en guardar()).
Camila (45000005) no puede loguearse hasta que un preceptor o profesor la
autorice.

Correr desde la raiz del repo:
    python database/seed_alumnos_demo.py
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
from models.acceso import Acceso


CONTRASENA_DEMO = "demo123"

ALUMNOS = [
    {
        "dni": "45000001", "nombre": "Sofia", "apellido": "Gonzalez",
        "direccion": "Av. Principal 123", "telefono": "11110001",
        "fecha_nacimiento": "2011-03-14", "curso": "N1G1", "autorizado": 1,
    },
    {
        "dni": "45000002", "nombre": "Mateo", "apellido": "Rodriguez",
        "direccion": "Calle Belgrano 456", "telefono": "11110002",
        "fecha_nacimiento": "2011-07-22", "curso": "N1G2", "autorizado": 1,
    },
    {
        "dni": "45000003", "nombre": "Valentina", "apellido": "Fernandez",
        "direccion": "San Martin 789", "telefono": "11110003",
        "fecha_nacimiento": "2010-11-05", "curso": "N2G1", "autorizado": 1,
    },
    {
        "dni": "45000004", "nombre": "Lautaro", "apellido": "Lopez",
        "direccion": "Rivadavia 321", "telefono": "11110004",
        "fecha_nacimiento": "2010-02-18", "curso": "N2G2", "autorizado": 1,
    },
    {
        "dni": "45000005", "nombre": "Camila", "apellido": "Martinez",
        "direccion": "Colon 654", "telefono": "11110005",
        "fecha_nacimiento": "2009-09-30", "curso": "N3G1", "autorizado": 0,
    },
]

# Notas por alumno: (materia, nota, comentario). Cada uno con valores
# distintos, asi los promedios no se repiten.
NOTAS = {
    "45000001": [
        ("Matematica", 7, "Regular."),
        ("Lengua", 8, "Buen desempeño."),
        ("Ingles", 9, "Muy buen nivel."),
    ],
    "45000002": [
        ("Matematica", 4, "Necesita refuerzo."),
        ("Lengua", 5, "Mejoró este trimestre."),
        ("Ingles", 6, "Aceptable."),
    ],
    "45000003": [
        ("Matematica", 10, "Excelente."),
        ("Lengua", 9, "Muy bien."),
        ("Ingles", 8, "Bien."),
    ],
    "45000004": [
        ("Matematica", 6, "Correcto."),
        ("Lengua", 6, "Correcto."),
        ("Ingles", 7, "Bien."),
        # Materia que solo tiene este alumno: el combo de filtro por materia
        # muestra un caso con un solo resultado.
        ("Historia", 8, "Buen manejo de fuentes."),
    ],
    "45000005": [
        ("Matematica", 8, "Bien."),
        ("Lengua", 7, "Bien."),
        ("Ingles", 8, "Muy bien."),
    ],
}

# Ausencias por alumno: (fecha, justificada). 0 = sin justificar, 1 = justificada.
# La UNIQUE es (dni, fecha): dos faltas el mismo dia no pueden repetirse.
AUSENCIAS = {
    # 6 sin justificar -> ALERTA en la vista de ausencias (limite 5).
    "45000001": [
        ("2026-08-03", 0),
        ("2026-08-05", 0),
        ("2026-08-10", 0),
        ("2026-08-12", 0),
        ("2026-08-17", 0),
        ("2026-08-19", 0),
        ("2026-08-24", 1),
    ],
    # Pocas faltas: estado OK.
    "45000002": [
        ("2026-08-11", 0),
        ("2026-08-18", 0),
        ("2026-08-25", 1),
    ],
    "45000003": [
        ("2026-08-26", 0),
        ("2026-09-02", 1),
        ("2026-09-16", 1),
    ],
    # Sin ausencias: no se inserta nada para este DNI.
    "45000004": [],
    "45000005": [
        ("2026-09-01", 1),
        ("2026-09-08", 1),
        ("2026-09-15", 1),
    ],
}


def _id_curso(nombre_curso):
    for curso in Curso.obtener_todos():
        if curso.curso == nombre_curso:
            return curso.curso_id
    return None


def sembrar_alumnos_demo():
    """Inserta (si no existen) alumnos, sus notas, ausencias y accesos."""
    creados = 0
    notas_creadas = 0
    ausencias_creadas = 0
    accesos_creados = 0

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
                autorizado=datos["autorizado"],
            )
            alumno.guardar()
            creados += 1

        if not Nota.obtener_por_alumno(dni):
            for materia, valor, comentario in NOTAS.get(dni, []):
                Nota(dni, materia, valor, comentario).guardar()
                notas_creadas += 1

        if not Ausencia.obtener_por_alumno(dni):
            for fecha, justificada in AUSENCIAS.get(dni, []):
                Ausencia(dni, fecha, justificada).guardar()
                ausencias_creadas += 1

        # Un acceso exitoso y uno fallido: la vista "Historial de Accesos"
        # tiene que tener con que mostrar. Solo si el alumno no tiene ninguno,
        # para que re-correr el seed no duplique filas.
        if not Acceso.historial_por_dni(dni):
            Acceso.registrar(dni, exitoso=True)
            Acceso.registrar(dni, exitoso=False)
            accesos_creados += 2

    print(f"Alumnos creados: {creados}.")
    print(f"Notas cargadas: {notas_creadas}.")
    print(f"Ausencias cargadas: {ausencias_creadas}.")
    print(f"Accesos registrados: {accesos_creados}.")
    print(f"Contrasena de los alumnos demo: {CONTRASENA_DEMO}")


if __name__ == "__main__":
    sembrar_alumnos_demo()
