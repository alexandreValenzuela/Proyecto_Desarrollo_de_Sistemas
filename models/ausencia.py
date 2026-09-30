import sqlite3
import re
from datetime import date

from database.connection import obtener_conexion


class Ausencia:

    """
    Registro de que un alumno falto un dia, y si fue justificada.

    Una ausencia por alumno y por dia (UNIQUE en el esquema). Para cambiar
    si fue justificada, usar actualizar() sobre la ausencia ya cargada,
    no guardar() de nuevo.
    """

    FORMATO_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def __init__(self, dni, fecha, justificada, ausencia_id=None):
        self.ausencia_id = ausencia_id
        self.dni = int(dni)
        self.fecha = self._normalizar_fecha(fecha)
        self.justificada = bool(justificada)

    def __str__(self):
        estado = "justificada" if self.justificada else "no justificada"
        return f"{self.fecha}: {estado}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _normalizar_fecha(fecha):
        """Acepta un string YYYY-MM-DD y lo valida como fecha real."""
        texto = str(fecha).strip()

        if not Ausencia.FORMATO_FECHA.match(texto):
            raise ValueError(
                "La fecha debe tener el formato AAAA-MM-DD."
            )

        try:
            date.fromisoformat(texto)
        except ValueError:
            raise ValueError(f"La fecha '{texto}' no existe en el calendario.")

        return texto

    @classmethod
    def _desde_fila(cls, fila):
        """Construye una Ausencia desde una fila de consulta."""
        ausencia_id, dni, fecha, justificada = fila

        return cls(
            dni=dni,
            fecha=fecha,
            justificada=justificada,
            ausencia_id=ausencia_id
        )

    # -------------------------------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------------------------------

    def validar_datos(self):

        if not self.fecha:
            raise ValueError("La fecha de la ausencia no puede estar vacía.")

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
                    INSERT INTO ausencias (dni, fecha, justificada)
                    VALUES (?, ?, ?)
                    """,
                    (self.dni, self.fecha, 1 if self.justificada else 0)
                )

                self.ausencia_id = cursor.lastrowid

                conexion.commit()

            return True

        except sqlite3.IntegrityError as e:
            mensaje = str(e).upper()

            if "UNIQUE" in mensaje:
                raise ValueError(
                    f"Este alumno ya tiene registrada una ausencia "
                    f"para el {self.fecha}."
                )

            if "FOREIGN KEY" in mensaje:
                raise ValueError(
                    "El alumno indicado no existe o no está cargado."
                )

            raise ValueError(f"No se pudo guardar la ausencia: {e}")

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al guardar ausencia: {e}")

    def actualizar(self):

        self.validar_datos()

        if self.ausencia_id is None:
            raise ValueError("La ausencia no tiene identificador para actualizar.")

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    UPDATE ausencias
                    SET dni = ?, fecha = ?, justificada = ?
                    WHERE ausencia_id = ?
                    """,
                    (self.dni, self.fecha,
                     1 if self.justificada else 0, self.ausencia_id)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.IntegrityError as e:
            raise ValueError(f"No se pudo actualizar la ausencia: {e}")

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al actualizar ausencia: {e}")

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------

    @classmethod
    def obtener_por_id(cls, ausencia_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT ausencia_id, dni, fecha, justificada
                    FROM ausencias
                    WHERE ausencia_id = ?
                    """,
                    (ausencia_id,)
                )

                fila = cursor.fetchone()

                if fila:
                    return cls._desde_fila(fila)

                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al buscar ausencia: {e}")

    @classmethod
    def obtener_por_alumno(cls, dni, desde=None, hasta=None):

        """
        Lista las ausencias de un alumno, opcionalmente en un rango de fechas.
        """
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                consulta = (
                    "SELECT ausencia_id, dni, fecha, justificada "
                    "FROM ausencias WHERE dni = ?"
                )
                parametros = [int(dni)]

                if desde:
                    consulta += " AND fecha >= ?"
                    parametros.append(str(desde).strip())

                if hasta:
                    consulta += " AND fecha <= ?"
                    parametros.append(str(hasta).strip())

                consulta += " ORDER BY fecha DESC"

                cursor.execute(consulta, tuple(parametros))

                return [cls._desde_fila(fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener ausencias del alumno: {e}")

    @classmethod
    def obtener_todas(cls, solo_justificadas=False):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                consulta = (
                    "SELECT ausencia_id, dni, fecha, justificada "
                    "FROM ausencias"
                )

                if solo_justificadas:
                    consulta += " WHERE justificada = 1"

                consulta += " ORDER BY fecha DESC, dni"

                cursor.execute(consulta)

                return [cls._desde_fila(fila) for fila in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener ausencias: {e}")

    @classmethod
    def existe(cls, dni, fecha):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    "SELECT ausencia_id FROM ausencias WHERE dni = ? AND fecha = ?",
                    (int(dni), str(fecha).strip())
                )

                return cursor.fetchone() is not None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al verificar ausencia: {e}")

    @classmethod
    def contar_por_alumno(cls, dni, solo_justificadas=False):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                consulta = "SELECT COUNT(*) FROM ausencias WHERE dni = ?"
                parametros = [int(dni)]

                if solo_justificadas:
                    consulta += " AND justificada = 1"

                cursor.execute(consulta, tuple(parametros))

                return cursor.fetchone()[0]

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al contar ausencias: {e}")

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------

    @classmethod
    def eliminar(cls, ausencia_id):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    "DELETE FROM ausencias WHERE ausencia_id = ?",
                    (ausencia_id,)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al eliminar ausencia: {e}")

    @classmethod
    def eliminar_por_alumno(cls, dni):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    "DELETE FROM ausencias WHERE dni = ?",
                    (int(dni),)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al eliminar ausencias del alumno: {e}")
