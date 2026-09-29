import sqlite3
from database.connection import obtener_conexion


class Cargo:

    def __init__(self, cargo_id, cargo, nivel_permisos):
        self.cargo_id = cargo_id
        self.cargo = str(cargo).strip()
        self.nivel_permisos = int(nivel_permisos)

    def __str__(self):
        return f"{self.cargo} (nivel {self.nivel_permisos})"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def obtener_por_id(cls, cargo_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT cargo_id, cargo, nivel_permisos
                    FROM cargo
                    WHERE cargo_id = ?
                    """,
                    (cargo_id,)
                )

                fila = cursor.fetchone()

                if fila:
                    return cls(*fila)

                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al buscar cargo: {e}")

    @classmethod
    def obtener_todos(cls):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT cargo_id, cargo, nivel_permisos
                    FROM cargo
                    """
                )

                return [cls(*fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener cargos: {e}")