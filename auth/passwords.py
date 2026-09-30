"""
Hashing de contrasenas para NeoED.

Usa PBKDF2-HMAC-SHA256 con sal aleatoria por usuario.
Las contrasenas nunca se guardan en texto plano: la base almacena
el hash con su sal, en formato "pbkdf2_sha256$<iteraciones>$<sal>$<hash>".
"""
import hashlib
import hmac
import secrets


ITERACIONES = 260000
LONGITUD_SAL = 16
LONGITUD_HASH = 32
ALGORITMO = "pbkdf2_sha256"
LARGO_MINIMO = 6


def hashear(contrasena):
    """
    Devuelve el hash de una contrasena en texto plano.
    Genera una sal aleatoria nueva en cada llamada.
    """
    sal = secrets.token_bytes(LONGITUD_SAL)

    resumen = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        sal,
        ITERACIONES,
        dklen=LONGITUD_HASH
    )

    return f"{ALGORITMO}${ITERACIONES}${sal.hex()}${resumen.hex()}"


def verificar(contrasena, hash_almacenado):
    """
    Compara una contrasena contra un hash almacenado.

    Usa comparacion de tiempo constante para no filtrar informacion
    por analisis temporal.
    """
    if not hash_almacenado or not contrasena:
        return False

    partes = hash_almacenado.split("$")

    if len(partes) != 4 or partes[0] != ALGORITMO:
        return False

    _, iteraciones, sal_hex, esperado_hex = partes

    try:
        iteraciones = int(iteraciones)
        sal = bytes.fromhex(sal_hex)
        esperado = bytes.fromhex(esperado_hex)
    except (ValueError, TypeError):
        return False

    calculado = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        sal,
        iteraciones,
        dklen=len(esperado)
    )

    return hmac.compare_digest(calculado, esperado)


def es_hash_contrasena(valor):
    """Indica si un valor ya tiene formato de hash, no de contrasena plana."""
    if not valor or not isinstance(valor, str):
        return False

    partes = valor.split("$")

    return len(partes) == 4 and partes[0] == ALGORITMO


def validar_contrasena(contrasena):
    """Valida la robustez minima de una contrasena antes de hashearla."""
    if not contrasena:
        raise ValueError("La contraseña no puede estar vacía.")

    if len(contrasena) < LARGO_MINIMO:
        raise ValueError(
            f"La contraseña debe tener al menos {LARGO_MINIMO} caracteres."
        )

    return True
