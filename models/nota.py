import sqlite3
from database.connection import obtener_conexion


class Nota:

    """
    Una nota pertenece a un alumno y a una materia.

    No puede haber dos notas de la misma materia para el mismo alumno
    (UNIQUE en el esquema). Para reemplazar una nota existente, usar
    actualizar() sobre la nota ya cargada, no guardar() de nuevo.
    """

    # El CHECK de database/setup.py exige un entero en este rango.
    NOTA_MINIMA = 1
    NOTA_MAXIMA = 10

    def __init__(self, dni, materia, nota, comentario=None, nota_id=None):
        self.nota_id = nota_id
        self.dni = int(dni)
        self.materia = str(materia).strip()
        self.nota = int(nota)
        self.comentario = str(comentario).strip() if comentario else None

    @classmethod
    def _desde_fila(cls, fila):
        """
        Construye una Nota desde una fila de consulta.

        Los SELECT devuelven las columnas en orden alfabetico
        (nota_id, comentario, dni, materia, nota), que no es el orden del
        constructor. Centralizarlo aca evita repetir el mapeo.
        """
        nota_id, comentario, dni, materia, nota = fila

        return cls(
            dni=dni,
            materia=materia,
            nota=nota,
            comentario=comentario,
            nota_id=nota_id
        )

    def __str__(self):
        return f"{self.materia}: {self.nota}"

    def __repr__(self):
        return self.__str__()

    # -------------------------------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------------------------------

    def validar_datos(self):

        if not self.materia:
            raise ValueError("La materia no puede estar vacía.")

        if len(self.materia) > 255:
            raise ValueError("La materia no puede superar los 255 caracteres.")

        if not self.NOTA_MINIMA <= self.nota <= self.NOTA_MAXIMA:
            raise ValueError(
                f"La nota debe estar entre {self.NOTA_MINIMA} "
                f"y {self.NOTA_MAXIMA}."
            )

        if self.comentario and len(self.comentario) > 255:
            raise ValueError("El comentario no puede superar los 255 caracteres.")

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
                    INSERT INTO notas (dni, nota, materia, comentario)
                    VALUES (?, ?, ?, ?)
                    """,
                    (self.dni, self.nota, self.materia, self.comentario)
                )

                self.nota_id = cursor.lastrowid

                conexion.commit()

            return True

        except sqlite3.IntegrityError as e:
            # UNIQUE(dni, materia) o FK a alumnos.
            if "UNIQUE" in str(e).upper() or "unique" in str(e):
                raise ValueError(
                    f"Este alumno ya tiene una nota de {self.materia}."
                )

            if "FOREIGN KEY" in str(e).upper() or "foreign key" in str(e):
                raise ValueError(
                    "El alumno indicado no existe o no está cargado."
                )

            raise ValueError(f"No se pudo guardar la nota: {e}")

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar nota: {e}")

    def actualizar(self):

        self.validar_datos()

        if self.nota_id is None:
            raise ValueError("La nota no tiene identificador para actualizar.")

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    UPDATE notas
                    SET dni = ?, nota = ?, materia = ?, comentario = ?
                    WHERE nota_id = ?
                    """,
                    (self.dni, self.nota, self.materia, self.comentario,
                     self.nota_id)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.IntegrityError as e:
            raise ValueError(f"No se pudo actualizar la nota: {e}")

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al actualizar nota: {e}")

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------

    @classmethod
    def obtener_por_id(cls, nota_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nota_id, comentario, dni, materia, nota
                    FROM notas
                    WHERE nota_id = ?
                    """,
                    (nota_id,)
                )

                fila = cursor.fetchone()

                if fila:
                    return cls._desde_fila(fila)

                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al buscar nota: {e}")

    @classmethod
    def obtener_por_alumno(cls, dni):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nota_id, comentario, dni, materia, nota
                    FROM notas
                    WHERE dni = ?
                    ORDER BY materia
                    """,
                    (int(dni),)
                )

                return [cls._desde_fila(fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener notas del alumno: {e}")

    @classmethod
    def obtener_todas(cls):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nota_id, comentario, dni, materia, nota
                    FROM notas
                    ORDER BY dni, materia
                    """
                )

                return [cls._desde_fila(fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener notas: {e}")

    @classmethod
    def obtener_materias(cls):

        """Lista las materias distintas que tienen notas cargadas."""

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT DISTINCT materia
                    FROM notas
                    ORDER BY materia
                    """
                )

                return [fila[0] for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener materias: {e}")

    @classmethod
    def existe(cls, dni, materia):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT nota_id
                    FROM notas
                    WHERE dni = ? AND materia = ?
                    """,
                    (int(dni), str(materia).strip())
                )

                return cursor.fetchone() is not None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al verificar nota: {e}")

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------

    @classmethod
    def eliminar(cls, nota_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    DELETE FROM notas
                    WHERE nota_id = ?
                    """,
                    (nota_id,)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al eliminar nota: {e}")

    @classmethod
    def eliminar_por_alumno(cls, dni):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    DELETE FROM notas
                    WHERE dni = ?
                    """,
                    (int(dni),)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al eliminar notas del alumno: {e}")
