from models.personal import Personal
from models.alumno import Alumno
from models.acceso import Acceso
from auth.permisos import PermisoDenegadoError


def login_unificado(dni, password):
    """
    Punto único de autenticación del sistema.

    Prueba primero contra 'personal' (administrador/profesor/preceptor).
    Si no coincide, prueba contra 'alumnos'.

    Devuelve un dict con al menos 'nivel_permisos' y 'tipo'
    ('personal' o 'alumno'), o None si las credenciales no son válidas.

    Puede propagar PermisoDenegadoError si el alumno existe pero
    todavía no fue autorizado.

    Registra **exactamente un** intento en la tabla accesos, tenga o no
    éxito. Antes cada login de alumno dejaba dos filas: el intento fallido
    contra 'personal' y luego el exitoso contra 'alumnos'. Eso duplicaba
    también los intentos fallidos, que son los que sirven para detectar
    fuerza bruta. Por eso los dos login internos se llaman con
    registrar_acceso=False y el registro se hace acá, una sola vez.
    """

    usuario = Personal.login(dni, password, registrar_acceso=False)

    if usuario:
        Acceso.registrar(dni, exitoso=True)
        usuario["tipo"] = "personal"
        return usuario

    try:
        alumno = Alumno.login(dni, password, registrar_acceso=False)
    except PermisoDenegadoError:
        # El alumno existe y la contraseña es correcta, pero todavia no
        # fue autorizado. Es un intento fallido: queda registrado.
        Acceso.registrar(dni, exitoso=False)
        raise

    if alumno:
        Acceso.registrar(dni, exitoso=True)
        alumno["tipo"] = "alumno"
        return alumno

    Acceso.registrar(dni, exitoso=False)
    return None
