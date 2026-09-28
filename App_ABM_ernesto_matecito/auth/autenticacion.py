from models.personal import Personal
from models.alumno import Alumno


def login_unificado(dni, password):
    """
    Punto único de autenticación del sistema.

    Prueba primero contra 'personal' (administrador/profesor/preceptor).
    Si no coincide, prueba contra 'alumnos'.

    Devuelve un dict con al menos 'nivel_permisos' y 'tipo'
    ('personal' o 'alumno'), o None si las credenciales no son válidas.

    Puede propagar PermisoDenegadoError si el alumno existe pero
    todavía no fue autorizado.
    """

    usuario = Personal.login(dni, password)

    if usuario:
        usuario["tipo"] = "personal"
        return usuario

    return Alumno.login(dni, password)