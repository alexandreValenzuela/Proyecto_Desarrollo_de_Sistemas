import sqlite3

from auth.passwords import hashear
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
        # Formato N<nivel>G<grupo>: "N1G1" es nivel 1, grupo 1.
        # El nivel 1 tiene 6 grupos; los niveles 2 a 6 tienen 4 cada uno.
        # El CHECK de database/setup.py exige el patron [A-Z][0-9][A-Z][0-9].
        # Se generan en vez de escribirse a mano: son 26 y cambian seguido.
        # ---------------------------------------------------------------------

        GRUPOS_POR_NIVEL = {1: 6}
        GRUPOS_POR_DEFECTO = 4
        NIVEL_MAXIMO = 6

        cursos = [
            (f"N{nivel}G{grupo}",)
            for nivel in range(1, NIVEL_MAXIMO + 1)
            for grupo in range(
                1, GRUPOS_POR_NIVEL.get(nivel, GRUPOS_POR_DEFECTO) + 1
            )
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

        # Cada password se hashea antes de insertar. El texto plano solo
        # existe en este archivo, nunca en la base de datos.
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
                password,
                password_hash
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            """,
            [
                (dni, nombre, apellido, direccion, telefono, cargo_id, "",
                 hashear(password))
                for (dni, nombre, apellido, direccion, telefono, cargo_id,
                     password) in personal
            ]
        )

        conexion.commit()

        print("Datos iniciales cargados correctamente.")

    except sqlite3.Error as e:

        print(f"Error cargando datos iniciales: {e}")

    finally:
        conexion.close()
