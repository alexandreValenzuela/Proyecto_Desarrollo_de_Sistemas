import sqlite3
from database.connection import obtener_conexion


def inicio():

    conexion = obtener_conexion()

    try:

        cursor = conexion.cursor()

        # ---------------------------------------------------------------------
        # CARGOS
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS cargo (
                cargo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cargo TEXT NOT NULL UNIQUE
                CHECK(length(cargo) <= 255),
                nivel_permisos INTEGER NOT NULL
            )
            '''
        )

        # ---------------------------------------------------------------------
        # CURSOS
        # Ejemplo válido: 1N2G
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS curso (
                curso_id INTEGER PRIMARY KEY AUTOINCREMENT,
                curso TEXT NOT NULL UNIQUE,
                CHECK(length(curso) = 4),
                CHECK(
                    curso GLOB '[0-9][A-Z][0-9][A-Z]'
                )
            )
            '''
        )

        # ---------------------------------------------------------------------
        # ALUMNOS
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS alumnos (
                dni INTEGER PRIMARY KEY,

                nombre TEXT NOT NULL
                CHECK(length(nombre) <= 255),

                apellido TEXT NOT NULL
                CHECK(length(apellido) <= 255),

                direccion TEXT NOT NULL
                CHECK(length(direccion) <= 255),

                fecha_nacimiento DATE NOT NULL,

                telefono TEXT NOT NULL
                CHECK(length(telefono) BETWEEN 8 AND 15),

                telefono_respaldo TEXT
                CHECK(
                    telefono_respaldo IS NULL
                    OR length(telefono_respaldo) BETWEEN 8 AND 15
                ),

                curso_id INTEGER NOT NULL,

                password TEXT NOT NULL,

                autorizado INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY(curso_id)
                REFERENCES curso(curso_id)
            )
            '''
        )

        # ---------------------------------------------------------------------
        # PERSONAL
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS personal (

                dni INTEGER PRIMARY KEY,

                nombre TEXT NOT NULL
                CHECK(length(nombre) <= 255),

                apellido TEXT NOT NULL
                CHECK(length(apellido) <= 255),

                direccion TEXT NOT NULL
                CHECK(length(direccion) <= 255),

                telefono TEXT NOT NULL
                CHECK(length(telefono) BETWEEN 8 AND 15),

                cargo_id INTEGER NOT NULL,

                password TEXT NOT NULL,


                FOREIGN KEY(cargo_id)
                REFERENCES cargo(cargo_id)
            )
            '''
        )


        # ---------------------------------------------------------------------
        # NOTAS
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS notas (

                nota_id INTEGER PRIMARY KEY AUTOINCREMENT,

                nota INTEGER NOT NULL
                CHECK(nota BETWEEN 1 AND 10),

                materia TEXT NOT NULL
                CHECK(length(materia) <= 255),

                comentario TEXT NOT NULL
                CHECK(length(comentario) <= 255)
            )
            '''
        )
        # ---------------------------------------------------------------------
        # ACCESOS
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS accesos (

                acceso_id INTEGER PRIMARY KEY AUTOINCREMENT,

                dni INTEGER NOT NULL,

                fecha_hora TEXT NOT NULL,

                exitoso BOOLEAN NOT NULL
            )
            '''
        )

        # ---------------------------------------------------------------------
        # AUSENCIAS
        # ---------------------------------------------------------------------

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS ausencias (

                ausencia_id INTEGER PRIMARY KEY AUTOINCREMENT,

                dni INTEGER NOT NULL,

                fecha DATE NOT NULL,

                justificada BOOLEAN NOT NULL,


                FOREIGN KEY(dni)
                REFERENCES alumnos(dni)
            )
            '''
        )


        conexion.commit()

        print(
            "¡Base de datos creada correctamente!"
        )


    except sqlite3.Error as e:

        print(
            f"Error al crear tablas: {e}"
        )


    finally:

        conexion.close()
