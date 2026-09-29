import sqlite3
from datetime import datetime

from database.connection import obtener_conexion


class Acceso:

    @classmethod
    def registrar(cls, dni, exitoso):
        """Registra un intento de inicio de sesión (exitoso o no)."""

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    INSERT INTO accesos (dni, fecha_hora, exitoso)
                    VALUES (?, ?, ?)
                    """,
                    (
                        dni,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        1 if exitoso else 0
                    )
                )

                conexion.commit()

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al registrar acceso: {e}")

    @classmethod
    def historial_por_dni(cls, dni):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT acceso_id, dni, fecha_hora, exitoso
                    FROM accesos
                    WHERE dni = ?
                    ORDER BY fecha_hora DESC
                    """,
                    (dni,)
                )

                return cursor.fetchall()

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener historial de accesos: {e}")