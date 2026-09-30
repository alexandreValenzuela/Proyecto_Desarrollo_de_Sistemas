import sqlite3
from database.connection import obtener_conexion
from auth.permisos import PermisoDenegadoError
from auth.passwords import hashear, verificar

class Personal:
    def __init__(
        self,
        dni,
        nombre,
        apellido,
        direccion,
        telefono,
        cargo_id,
        password
    ):

        try:
            self.dni = int(dni)

        except (ValueError, TypeError):
            raise ValueError("El DNI debe contener solamente números.")

        self.nombre = str(nombre).strip()
        self.apellido = str(apellido).strip()
        self.direccion = str(direccion).strip()
        self.telefono = str(telefono).strip()
        self.cargo_id = cargo_id
        self.password = str(password).strip()


    def __str__(self):
        return f"{self.nombre} {self.apellido} - DNI: {self.dni}"


    def __repr__(self):
        return self.__str__()

    # -------------------------------------------------------------------------
    # VALIDACIONES
    # -------------------------------------------------------------------------

    def _validar_telefono(self):

        if not self.telefono.isdigit():
            raise ValueError("El teléfono solo puede contener números.")

        if len(self.telefono) < 8 or len(self.telefono) > 15:
            raise ValueError("El teléfono debe tener entre 8 y 15 dígitos.")

    def validar_datos(self):

        if not self.nombre:
            raise ValueError("El nombre no puede estar vacío.")

        if not self.apellido:
            raise ValueError("El apellido no puede estar vacío.")

        if not self.direccion:
            raise ValueError("La dirección no puede estar vacía.")

        if self.dni <= 0:
            raise ValueError("El DNI debe ser positivo.")

        self._validar_telefono()

        if not self.password:
            raise ValueError("La contraseña no puede estar vacía.")

        if self.cargo_id is None:
            raise ValueError("El personal debe tener un cargo asignado.")

        return True

    # -------------------------------------------------------------------------
    # LOGIN
    # -------------------------------------------------------------------------

    @classmethod
    def login(cls, dni, password):

        from models.acceso import Acceso

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT
                        personal.dni,
                        personal.nombre,
                        personal.apellido,
                        cargo.cargo,
                        cargo.nivel_permisos,
                        personal.password_hash

                    FROM personal
                    INNER JOIN cargo ON personal.cargo_id = cargo.cargo_id
                    WHERE personal.dni = ?
                    """,
                    (dni,)
                )

                usuario = cursor.fetchone()

                if usuario and verificar(password, usuario[5]):
                    Acceso.registrar(dni, exitoso=True)

                    return {
                        "dni": usuario[0],
                        "nombre": usuario[1],
                        "apellido": usuario[2],
                        "cargo": usuario[3],
                        "nivel_permisos": usuario[4]
                    }

                Acceso.registrar(dni, exitoso=False)
                return None

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al iniciar sesión: {e}")

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
                    INSERT INTO personal
                    (
                        dni,
                        nombre,
                        apellido,
                        direccion,
                        telefono,
                        cargo_id,
                        password,
                        password_hash
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

                    """,
                    (
                        self.dni,
                        self.nombre,
                        self.apellido,
                        self.direccion,
                        self.telefono,
                        self.cargo_id,
                        "",
                        hashear(self.password)
                    )
                )

                conexion.commit()

            return True

        except sqlite3.IntegrityError:

            raise ValueError("Ya existe un personal con ese DNI.")

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al guardar personal: {e}")

    # -------------------------------------------------------------------------
    # ASIGNAR CARGO
    # -------------------------------------------------------------------------

    @classmethod
    def asignar_cargo(cls, usuario_admin, dni_objetivo, nuevo_cargo_id):
        """Un usuario con nivel 10 le cambia el cargo a otro personal."""

        from models.cargo import Cargo

        if usuario_admin is None or usuario_admin.get("nivel_permisos", 0) < 10:
            raise PermisoDenegadoError(
                "Solo un administrador puede asignar cargos."
            )

        cargo_nuevo = Cargo.obtener_por_id(nuevo_cargo_id)

        if cargo_nuevo is None:
            raise ValueError("El cargo indicado no existe.")

        objetivo = cls.obtener_por_dni(dni_objetivo)

        if objetivo is None:
            raise ValueError("No existe personal con ese DNI.")

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute(
                    "UPDATE personal SET cargo_id = ? WHERE dni = ?",
                    (nuevo_cargo_id, dni_objetivo)
                )

                conexion.commit()
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise RuntimeError(f"Error al asignar cargo: {e}")
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
                        telefono,
                        cargo_id,
                        password

                    FROM personal

                    WHERE dni = ?

                    """,
                    (dni,)
                )

                fila = cursor.fetchone()

                if fila:

                    return cls(*fila)

                return None

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al buscar personal: {e}")

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
                        telefono,
                        cargo_id,
                        password

                    FROM personal
                    """
                )

                filas = cursor.fetchall()

                return [
                    cls(*fila)
                    for fila in filas
                ]

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al obtener personal: {e}")

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
                    UPDATE personal

                    SET

                        nombre = ?,

                        apellido = ?,

                        direccion = ?,

                        telefono = ?,

                        cargo_id = ?,

                        password = ?,

                        password_hash = ?

                    WHERE dni = ?

                    """,
                    (
                        self.nombre,
                        self.apellido,
                        self.direccion,
                        self.telefono,
                        self.cargo_id,
                        "",
                        hashear(self.password),
                        self.dni
                    )
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al actualizar personal: {e}")

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
                    DELETE FROM personal

                    WHERE dni = ?

                    """,
                    (dni,)
                )

                conexion.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as e:

            raise RuntimeError(f"Error al eliminar personal: {e}")