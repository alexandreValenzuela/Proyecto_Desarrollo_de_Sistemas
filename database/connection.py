import os
import sqlite3

# Ruta absoluta basada en laubicacion de este archivo, no en el directorio
# desde el que se ejecute el programa.
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATABASE = os.path.join(CARPETA_BASE, "database")

# La variable de entorno NEOED_DB_PATH permite apuntar la base a otro archivo
# (lo usa la suite de tests para aislar las pruebas de los datos reales).
RUTA_BBDD = os.environ.get(
    "NEOED_DB_PATH",
    os.path.join(CARPETA_DATABASE, "app_abm.db"),
)


class Conexion:
    """
    Envoltura de sqlite3.Connection que cierra la conexion al salir del bloque
    with.

    El context manager nativo de sqlite3 hace commit o rollback, pero NO cierra
    la conexion, por lo que cada consulta dejaba una conexion abierta. Esta
    clase delega todo a la conexion real y agrega el cierre.

    Uso como contexto (recomendado):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(...)
            conexion.commit()

    Uso directo (aun soportado,Recorda cerrar manual):
        conexion = obtener_conexion()
        try:
            ...
        finally:
            conexion.close()
    """

    def __init__(self, ruta):
        self._conexion = sqlite3.connect(ruta)
        # El PRAGMA es por conexion: debe activarse en cada una.
        self._conexion.execute("PRAGMA foreign_keys = ON")

    def __enter__(self):
        return self

    def __exit__(self, tipo_exc, valor_exc, traceback):
        try:
            if tipo_exc is None:
                self._conexion.commit()
            else:
                self._conexion.rollback()
        finally:
            self._conexion.close()

        # No suprime la excepcion original.
        return False

    def close(self):
        self._conexion.close()

    def __getattr__(self, nombre):
        # Delega cursor(), commit(), execute(), rollback(), etc.
        return getattr(self._conexion, nombre)


def obtener_conexion():
    if not os.path.exists(CARPETA_DATABASE):
        os.makedirs(CARPETA_DATABASE)
        print('Se creó la carpeta database con éxito')

    return Conexion(RUTA_BBDD)
