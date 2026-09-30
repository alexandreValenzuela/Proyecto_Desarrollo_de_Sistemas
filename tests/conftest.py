"""
Configuracion compartida de la suite de tests de NeoED.

Aislamiento total: los tests corren contra una base SQLite temporal creada
por el propio pytest, jamas contra database/app_abm.db. Para que eso
funcione, NEOED_DB_PATH se define ANTES de importar database.connection
(que resuelve la ruta al importarse). QT_QPA_PLATFORM=offscreen permite
construir las vistas Qt sin pantalla.

El esquema se arma con la misma secuencia que la app real: setup.inicio()
-> migraciones() -> seed.cargar_datos_iniciales().
"""
import os
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="neoed_tests_")
os.environ["NEOED_DB_PATH"] = os.path.join(_TMP_DIR, "test.db")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sqlite3

import pytest

from database.connection import obtener_conexion, RUTA_BBDD, CARPETA_DATABASE

# Guardia: los tests BORRAN filas (el fixture bd_limpia vacia las tablas). Si
# por lo que sea la base real quedara apuntada, la suite la destruiria. Se
# aborta en el import, antes de ejecutar un solo test.
_RUTA_REAL = os.path.join(CARPETA_DATABASE, "app_abm.db")

if os.path.normcase(os.path.abspath(RUTA_BBDD)) == os.path.normcase(_RUTA_REAL):
    raise RuntimeError(
        f"La suite de tests apunta a la base real ({RUTA_BBDD}). "
        "Abortando para no destruir los datos."
    )
from database.setup import inicio
from database.migraciones import migraciones
from database.seed import cargar_datos_iniciales
from auth.passwords import hashear

DNI_ADMIN = 11111111
DNI_PROFESOR = 22222222
DNI_PRECEPTOR = 33333333

USUARIOS = {
    "admin": {
        "dni": DNI_ADMIN, "nombre": "Matt", "apellido": "Administrador",
        "cargo": "Administrador", "nivel_permisos": 10, "tipo": "personal",
    },
    "profesor": {
        "dni": DNI_PROFESOR, "nombre": "Kira", "apellido": "Administrador",
        "cargo": "Profesor", "nivel_permisos": 5, "tipo": "personal",
    },
    "preceptor": {
        "dni": DNI_PRECEPTOR, "nombre": "Ariadna", "apellido": "Administrador",
        "cargo": "Preceptor", "nivel_permisos": 3, "tipo": "personal",
    },
}


@pytest.fixture(scope="session", autouse=True)
def _esquema_creado():
    """Crea el esquema y los datos base una sola vez por sesion."""
    inicio()
    migraciones()
    yield


@pytest.fixture(autouse=True)
def bd_limpia(_esquema_creado):
    """
    Deja el estado de la base listo para cada test: conserva los cargos y
    los 26 cursos, y borra alumnos, notas, ausencias, accesos y personal.
    Luego recarga el personal base (INSERT OR IGNORE) desde el seed.
    """
    with obtener_conexion() as conexion:
        for tabla in ("accesos", "ausencias", "notas", "personal", "alumnos"):
            conexion.execute(f"DELETE FROM {tabla}")

    cargar_datos_iniciales()
    yield


@pytest.fixture
def crear_alumno(bd_limpia):
    """Crea un alumno autorizado en el curso indicado y devuelve su dict de
    usuario, como el que devuelve el login."""
    def _crear(dni=45000001, nombre="Ana", apellido="Gomez",
               password="demo123", autorizado=1, curso_id=None):
        from models.alumno import Alumno

        with obtener_conexion() as conexion:
            if curso_id is None:
                curso_id = conexion.execute(
                    "SELECT curso_id FROM curso ORDER BY curso_id LIMIT 1"
                ).fetchone()[0]

        alumno = Alumno(
            dni=dni,
            nombre=nombre,
            apellido=apellido,
            direccion="Direccion 123",
            fecha_nacimiento="2010-05-05",
            telefono="1122334455",
            password=password,
            curso_id=curso_id,
            autorizado=autorizado,
        )
        alumno.guardar()

        return {
            "dni": dni, "nombre": nombre, "apellido": apellido,
            "cargo": "Alumno", "nivel_permisos": 0, "tipo": "alumno",
        }
    return _crear


@pytest.fixture
def crear_personal(bd_limpia):
    """Inserta un miembro del personal con un cargo existente."""
    def _crear(dni=44444444, nombre="Doc", apellido="Nuevo", cargo_id=1,
               password="clave123"):
        with obtener_conexion() as conexion:
            conexion.execute(
                """
                INSERT INTO personal
                    (dni, nombre, apellido, direccion, telefono, cargo_id,
                     password, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (dni, nombre, apellido, "Direccion 999", "1155550000",
                 cargo_id, "", hashear(password)),
            )
        return dni
    return _crear


@pytest.fixture
def usuarios():
    return {clave: dict(datos) for clave, datos in USUARIOS.items()}


@pytest.fixture
def sin_modales(monkeypatch):
    """
    Los modales de alerta bloquean en offscreen: se sustituyen por no-ops.

    Las vistas hacen "from gui.componentes import alerta_error", asi que la
    sustitucion tiene que aplicarse en cada modulo que ya la importo, no solo
    en gui.componentes.
    """
    import sys

    import gui.componentes as componentes

    alertas = []

    def _error(*args, **kwargs):
        alertas.append(("error", args[1] if len(args) > 1 else ""))

    def _exito(*args, **kwargs):
        alertas.append(("exito", args[1] if len(args) > 1 else ""))

    modulos = [componentes] + [
        modulo for modulo in list(sys.modules.values())
        if modulo is not None and hasattr(modulo, "alerta_error")
    ]

    for modulo in modulos:
        if hasattr(modulo, "alerta_error"):
            monkeypatch.setattr(modulo, "alerta_error", _error)
        if hasattr(modulo, "alerta_exito"):
            monkeypatch.setattr(modulo, "alerta_exito", _exito)

    return alertas


@pytest.fixture
def qapp():
    """QApplication unica para toda la sesion de tests GUI."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
