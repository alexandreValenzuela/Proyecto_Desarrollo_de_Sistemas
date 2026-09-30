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


def _tabla_existe(cursor, tabla):
    """Indica si la tabla ya fue creada."""
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (tabla,)
        )
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False


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


def _reconstruir_tabla(cursor, tabla, esquema_plantilla, columnas_mapeo,
                       desactivar_fk=False):
    """
    Reconstruye una tabla conservando los datos indicados en columnas_mapeo.

    SQLite no permite agregar restricciones (UNIQUE, CHECK, FK) con
    ALTER TABLE ADD COLUMN. La unica forma de agregarlas es crear la tabla
    nueva, copiar los datos y renombrar.

    esquema_plantilla: el CREATE TABLE con {tabla} como marcador de posicion.
    columnas_mapeo: lista de (columna_vieja, columna_nueva). Si una fila no
    tiene valor para una columna nueva, se inserta NULL.

    desactivar_fk: poner en True solo si otra tabla tiene una FK que apunta a
    {tabla}. DROP TABLE falla en ese caso y hay que desactivar las FK durante
    la reconstruccion. Quien llama es responsable de reactivarlas.
    """
    temporal = f"{tabla}_migracion"

    if desactivar_fk:
        # SQLite no permite dropear una tabla referenciada por una FK: si otra
        # tabla apunta aca, el DROP falla con "FOREIGN KEY constraint failed".
        # El PRAGMA se ignora si hay una transaccion abierta, asi que se
        # fuerza un commit antes de desactivarlo.
        cursor.connection.commit()
        cursor.execute("PRAGMA foreign_keys = OFF")

    cursor.execute(f"DROP TABLE IF EXISTS {temporal}")
    cursor.execute(esquema_plantilla.replace("{tabla}", temporal))

    origen = ", ".join(vieja for vieja, _ in columnas_mapeo)
    destino = ", ".join(nueva for _, nueva in columnas_mapeo)

    try:
        cursor.execute(
            f"INSERT INTO {temporal} ({destino}) "
            f"SELECT {origen} FROM {tabla}"
        )
    except sqlite3.IntegrityError:
        # Hay filas huerfanas: se copian una por una y se descartan las que
        # no se pueden associar, en vez de abortar la migracion completa.
        cursor.execute(f"DELETE FROM {temporal}")

        cursor.execute(f"SELECT * FROM {tabla}")
        nombres = [d[0] for d in cursor.description]

        for fila in cursor.fetchall():
            registro = dict(zip(nombres, fila))
            valores = [registro.get(vieja) for vieja, _ in columnas_mapeo]

            if any(valor is None for valor in valores):
                continue

            try:
                cursor.execute(
                    f"INSERT INTO {temporal} ({destino}) "
                    f"VALUES ({', '.join('?' * len(valores))})",
                    valores
                )
            except sqlite3.IntegrityError:
                continue

    cursor.execute(f"DROP TABLE {tabla}")
    cursor.execute(f"ALTER TABLE {temporal} RENAME TO {tabla}")


def migrar_notas_con_alumno():
    """
    Asocia cada nota a un alumno.

    La tabla "notas" se creo sin dni: una nota no pertenecia a nadie. Se
    agrega la FK a alumnos y una restriccion UNIQUE (dni, materia) para que
    un alumno no tenga dos notas de la misma materia.

    Las notas huerfanas (sin alumno al que asociarse) no se pueden conservar
    porque dni es NOT NULL: se descartan. hoy la tabla esta vacia, asi que
    no se pierde informacion.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()

        if not _tabla_existe(cursor, "notas"):
            return 0

        migrada = "dni" in _columnas_existentes(cursor, "notas")

        if migrada:
            # El esquema ya es correcto, pero puede faltar el indice si la
            # base se creo con una version anterior de este modulo.
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notas_dni ON notas(dni)"
            )
            conexion.commit()
            return 0

        _reconstruir_tabla(
            cursor,
            "notas",
            '''
            CREATE TABLE {tabla} (
                nota_id INTEGER PRIMARY KEY AUTOINCREMENT,

                dni INTEGER NOT NULL,

                nota INTEGER NOT NULL
                CHECK(nota BETWEEN 1 AND 10),

                materia TEXT NOT NULL
                CHECK(length(materia) <= 255),

                comentario TEXT,

                FOREIGN KEY(dni)
                REFERENCES alumnos(dni),

                UNIQUE(dni, materia)
            )
            ''',
            [("nota_id", "nota_id"), ("nota", "nota"),
             ("materia", "materia"), ("comentario", "comentario")]
        )

        # Indice para buscar notas por alumno.
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_notas_dni ON notas(dni)"
        )

        conexion.commit()

    return 1


def _asegurar_indice(cursor, tabla, indice, columnas):
    """Crea un indice solo si la tabla tiene las columnas indicadas."""
    existentes = _columnas_existentes(cursor, tabla)

    if not existentes or not set(columnas).issubset(existentes):
        return False

    cursor.execute(
        f"CREATE INDEX IF NOT EXISTS {indice} ON {tabla}({', '.join(columnas)})"
    )
    return True


def migrar_ausencias_sin_duplicados():
    """
    Impide registrar dos veces la misma ausencia.

    La tabla "ausencias" permitia cargar varias filas para el mismo alumno
    en la misma fecha. Se agrega UNIQUE(dni, fecha): una ausencia por dia
    y por alumno, que es como funciona un registro de asistencia.

    La tabla no cambia de columnas, solo se agrega la restriccion, asi que
    la reconstruccion conserva todos los datos existentes.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()

        if not _tabla_existe(cursor, "ausencias"):
            return 0

        # Detectar si ya existe la restriccion en el esquema guardado.
        esquema = cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='ausencias'"
        ).fetchone()[0]

        if "UNIQUE" in esquema.upper():
            _asegurar_indice(cursor, "ausencias", "idx_ausencias_dni", ["dni"])
            conexion.commit()
            return 0

        _reconstruir_tabla(
            cursor,
            "ausencias",
            '''
            CREATE TABLE {tabla} (
                ausencia_id INTEGER PRIMARY KEY AUTOINCREMENT,

                dni INTEGER NOT NULL,

                fecha DATE NOT NULL,

                justificada BOOLEAN NOT NULL,

                FOREIGN KEY(dni)
                REFERENCES alumnos(dni),

                UNIQUE(dni, fecha)
            )
            ''',
            [("ausencia_id", "ausencia_id"), ("dni", "dni"),
             ("fecha", "fecha"), ("justificada", "justificada")]
        )

        _asegurar_indice(cursor, "ausencias", "idx_ausencias_dni", ["dni"])

        conexion.commit()

    return 1


