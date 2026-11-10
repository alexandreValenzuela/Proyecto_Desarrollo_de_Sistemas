import sqlite3
import re

from database.connection import obtener_conexion


# Formato del curso: N<nivel>G<grupo>, por ejemplo "N1G1".
FORMATO_CURSO = re.compile(r"^N([1-6])G([1-6])$")


def nivel_de_curso(curso):
    """Devuelve el año (nivel) de un curso, entero de 1 a 6."""
    m = FORMATO_CURSO.match(str(curso).strip().upper())
    if not m:
        raise ValueError(f"Curso invalido: {curso}")
    return int(m.group(1))


def grupo_de_curso(curso):
    """Devuelve el grupo de un curso, entero de 1 a 6."""
    m = FORMATO_CURSO.match(str(curso).strip().upper())
    if not m:
        raise ValueError(f"Curso invalido: {curso}")
    return int(m.group(2))


def especialidad_de_curso(curso):
    """
    Devuelve la especialidad de un curso segun su grupo.

    G1 y G3 -> Computacion
    G2 y G4 -> Gestion y Administracion de las Organizaciones
    """
    grupo = grupo_de_curso(curso)
    if grupo in (1, 3):
        return "Computacion"
    if grupo in (2, 4):
        return "Gestion y Administracion de las Organizaciones"
    raise ValueError(f"Grupo sin especialidad definida: {curso}")


# Mapeo nivel -> (especialidad G1/G3, especialidad G2/G4) para armar los
# filtros de la vista.
ESPECIALIDADES = ("Computacion", "Gestion y Administracion de las Organizaciones")


class Materia:
    """Una materia pertenece a un curso y no tiene mas campos."""

    def __init__(self, nombre, curso_id, materia_id=None):
        self.materia_id = materia_id
        self.nombre = str(nombre).strip()
        self.curso_id = int(curso_id)

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return self.__str__()

    # -------------------------------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------------------------------

    def validar_datos(self):

        if not self.nombre:
            raise ValueError("El nombre de la materia no puede estar vacio.")

        if len(self.nombre) > 255:
            raise ValueError("El nombre de la materia no puede superar los 255 caracteres.")

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
                    INSERT INTO materia (nombre, curso_id)
                    VALUES (?, ?)
                    """,
                    (self.nombre, self.curso_id),
                )

                self.materia_id = cursor.lastrowid

                conexion.commit()

            return True

        except sqlite3.IntegrityError:
            raise ValueError("Ya existe una materia con ese nombre.")

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar materia: {e}")

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------

    @classmethod
    def obtener_por_id(cls, materia_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nombre, curso_id
                    FROM materia
                    WHERE materia_id = ?
                    """,
                    (materia_id,),
                )

                fila = cursor.fetchone()

                if fila:
                    return cls(fila[0], fila[1], materia_id=materia_id)

                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al buscar materia: {e}")

    @classmethod
    def obtener_todos(cls):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nombre, curso_id, materia_id
                    FROM materia
                    ORDER BY nombre
                    """
                )

                return [
                    cls(fila[0], fila[1], materia_id=fila[2])
                    for fila in cursor.fetchall()
                ]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener materias: {e}")

    @classmethod
    def obtener_por_filtro(cls, nivel=None, especialidad=None):
        """
        Lista materias filtradas por nivel (año) y/o especialidad.

        El filtro se aplica haciendo JOIN con la tabla curso y analizando el
        codigo NxGy. Si ambos filtros son None, devuelve todas las materias.
        """
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                query = """
                    SELECT m.nombre, m.curso_id, m.materia_id, c.curso
                    FROM materia m
                    JOIN curso c ON m.curso_id = c.curso_id
                    WHERE 1=1
                """
                params = []

                if nivel is not None:
                    query += " AND substr(c.curso, 2, 1) = ?"
                    params.append(str(nivel))

                if especialidad is not None:
                    if especialidad == "Computacion":
                        # G1 y G3 -> Computacion
                        query += " AND substr(c.curso, 4, 1) IN ('1', '3')"
                    else:
                        # G2 y G4 -> Gestion y Administracion de las Organizaciones
                        query += " AND substr(c.curso, 4, 1) IN ('2', '4')"

                query += " ORDER BY m.nombre"

                cursor.execute(query, params)

                return [
                    cls(fila[0], fila[1], materia_id=fila[2])
                    for fila in cursor.fetchall()
                ]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al filtrar materias: {e}")

    @classmethod
    def nombre_existe(cls, nombre):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT materia_id
                    FROM materia
                    WHERE nombre = ?
                    """,
                    (str(nombre).strip(),),
                )

                return cursor.fetchone() is not None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al verificar materia: {e}")

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------

    @classmethod
    def eliminar(cls, materia_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    DELETE FROM materia
                    WHERE materia_id = ?
                    """,
                    (materia_id,),
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al eliminar materia: {e}")
