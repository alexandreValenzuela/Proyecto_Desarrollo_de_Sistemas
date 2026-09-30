import sqlite3
import re
from database.connection import obtener_conexion


class Curso:

    # Mismo patron que exige el CHECK de database/setup.py:
    # N<nivel>G<grupo>, por ejemplo "N1G1".
    FORMATO_CURSO = re.compile(r"^[A-Z][0-9][A-Z][0-9]$")

    # Regla de negocio: el nivel 1 tiene 6 grupos, los niveles 2 a 6 tienen
    # 4 cada uno. El CHECK de la base solo valida la forma (N1G1), asi que
    # el rango real se controla aca.
    NIVEL_MINIMO = 1
    NIVEL_MAXIMO = 6
    GRUPOS_POR_NIVEL = {1: 6}
    GRUPOS_POR_DEFECTO = 4

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
                "N1G1 (letra, digito, letra, digito), donde N es el "
                "nivel y G el grupo."
            )

        nivel = int(self.curso[1])
        grupo = int(self.curso[3])

        if not self.NIVEL_MINIMO <= nivel <= self.NIVEL_MAXIMO:
            raise ValueError(
                f"El nivel debe estar entre {self.NIVEL_MINIMO} y "
                f"{self.NIVEL_MAXIMO}. {self.curso} tiene nivel {nivel}."
            )

        maximo_grupos = self.GRUPOS_POR_NIVEL.get(
            nivel, self.GRUPOS_POR_DEFECTO
        )

        if not 1 <= grupo <= maximo_grupos:
            raise ValueError(
                f"El nivel {nivel} tiene {maximo_grupos} grupo(s). "
                f"{self.curso} pide el grupo {grupo}."
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