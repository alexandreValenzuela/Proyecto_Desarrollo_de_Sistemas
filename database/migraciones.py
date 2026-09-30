"""
Migraciones de esquema para NeoED.

SQLite no tiene "IF NOT EXISTS" para columnas, y CREATE TABLE IF NOT EXISTS
no modifica tablas existentes. Por eso este modulo agrega columnas de forma
idempotente y migra datos de versiones anteriores.

Ejecutar migraciones() es seguro aunque se llame en cada arranque.
"""
import sqlite3

from auth.passwords import hashear, es_hash_contrasena
from database.connection import obtener_conexion


# Tablas que tienen una columna "password" en texto plano desde el origen
TABLAS_CON_PASSWORD = ("alumnos", "personal")


def _columnas_existentes(cursor, tabla):
    """Devuelve el conjunto de nombres de columna de una tabla."""
    try:
        cursor.execute(f"PRAGMA table_info({tabla})")
        return {fila[1] for fila in cursor.fetchall()}
    except sqlite3.Error:
        return set()


def _agregar_columna(cursor, tabla, columna, definicion):
    """Agrega una columna solo si la tabla no la tiene todavia."""
    if not _columnas_existentes(cursor, tabla):
        # La tabla no existe todavia: la creara database/setup.py.
        return False

    if columna in _columnas_existentes(cursor, tabla):
        return False

    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")
    return True


def migrar_passwords_a_hash():
    """
    Convierte las contrasenas en texto plano de origen a hash PBKDF2.

    Para cada fila con la columna "password_hash" vacia, hashea la contrasena
    plana y la guarda. Luego limpia la columna "password" para que ningun
    archivo de la base contenga credenciales legibles.

    Las filas que ya tienen un hash (o cuya contrasena ya tiene formato de
    hash) se dejan intactas, asi el proceso es idempotente.
    """
    filas_migradas = 0

    with obtener_conexion() as conexion:
        cursor = conexion.cursor()

        for tabla in TABLAS_CON_PASSWORD:
            columnas = _columnas_existentes(cursor, tabla)

            if not columnas:
                continue

            _agregar_columna(cursor, tabla, "password_hash", "TEXT")

            # Recalcular por si acabamos de agregar la columna.
            columnas = _columnas_existentes(cursor, tabla)

            if "password" not in columnas:
                continue

            if "password_hash" not in columnas:
                continue

            cursor.execute(
                f"SELECT dni, password FROM {tabla} "
                f"WHERE password_hash IS NULL OR password_hash = ''"
            )
            pendientes = cursor.fetchall()

            for dni, password_plano in pendientes:
                if password_plano is None or password_plano == "":
                    continue

                # Si la "contrasena" ya es un hash, no la re-hasheamos.
                if es_hash_contrasena(password_plano):
                    cursor.execute(
                        f"UPDATE {tabla} SET password_hash = ?, password = '' "
                        f"WHERE dni = ?",
                        (password_plano, dni)
                    )
                    filas_migradas += 1
                    continue

                cursor.execute(
                    f"UPDATE {tabla} SET password_hash = ?, password = '' "
                    f"WHERE dni = ?",
                    (hashear(password_plano), dni)
                )
                filas_migradas += 1

            # Limpiar contrasenas que ya tenian hash, para no dejar
            # texto plano dando vueltas en archivos viejos.
            cursor.execute(
                f"UPDATE {tabla} SET password = '' "
                f"WHERE password_hash IS NOT NULL AND password_hash != '' "
                f"AND password != ''"
            )

        conexion.commit()

    return filas_migradas


def migraciones():
    """Punto de entrada. Ejecutar en cada arranque de la aplicacion."""
    return migrar_passwords_a_hash()