def _cursos_nivel_grupo():
    """Genera los 26 cursos: N1G1..N1G6 y N2G1..N6G4."""
    grupos_por_defecto = 4
    grupos_por_nivel = {1: 6}

    return [
        f"N{nivel}G{grupo}"
        for nivel in range(1, 7)
        for grupo in range(
            1, grupos_por_nivel.get(nivel, grupos_por_defecto) + 1
        )
    ]


def migrar_curso_a_nivel_grupo():
    """
    Cambia el formato de los cursos de "1A1A" a "N1G1" (nivel 1 grupo 1).

    El patron del CHECK cambio, asi que la tabla se reconstruye: los cursos
    viejos con formato [0-9][A-Z][0-9][A-Z] ya no son validos y no se
    pueden copiar. Son datos de prueba inventados, asi que se descartan y
    el seed vuelve a cargar los 26 reales.

    Como alumnos.curso_id tiene FK a esta tabla, los alumnos que apuntaban
    a un curso descartado quedan apuntando a un id inexistente. Se los
    reasigna al primer curso real y se avisa por pantalla: son datos de
    prueba, pero perderlos en silencio seria peor.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()

        if not _tabla_existe(cursor, "curso"):
            return 0

        esquema = cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='curso'"
        ).fetchone()[0]

        if "GLOB '[A-Z][0-9][A-Z][0-9]'" in esquema:
            return 0

        # Id del primer curso real, para reasignar alumnos huerfanos.
        cursos = _cursos_nivel_grupo()
        primer_curso = cursos[0]

        # NO borrar y reinsertar a ciegas: AUTOINCREMENT recicla los ids
        # 1..26 y un alumno que apuntaba al id 2 terminaria en un curso
        # DISTINTO que casualmente tiene ese id. La FK quedaria valida y
        # el error seria invisible. Se photographia a quien queda sin
        # curso antes de tocar nada.
        #
        # curso_id es NOT NULL, asi que no se puede dejar en NULL: todos
        # van al primer curso real y se informan por DNI.
        afectados = cursor.execute(
            "SELECT dni, curso_id FROM alumnos"
        ).fetchall()

        _reconstruir_tabla(
            cursor,
            "curso",
            """
            CREATE TABLE {tabla} (
                curso_id INTEGER PRIMARY KEY AUTOINCREMENT,
                curso TEXT NOT NULL UNIQUE,
                CHECK(length(curso) = 4),
                CHECK(
                    curso GLOB '[A-Z][0-9][A-Z][0-9]'
                )
            )
            """,
            [("curso_id", "curso_id"), ("curso", "curso")],
            desactivar_fk=True
        )

        # Los cursos viejos no se copian: violan el CHECK nuevo.
        cursor.execute("DELETE FROM curso")

        cursor.executemany(
            "INSERT INTO curso (curso) VALUES (?)",
            [(c,) for c in cursos]
        )

        if afectados:
            nuevo_id = cursor.execute(
                "SELECT curso_id FROM curso WHERE curso = ?", (primer_curso,)
            ).fetchone()[0]

            for dni, _ in afectados:
                cursor.execute(
                    "UPDATE alumnos SET curso_id = ? WHERE dni = ?",
                    (nuevo_id, dni)
                )

            dnis = ", ".join(str(dni) for dni, _ in afectados)
            print(
                f"Migracion: {len(afectados)} alumno(s) estaban en cursos con "
                f"el formato viejo, que ya no existe. Se movieron todos a "
                f"{primer_curso}. Reasignalos a mano: DNI {dnis}."
            )

        # Reactivar las FK y verificar que no quedara ninguna rota. El PRAGMA
        # se ignora con una transaccion abierta, de ahi el commit previo.
        conexion.commit()
        cursor.execute("PRAGMA foreign_keys = ON")

        rotas = cursor.execute("PRAGMA foreign_key_check").fetchall()

        if rotas:
            raise sqlite3.IntegrityError(
                f"La migracion de cursos dejo {len(rotas)} referencia(s) "
                f"rota(s) entre tablas. Revisar alumnos.curso_id."
            )

        conexion.commit()

    return 1


def migraciones():
    """Punto de entrada. Ejecutar en cada arranque de la aplicacion."""
    migrar_passwords_a_hash()
    migrar_curso_a_nivel_grupo()
    migrar_notas_con_alumno()
    migrar_ausencias_sin_duplicados()
