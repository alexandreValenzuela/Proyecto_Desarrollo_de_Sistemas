import sqlite3
from datetime import datetime
from auth.permisos import PermisoDenegadoError
from auth.passwords import hashear, verificar

from database.connection import obtener_conexion


class Alumno:

    def __init__(
        self,
        dni,
        nombre,
        apellido,
        direccion,
        fecha_nacimiento,
        telefono,
        password,
        telefono_respaldo=None,
        curso_id=None,
        autorizado=0
    ):

        try:
            self.dni = int(dni)

        except (ValueError, TypeError):
            raise ValueError(
                "El DNI debe contener solamente números."
            )

        self.nombre = str(nombre).strip()
        self.apellido = str(apellido).strip()
        self.direccion = str(direccion).strip()
        self.fecha_nacimiento = str(fecha_nacimiento).strip()
        self.telefono = str(telefono).strip()
        self.password = str(password).strip()
        self.autorizado = int(autorizado)

        if telefono_respaldo:
            self.telefono_respaldo = str(telefono_respaldo).strip()
        else:
            self.telefono_respaldo = None

        self.curso_id = curso_id


    def __str__(self):
        return f"{self.nombre} {self.apellido} - DNI: {self.dni}"


    def __repr__(self):
        return self.__str__()


    # -------------------------------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------------------------------

    def _validar_telefono(self, telefono, nombre_campo="teléfono"):

        if not telefono.isdigit():
            raise ValueError(f"El {nombre_campo} solo puede contener números.")

        if len(telefono) < 8 or len(telefono) > 15:
            raise ValueError(f"El {nombre_campo} debe tener entre 8 y 15 dígitos.")

    def validar_datos(self):

        if not self.nombre:
            raise ValueError("El nombre no puede estar vacío.")

        if not self.apellido:
            raise ValueError("El apellido no puede estar vacío.")

        if not self.direccion:
            raise ValueError("La dirección no puede estar vacía.")

        try:

            datetime.strptime(self.fecha_nacimiento,"%Y-%m-%d")

        except ValueError:

            raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")

        if self.dni <= 0:
            raise ValueError("El DNI debe ser un número positivo.")

        self._validar_telefono(self.telefono,"teléfono principal")

        if self.telefono_respaldo:

            self._validar_telefono(self.telefono_respaldo,"teléfono de respaldo")

        if self.curso_id is None:

            raise ValueError("El alumno debe tener un curso asignado.")

        if not self.password:
            raise ValueError("La contraseña no puede estar vacía.")
        
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
                    INSERT INTO alumnos
                    (
                        dni,
                        nombre,
                        apellido,
                        direccion,
                        fecha_nacimiento,
                        telefono,
                        telefono_respaldo,
                        curso_id,
                        password,
                        password_hash,
                        autorizado
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.dni,
                        self.nombre,
                        self.apellido,
                        self.direccion,
                        self.fecha_nacimiento,
                        self.telefono,
                        self.telefono_respaldo,
                        self.curso_id,
                        # La columna "password" queda vacia: el hash va aparte.
                        "",
                        hashear(self.password),
                        self.autorizado
                    )
                )

                conexion.commit()

            return True

        except sqlite3.IntegrityError:

            raise ValueError("Ya existe un alumno con ese DNI o el curso no existe.")

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al guardar alumno: {e}")

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------

    @classmethod
    def obtener_por_dni(cls, dni):

        try:

            with obtener_conexion() as conexion:

                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT
                        dni,
                        nombre,
                        apellido,
                        direccion,
                        fecha_nacimiento,
                        telefono,
                        password,
                        telefono_respaldo,
                        curso_id,
                        autorizado
                    FROM alumnos WHERE dni = ? """,(dni,)
                )

                fila = cursor.fetchone()
                if fila:
                    return cls(*fila)

                return None

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al buscar alumno: {e}")

    @classmethod
    def obtener_todos(cls):

        try:
            with obtener_conexion() as conexion:

                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT
                        dni,
                        nombre,
                        apellido,
                        direccion,
                        fecha_nacimiento,
                        telefono,
                        telefono_respaldo,
                        curso_id
                    FROM alumnos
                    """
                )


                filas = cursor.fetchall()


                return [
                    cls(*fila)
                    for fila in filas
                ]


        except sqlite3.Error as e:

            raise RuntimeError(f"Error al obtener alumnos: {e}")


    # -------------------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------------------

    def actualizar(self):

        self.validar_datos()


        try:

            with obtener_conexion() as conexion:

                cursor = conexion.cursor()


                cursor.execute(
                    """
                    UPDATE alumnos

                    SET
                        nombre = ?,
                        apellido = ?,
                        direccion = ?,
                        fecha_nacimiento = ?,
                        telefono = ?,
                        telefono_respaldo = ?,
                        curso_id = ?

                    WHERE dni = ?

                    """,
                    (
                        self.nombre,
                        self.apellido,
                        self.direccion,
                        self.fecha_nacimiento,
                        self.telefono,
                        self.telefono_respaldo,
                        self.curso_id,
                        self.dni
                    )
                )


                conexion.commit()


                return cursor.rowcount > 0


        except sqlite3.Error as e:

            raise RuntimeError(f"Error al actualizar alumno: {e}")

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------

    @classmethod
    def eliminar(cls, dni):

        try:

            with obtener_conexion() as conexion:

                cursor = conexion.cursor()


                cursor.execute(
                    """
                    DELETE FROM alumnos
                    WHERE dni = ?
                    """,
                    (dni,)
                )


                conexion.commit()


                return cursor.rowcount > 0


        except sqlite3.Error as e:

            raise RuntimeError(f"Error al eliminar alumno: {e}")

    # -------------------------------------------------------------------------
    # LOGIN
    # -------------------------------------------------------------------------

    @classmethod
    def login(cls, dni, password, registrar_acceso=True):

        """
        Autentica a un alumno.

        registrar_acceso=False evita que este intento quede registrado en
        la tabla accesos. Lo usa auth/autenticacion.py para probar contra
        ambas tablas y registrar un unico intento por login.
        """
        from models.acceso import Acceso

        def registrar(exitoso):
            if registrar_acceso:
                Acceso.registrar(dni, exitoso=exitoso)

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                # Se busca por DNI solamente. La contrasena se verifica
                # en Python contra el hash: no se puede filtrar en SQL.
                cursor.execute(
                    """
                    SELECT dni, nombre, apellido, autorizado, password_hash
                    FROM alumnos
                    WHERE dni = ?
                    """,
                    (dni,)
                )

                fila = cursor.fetchone()

                if not fila:
                    registrar(False)
                    return None

                dni_encontrado, nombre, apellido, autorizado, hash_almacenado = fila

                if not verificar(password, hash_almacenado):
                    registrar(False)
                    return None

                if not autorizado:
                    registrar(False)
                    raise PermisoDenegadoError(
                        "Tu registro todavía no fue autorizado por un "
                        "profesor o preceptor."
                    )

                registrar(True)

                return {
                    "dni": dni_encontrado,
                    "nombre": nombre,
                    "apellido": apellido,
                    "cargo": "Alumno",
                    "nivel_permisos": 0,
                    "tipo": "alumno"
                }

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al iniciar sesión: {e}")

    # -------------------------------------------------------------------------
    # BUSQUEDA FILTRADA (Vista Ver Alumnos)
    # -------------------------------------------------------------------------

    @staticmethod
    def buscar_filtrado(dni=None, nombre=None, id_curso=None):
        """
        Consulta filtrada con LEFT JOIN a cursos para la grilla de alumnos.
        Soporta busquedas parciales con LIKE.
        """
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                query = """
                    SELECT a.dni, a.nombre, a.apellido, c.curso, a.autorizado
                    FROM alumnos a
                    LEFT JOIN curso c ON a.curso_id = c.curso_id
                    WHERE 1=1
                """
                params = []

                if dni and dni.strip():
                    query += " AND a.dni LIKE ?"
                    params.append(f"%{dni.strip()}%")

                if nombre and nombre.strip():
                    query += " AND (a.nombre LIKE ? OR a.apellido LIKE ?)"
                    params.append(f"%{nombre.strip()}%")
                    params.append(f"%{nombre.strip()}%")

                if id_curso and str(id_curso).isdigit() and int(id_curso) > 0:
                    query += " AND a.curso_id = ?"
                    params.append(int(id_curso))

                query += " ORDER BY a.apellido, a.nombre ASC"

                cursor.execute(query, params)
                return cursor.fetchall()

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al buscar alumnos: {e}")

    # -------------------------------------------------------------------------
    # AUTORIZACION DE REGISTROS
    # -------------------------------------------------------------------------

    NIVEL_MINIMO_PARA_AUTORIZAR = 3  # Preceptor o superior. Subilo a 5 si querés que sea solo Profesor+.

    @classmethod
    def obtener_pendientes(cls):

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT dni, nombre, apellido
                    FROM alumnos
                    WHERE autorizado = 0
                    """
                )

                return cursor.fetchall()

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener alumnos pendientes: {e}")

    @classmethod
    def autorizar(cls, usuario_autorizante, dni_alumno):

        nivel = usuario_autorizante.get("nivel_permisos", 0) if usuario_autorizante else 0

        if nivel < cls.NIVEL_MINIMO_PARA_AUTORIZAR:
            raise PermisoDenegadoError(
                "No tenés permisos para autorizar alumnos."
            )

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    "UPDATE alumnos SET autorizado = 1 WHERE dni = ?",
                    (dni_alumno,)
                )

                conexion.commit()
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al autorizar alumno: {e}")