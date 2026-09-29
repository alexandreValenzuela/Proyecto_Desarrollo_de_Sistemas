from functools import wraps


class PermisoDenegadoError(Exception):
    """Se lanza cuando un usuario no tiene el nivel de permisos necesario."""
    pass


def requiere_permiso(nivel_minimo):
    """
    Decorador que bloquea la ejecución de una función si el usuario
    (dict devuelto por Personal.login) no alcanza el nivel mínimo.

    La función decorada debe recibir el usuario como primer argumento
    posicional, o como argumento nombrado 'usuario'.
    """

    def decorador(funcion):

        @wraps(funcion)
        def envoltura(*args, **kwargs):

            usuario = kwargs.get("usuario")

            if usuario is None and args:
                usuario = args[0]

            if usuario is None or "nivel_permisos" not in usuario:
                raise PermisoDenegadoError(
                    "No se pudo determinar el nivel de permisos del usuario."
                )

            if usuario["nivel_permisos"] < nivel_minimo:
                raise PermisoDenegadoError(
                    f"El cargo '{usuario.get('cargo', '?')}' no tiene permisos "
                    f"suficientes para esta acción (requiere nivel {nivel_minimo})."
                )

            return funcion(*args, **kwargs)

        return envoltura

    return decorador


def tiene_permiso(usuario, nivel_minimo):
    """
    Indica si el usuario alcanza el nivel de permisos requerido.

    Pensado para la capa de presentacion, donde el usuario es un dict
    con 'nivel_permisos' y no el primer argumento posicional de una funcion.
    """
    if usuario is None:
        return False

    return usuario.get("nivel_permisos", 0) >= nivel_minimo