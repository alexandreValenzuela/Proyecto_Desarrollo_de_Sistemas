"""
Tests de autenticacion, permisos y gestion de contrasenas.
"""
import pytest

from auth.passwords import hashear, verificar, validar_contrasena
from auth.permisos import requiere_permiso, tiene_permiso, PermisoDenegadoError
from auth.autenticacion import login_unificado
from models.personal import Personal
from models.alumno import Alumno
from models.acceso import Acceso


# ========================================================================
# HASHING
# ========================================================================

def test_hash_no_es_texto_plano():
    hash_ = hashear("secreta123")

    assert "secreta123" not in hash_
    assert hash_.startswith("pbkdf2_sha256$")
    assert verificar("secreta123", hash_)


def test_hash_es_salteado():
    """Dos llamadas dan hashes distintos (sal aleatoria) y ambos verifican."""
    uno = hashear("secreta123")
    otro = hashear("secreta123")

    assert uno != otro
    assert verificar("secreta123", uno)
    assert verificar("secreta123", otro)


def test_verificar_rechaza_mal():
    hash_ = hashear("secreta123")

    assert not verificar("otra", hash_)
    assert not verificar("", hash_)
    assert not verificar("secreta123", None)
    assert not verificar("secreta123", "basura")


def test_validar_contrasena_corta():
    with pytest.raises(ValueError):
        validar_contrasena("123")

    with pytest.raises(ValueError):
        validar_contrasena("")

    validar_contrasena("1234567")


# ========================================================================
# PERMISOS
# ========================================================================

def test_tiene_permiso(usuarios):
    assert tiene_permiso(usuarios["admin"], 3)
    assert not tiene_permiso(usuarios["preceptor"], 5)
    assert not tiene_permiso(usuarios["profesor"], 10)


def test_requiere_permiso_bloquea(usuarios):
    @requiere_permiso(5)
    def solo_profesor(usuario):
        return "ok"

    assert solo_profesor(usuarios["profesor"]) == "ok"
    assert solo_profesor(usuarios["admin"]) == "ok"

    with pytest.raises(PermisoDenegadoError):
        solo_profesor(usuarios["preceptor"])


# ========================================================================
# LOGIN UNIFICADO
# ========================================================================

def test_login_personal(usuarios):
    usuario = login_unificado(11111111, "1234")

    assert usuario["tipo"] == "personal"
    assert usuario["nivel_permisos"] == 10
    assert usuario["nombre"] == "Matt"


def test_login_alumno(crear_alumno):
    crear_alumno(dni=45000001, password="demo123")

    usuario = login_unificado(45000001, "demo123")

    assert usuario["tipo"] == "alumno"
    assert usuario["nivel_permisos"] == 0


def test_login_password_incorrecto(crear_alumno):
    crear_alumno(dni=45000001, password="demo123")

    assert login_unificado(45000001, "incorrecta") is None
    # El intento fallido queda registrado.
    fallos = [
        f for f in Acceso.historial_por_dni(45000001) if f[3] == 0
    ]
    assert len(fallos) == 1


def test_login_alumno_no_autorizado(crear_alumno):
    crear_alumno(dni=45000001, password="demo123", autorizado=0)

    with pytest.raises(PermisoDenegadoError):
        login_unificado(45000001, "demo123")


def test_login_registra_un_solo_intento(crear_alumno):
    """Un login de alumno deja 1 fila en accesos, no 2 (tabla personal +
    tabla alumnos)."""
    crear_alumno(dni=45000001, password="demo123")
    Acceso.historial()  # fuerza la lectura previa (vacia la vista, no la tabla)

    login_unificado(45000001, "demo123")

    historial = [f for f in Acceso.historial() if f[1] == 45000001]
    assert len(historial) == 1


# ========================================================================
# CAMBIO / RESET DE CONTRASENA
# ========================================================================

def test_cambiar_password_personal_ok(usuarios):
    assert Personal.cambiar_password(11111111, "1234", "nueva123") is True

    # La nueva contrasena sirve para loguearse; la vieja ya no.
    assert Personal.login(11111111, "nueva123") is not None
    assert Personal.login(11111111, "1234") is None


def test_cambiar_password_personal_actual_incorrecta(usuarios):
    with pytest.raises(ValueError):
        Personal.cambiar_password(11111111, "no-es-la-actual", "nueva123")


def test_cambiar_password_personal_nueva_corta(usuarios):
    with pytest.raises(ValueError):
        Personal.cambiar_password(11111111, "1234", "123")


def test_cambiar_password_alumno(crear_alumno):
    crear_alumno(dni=45000001, password="demo123")

    assert Alumno.cambiar_password(45000001, "demo123", "otra123") is True
    assert Alumno.login(45000001, "otra123") is not None
    assert Alumno.login(45000001, "demo123") is None


def test_resetear_password_personal(usuarios):
    assert Personal.resetear_password(11111111, "reseteada1") is True
    assert Personal.login(11111111, "reseteada1") is not None


def test_resetear_password_alumno(crear_alumno):
    crear_alumno(dni=45000001, password="demo123")

    assert Alumno.resetear_password(45000001, "reseteada1") is True
    assert Alumno.login(45000001, "reseteada1") is not None


def test_resetear_password_dni_inexistente(usuarios):
    assert Personal.resetear_password(99999999, "reseteada1") is None
    assert Alumno.resetear_password(99999999, "reseteada1") is None
