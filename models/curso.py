import sqlite3
import re
from database.connection import obtener_conexion


class Curso:

    # Mismo patron que exige el CHECK de database/setup.py
    FORMATO_CURSO = re.compile(r"^[0-9][A-Z][0-9][A-Z]$")

    def __init__(self, curso_id, curso):
        self.curso_id = curso_id
        self.curso = str(curso).strip().upper()

    def __str__(self):
        return self.curso

    def __repr__(self):
        return self.__str__()

    # -------------------------------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------------------------------

    def validar_datos(self):

        if not self.curso:
            raise ValueError("El nombre del curso no puede estar vacío.")

        if not self.FORMATO_CURSO.match(self.curso):
            raise ValueError(
                "El curso debe tener 4 caracteres con el formato "
                "1A1A (digito, letra, digito, letra)."
            )

        return True

    # -------------------------------------------------------------------------
    # CREATE
    # -------------------------------------------------------------------------

    def guardar(self):

        self.validar_datos()

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    INSERT INTO curso (curso)
                    VALUES (?)
                    """,
                    (self.curso,)
                )

                self.curso_id = cursor.lastrowid

                conexion.commit()

            return True

        except sqlite3.IntegrityError:
            raise ValueError("Ya existe un curso con ese nombre.")

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar curso: {e}")

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------

    @classmethod
    def obtener_por_id(cls, curso_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT curso_id, curso
                    FROM curso
                    WHERE curso_id = ?
                    """,
                    (curso_id,)
                )

                fila = cursor.fetchone()

                if fila:
                    return cls(*fila)

                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al buscar curso: {e}")

    @classmethod
    def obtener_todos(cls):
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute("SELECT curso_id, curso FROM curso")

                return [cls(*fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener cursos: {e}")

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------

    @classmethod
    def eliminar(cls, curso_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    DELETE FROM curso
                    WHERE curso_id = ?
                    """,
                    (curso_id,)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al eliminar curso: {e}")