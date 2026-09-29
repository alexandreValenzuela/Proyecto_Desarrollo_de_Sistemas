import sqlite3
from database.connection import obtener_conexion


class Curso:

    def __init__(self, curso_id, curso):
        self.curso_id = curso_id
        self.curso = str(curso).strip()

    def __str__(self):
        return self.curso

    def __repr__(self):
        return self.__str__()

    @classmethod
    def obtener_todos(cls):
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute("SELECT curso_id, curso FROM curso")

                return [cls(*fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener cursos: {e}")