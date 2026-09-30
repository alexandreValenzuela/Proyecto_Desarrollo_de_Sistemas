from models.personal import Personal
from models.alumno import Alumno
from models.acceso import Acceso
from auth.permisos import requiere_permiso, PermisoDenegadoError
from auth.autenticacion import login_unificado


@requiere_permiso(10)
def accion_eliminar_alumno(usuario, dni):
    if Alumno.eliminar(dni):
        print(f"Alumno con DNI {dni} eliminado.")
    else:
        print("No se encontró un alumno con ese DNI.")


@requiere_permiso(10)
def accion_asignar_cargo(usuario, dni_objetivo, nuevo_cargo_id):
    if Personal.asignar_cargo(usuario, dni_objetivo, nuevo_cargo_id):
        print("Cargo asignado correctamente.")


@requiere_permiso(5)
def accion_ver_historial_accesos(usuario, dni):
    historial = Acceso.historial_por_dni(dni)

    if not historial:
        print("No hay accesos registrados para ese DNI.")
        return

    for acceso_id, dni_reg, fecha, exitoso in historial:
        estado = "OK" if exitoso else "FALLIDO"
        print(f"[{fecha}] DNI {dni_reg} -> {estado}")


@requiere_permiso(3)
def accion_listar_alumnos(usuario):
    alumnos = Alumno.obtener_todos()

    if not alumnos:
        print("No hay alumnos cargados.")
        return

    for alumno in alumnos:
        print(alumno)


def accion_ver_pendientes(usuario):
    pendientes = Alumno.obtener_pendientes()

    if not pendientes:
        print("No hay alumnos pendientes.")
        return

    for dni, nombre, apellido in pendientes:
        print(f"DNI {dni} - {nombre} {apellido}")


def accion_autorizar_alumno(usuario, dni):
    try:
        if Alumno.autorizar(usuario, dni):
            print("Alumno autorizado.")
        else:
            print("No se encontró un alumno pendiente con ese DNI.")

    except PermisoDenegadoError as e:
        print(f"Acceso denegado: {e}")


def _mostrar_menu(usuario):
    print("\n--- MENU PRINCIPAL ---")
    print(f"Usuario: {usuario['nombre']} {usuario['apellido']} "
          f"({usuario['cargo']}, nivel {usuario['nivel_permisos']}, tipo {usuario['tipo']})")
    print("1) Listar alumnos")
    print("2) Ver historial de accesos de un DNI")

    if usuario["tipo"] == "personal" and usuario["nivel_permisos"] >= 3:
        print("3) Ver alumnos pendientes de autorización")
        print("4) Autorizar alumno por DNI")

    if usuario["tipo"] == "personal" and usuario["nivel_permisos"] >= 10:
        print("5) Eliminar alumno")
        print("6) Asignar cargo a personal")

    print("0) Cerrar sesión")


def _ejecutar_opcion(usuario, opcion):
    try:
        if opcion == "1":
            accion_listar_alumnos(usuario)

        elif opcion == "2":
            dni = int(input("DNI a consultar: "))
            accion_ver_historial_accesos(usuario, dni)

        elif opcion == "3":
            accion_ver_pendientes(usuario)

        elif opcion == "4":
            dni = int(input("DNI del alumno a autorizar: "))
            accion_autorizar_alumno(usuario, dni)

        elif opcion == "5":
            dni = int(input("DNI del alumno a eliminar: "))
            accion_eliminar_alumno(usuario, dni)

        elif opcion == "6":
            dni_objetivo = int(input("DNI del personal a modificar: "))
            nuevo_cargo_id = int(input("Nuevo cargo_id: "))
            accion_asignar_cargo(usuario, dni_objetivo, nuevo_cargo_id)

        else:
            print("Opción inválida.")

    except PermisoDenegadoError as e:
        print(f"Acceso denegado: {e}")

    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")


def _leer_entrada(prompt):
    """Lee una linea de stdin. Devuelve None si el input se agota (EOF, por
    ejemplo un pipe o un < archivo) o si el usuario corta con Ctrl+C, para
    que la consola termine limpia en vez de tirar traceback."""
    try:
        return input(prompt)

    except (EOFError, KeyboardInterrupt):
        return None


def iniciar_sesion_consola():
    print("=== INICIO DE SESION ===")

    dni = _leer_entrada("DNI (o 'salir' para terminar): ")

    # Sin input disponible es igual que 'salir': no hay con quien autenticarse.
    if dni is None:
        return "salir"

    dni = dni.strip()

    # Sentinel: corta el ciclo de sesiones sin pedir contrasena.
    if dni.lower() == "salir":
        return "salir"

    password = _leer_entrada("Contraseña: ")

    if password is None:
        return "salir"

    try:
        usuario = login_unificado(dni, password)

    except PermisoDenegadoError as e:
        print(f"No podés ingresar: {e}")
        return None

    if not usuario:
        print("Usuario o contraseña incorrectos.")
        return None

    return usuario


def ejecutar_menu_consola():
    while True:
        usuario = iniciar_sesion_consola()

        if usuario == "salir":
            print("Hasta luego.")
            return

        if not usuario:
            continue  # credenciales inválidas: volver a preguntar

        print(f"\nBienvenido, {usuario['nombre']}.")

        while True:
            _mostrar_menu(usuario)
            opcion = _leer_entrada("Elegí una opción: ")

            # Input agotado en el menu: termina el proceso, no reinicia login.
            if opcion is None:
                print("Hasta luego.")
                return

            if opcion == "0":
                print("Sesión cerrada.")
                break  # vuelve al login, no termina el proceso

            _ejecutar_opcion(usuario, opcion)

if __name__ == "__main__":
    try:
        ejecutar_menu_consola()

    except KeyboardInterrupt:
        # Ctrl+C en cualquier punto: salida limpia, codigo 0.
        print("\nHasta luego.")