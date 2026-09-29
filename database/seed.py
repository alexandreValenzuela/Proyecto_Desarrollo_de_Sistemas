import sqlite3

from database.connection import obtener_conexion

def cargar_datos_iniciales():

    conexion = obtener_conexion()

    try:

        cursor = conexion.cursor()

        # ---------------------------------------------------------------------
        # CARGOS (ROLES DEL SISTEMA)
        # ---------------------------------------------------------------------

        cargos = [
            (
                "Administrador",
                10
            ),

            (
                "Profesor",
                5
            ),

            (
                "Preceptor",
                3
            )
        ]


        cursor.executemany(
            """
            INSERT OR IGNORE INTO cargo
            (
                cargo,
                nivel_permisos
            )

            VALUES (?, ?)

            """,
            cargos
        )

        # ---------------------------------------------------------------------
        # CURSOS
        # El CHECK de database/setup.py exige 4 caracteres con el patron
        # [0-9][A-Z][0-9][A-Z] (ej: 1A1A). "1°A" o "Primero A" son invalidos.
        # ---------------------------------------------------------------------

        cursos = [
            ("1A1A",),
            ("1B1B",),
            ("2A2A",),
            ("2B2B",),
            ("3A3A",),
            ("3B3B",)
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO curso
            (
                curso
            )

            VALUES (?)

            """,
            cursos
        )

        # ---------------------------------------------------------------------
        # PERSONAL
        # ---------------------------------------------------------------------

        personal = [

            (
                11111111,
                "Matt",
                "Administrador",
                "Direccion ejemplo 123",
                "1123456789",
                1,
                "1234"
            ),

            (
                22222222,
                "Kira",
                "Profesor",
                "Direccion ejemplo 456",
                "1198765432",
                2,
                "abcd"
            ),

            (
                33333333,
                "Ariadna",
                "Preceptor",
                "Direccion ejemplo 789",
                "1155555555",
                3,
                "5678"
            )

        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO personal
            (
                dni,
                nombre,
                apellido,
                direccion,
                telefono,
                cargo_id,
                password
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

            """,
            personal
        )

        conexion.commit()

        print("Datos iniciales cargados correctamente.")

    except sqlite3.Error as e:

        print(f"Error cargando datos iniciales: {e}")

    finally:
        conexion.close()
