"""
Tests de la capa de datos: cursos, alumnos, notas, ausencias y accesos.
"""
import pytest

from models.curso import Curso
from models.alumno import Alumno
from models.nota import Nota
from models.ausencia import Ausencia
from models.acceso import Acceso
from models.materia import Materia, nivel_de_curso, especialidad_de_curso


# ========================================================================
# CURSO
# ========================================================================

def test_cursos_base_cargados():
    """El seed deja los 26 cursos reales."""
    assert len(Curso.obtener_todos()) == 26


def test_curso_rechaza_formato_invalido():
    """El CHECK del esquema (patron N1G1) se aplica al guardar."""
    with pytest.raises(ValueError):
        Curso(curso_id=999, curso="NMAL").guardar()


# ========================================================================
# ALUMNO
# ========================================================================

def test_alumno_guardar_y_obtener(crear_alumno):
    usuario = crear_alumno(dni=45000001, nombre="Ana", apellido="Gomez")

    alumno = Alumno.obtener_por_dni(45000001)

    assert alumno is not None
    assert alumno.nombre == "Ana"
    assert alumno.apellido == "Gomez"
    assert alumno.autorizado == 1
    # La contrasena nunca queda en texto plano: la columna "password" se deja
    # vacia y el hash vive aparte. El login verifica contra el hash.
    assert alumno.password == ""
    assert Alumno.login(45000001, "demo123") is not None
    assert usuario["tipo"] == "alumno"


def test_alumno_dni_duplicado(crear_alumno):
    crear_alumno(dni=45000001)

    with pytest.raises(ValueError):
        crear_alumno(dni=45000001, nombre="Otro", apellido="Alumno")


def test_alumno_telefono_invalido():
    alumno = Alumno(
        dni=45000009, nombre="Mal", apellido="Telefono",
        direccion="Dir 1", fecha_nacimiento="2010-01-01",
        telefono="123", password="demo123", curso_id=1,
    )
    with pytest.raises(ValueError):
        alumno.guardar()


def test_alumno_fecha_invalida():
    alumno = Alumno(
        dni=45000009, nombre="Mal", apellido="Fecha",
        direccion="Dir 1", fecha_nacimiento="01/01/2010",
        telefono="1122334455", password="demo123", curso_id=1,
    )
    with pytest.raises(ValueError):
        alumno.guardar()


def test_alumno_borrar_bloqueado_por_fk(crear_alumno):
    """
    Borrar un alumno con notas o ausencias asociadas lo bloquea la FK:
    los datos historicos no se pierden en silencio.
    """
    crear_alumno(dni=45000001)
    Nota(dni=45000001, materia="Lengua", nota=8).guardar()
    Ausencia(dni=45000001, fecha="2026-09-01", justificada=True).guardar()

    with pytest.raises(RuntimeError):
        Alumno.eliminar(45000001)

    # Sin notas ni ausencias, el borrado si procede.
    Nota.eliminar_por_alumno(45000001)
    Ausencia.eliminar_por_alumno(45000001)
    assert Alumno.eliminar(45000001) is True
    assert Alumno.obtener_por_dni(45000001) is None


def test_alumno_pendientes_y_autorizar(crear_alumno):
    crear_alumno(dni=45000001, autorizado=0)
    crear_alumno(dni=45000002, autorizado=1)

    pendientes = Alumno.obtener_pendientes()
    assert [f[0] for f in pendientes] == [45000001]

    autorizante = {"nivel_permisos": 3}
    assert Alumno.autorizar(autorizante, 45000001) is True
    assert Alumno.obtener_pendientes() == []


def test_alumno_obtener_todos_no_desalinea_campos(crear_alumno):
    """
    obtener_todos() tiene que traer las columnas en el orden del
    constructor. Con un SELECT mas corto, autorizado volia 0, curso_id
    venía None y el telefono de respaldo caia en el campo equivocado.
    """
    crear_alumno(dni=45000001, autorizado=1, nombre="Ana")

    alumno = Alumno.obtener_todos()[0]

    assert alumno.dni == 45000001
    assert alumno.nombre == "Ana"
    assert alumno.autorizado == 1
    assert alumno.curso_id is not None
    assert alumno.telefono == "1122334455"
    assert alumno.telefono_respaldo is None
    # La columna "password" de la base va vacia: el hash esta aparte.
    assert alumno.password == ""


def test_alumno_autorizar_sin_permiso(crear_alumno):
    crear_alumno(dni=45000001, autorizado=0)

    from auth.permisos import PermisoDenegadoError

    with pytest.raises(PermisoDenegadoError):
        Alumno.autorizar({"nivel_permisos": 0}, 45000001)


# ========================================================================
# NOTA
# ========================================================================

def test_nota_guardar_y_promedio(crear_alumno):
    crear_alumno(dni=45000001)
    Nota(dni=45000001, materia="Matematica", nota=8).guardar()
    Nota(dni=45000001, materia="Lengua", nota=6).guardar()

    notas = Nota.obtener_por_alumno(45000001)
    assert len(notas) == 2
    assert [n.materia for n in notas] == ["Lengua", "Matematica"]
    assert Nota.promedio_por_alumno(45000001) == 7.0


def test_nota_promedio_sin_notas(crear_alumno):
    crear_alumno(dni=45000001)
    assert Nota.promedio_por_alumno(45000001) is None


def test_nota_unica_por_alumno_materia(crear_alumno):
    crear_alumno(dni=45000001)
    Nota(dni=45000001, materia="Lengua", nota=8).guardar()

    with pytest.raises(ValueError):
        Nota(dni=45000001, materia="Lengua", nota=9).guardar()


def test_nota_fuera_de_rango(crear_alumno):
    crear_alumno(dni=45000001)
    with pytest.raises(ValueError):
        Nota(dni=45000001, materia="Lengua", nota=11).guardar()


def test_nota_actualizar_y_eliminar(crear_alumno):
    crear_alumno(dni=45000001)
    nota = Nota(dni=45000001, materia="Ingles", nota=5, comentario="Bien")
    nota.guardar()

    nota.nota = 9
    nota.comentario = "Muy bien"
    assert nota.actualizar() is True

    actualizada = Nota.obtener_por_id(nota.nota_id)
    assert actualizada.nota == 9
    assert actualizada.comentario == "Muy bien"

    assert Nota.eliminar(nota.nota_id) is True
    assert Nota.obtener_por_id(nota.nota_id) is None


def test_nota_alumno_inexistente(crear_alumno):
    crear_alumno(dni=45000001)
    with pytest.raises(ValueError):
        Nota(dni=99999999, materia="Lengua", nota=7).guardar()


def test_notas_obtener_materias(crear_alumno):
    crear_alumno(dni=45000001)
    crear_alumno(dni=45000002)
    Nota(dni=45000001, materia="Matematica", nota=7).guardar()
    Nota(dni=45000001, materia="Lengua", nota=6).guardar()
    Nota(dni=45000002, materia="Artes", nota=9).guardar()

    assert Nota.obtener_materias() == ["Artes", "Lengua", "Matematica"]


# ========================================================================
# AUSENCIA
# ========================================================================

def test_ausencia_unicidad_por_fecha(crear_alumno):
    crear_alumno(dni=45000001)
    Ausencia(dni=45000001, fecha="2026-09-01", justificada=True).guardar()

    with pytest.raises(ValueError):
        Ausencia(dni=45000001, fecha="2026-09-01", justificada=False).guardar()


def test_ausencia_contar(crear_alumno):
    crear_alumno(dni=45000001)
    Ausencia(dni=45000001, fecha="2026-09-01", justificada=True).guardar()
    Ausencia(dni=45000001, fecha="2026-09-02", justificada=False).guardar()
    Ausencia(dni=45000001, fecha="2026-09-03", justificada=False).guardar()

    assert Ausencia.contar_por_alumno(45000001) == 3
    assert Ausencia.contar_por_alumno(
        45000001, solo_justificadas=True
    ) == 1


def test_ausencia_justificar_y_eliminar(crear_alumno):
    crear_alumno(dni=45000001)
    ausencia = Ausencia(
        dni=45000001, fecha="2026-09-01", justificada=False
    )
    ausencia.guardar()

    ausencia.justificada = True
    assert ausencia.actualizar() is True
    assert Ausencia.obtener_por_id(ausencia.ausencia_id).justificada is True

    assert Ausencia.eliminar(ausencia.ausencia_id) is True
    assert Ausencia.obtener_por_id(ausencia.ausencia_id) is None


def test_ausencia_fecha_invalida(crear_alumno):
    crear_alumno(dni=45000001)
    with pytest.raises(ValueError):
        Ausencia(
            dni=45000001, fecha="01-09-2026", justificada=False
        ).guardar()


# ========================================================================
# ACCESO
# ========================================================================

def test_acceso_registra_exitoso_y_fallido():
    Acceso.registrar(45000001, exitoso=True)
    Acceso.registrar(45000001, exitoso=False)

    historial = Acceso.historial_por_dni(45000001)
    assert len(historial) == 2
    # Todos los intentos quedan registrados, exitosos y fallidos.
    assert sorted(f[3] for f in historial) == [0, 1]


def test_acceso_historial_global():
    Acceso.registrar(45000001, exitoso=True)
    Acceso.registrar(11111111, exitoso=False)

    assert len(Acceso.historial()) == 2


# ========================================================================
# MATERIA
# ========================================================================

def _un_curso():
    cursos = Curso.obtener_todos()
    assert cursos
    return cursos[0]


def test_especialidad_por_grupo():
    """G1/G3 -> Computacion; G2/G4 -> Gestion y Administracion."""
    assert especialidad_de_curso("N1G1") == "Computacion"
    assert especialidad_de_curso("N2G3") == "Computacion"
    assert especialidad_de_curso("N3G2") == "Gestion y Administracion de las Organizaciones"
    assert especialidad_de_curso("N4G4") == "Gestion y Administracion de las Organizaciones"


def test_nivel_de_curso():
    assert nivel_de_curso("N5G2") == 5


def test_materia_guardar_y_obtener():
    curso = _un_curso()
    materia = Materia(nombre="Matematica", curso_id=curso.curso_id)
    assert materia.guardar() is True
    assert materia.materia_id is not None

    obtenida = Materia.obtener_por_id(materia.materia_id)
    assert obtenida is not None
    assert obtenida.nombre == "Matematica"
    assert obtenida.curso_id == curso.curso_id


def test_materia_nombre_duplicado():
    curso = _un_curso()
    Materia(nombre="Lengua", curso_id=curso.curso_id).guardar()

    with pytest.raises(ValueError):
        Materia(nombre="Lengua", curso_id=curso.curso_id).guardar()


def test_materia_nombre_vacio_rechazado():
    curso = _un_curso()
    with pytest.raises(ValueError):
        Materia(nombre="", curso_id=curso.curso_id).guardar()


def test_materia_obtener_todos_ordenado():
    curso = _un_curso()
    Materia(nombre="Zeta", curso_id=curso.curso_id).guardar()
    Materia(nombre="Alpha", curso_id=curso.curso_id).guardar()

    nombres = [m.nombre for m in Materia.obtener_todos()]
    assert "Alpha" in nombres and "Zeta" in nombres
    assert nombres.index("Alpha") < nombres.index("Zeta")


def test_materia_filtrar_por_nivel_y_especialidad():
    """Filtro por nivel (año) y especialidad derivada del grupo del curso."""
    curso_comp = None
    curso_gest = None
    for c in Curso.obtener_todos():
        esp = especialidad_de_curso(c.curso)
        if esp == "Computacion" and curso_comp is None:
            curso_comp = c
        elif esp == "Gestion y Administracion de las Organizaciones" and curso_gest is None:
            curso_gest = c
        if curso_comp and curso_gest:
            break

    assert curso_comp is not None and curso_gest is not None

    Materia(nombre="Algoritmos", curso_id=curso_comp.curso_id).guardar()
    Materia(nombre="Contabilidad", curso_id=curso_gest.curso_id).guardar()

    nivel_comp = nivel_de_curso(curso_comp.curso)

    comp = Materia.obtener_por_filtro(nivel=nivel_comp, especialidad="Computacion")
    assert any(m.nombre == "Algoritmos" for m in comp)
    assert not any(m.nombre == "Contabilidad" for m in comp)

    gest = Materia.obtener_por_filtro(
        especialidad="Gestion y Administracion de las Organizaciones"
    )
    assert any(m.nombre == "Contabilidad" for m in gest)

    todas = Materia.obtener_por_filtro()
    assert any(m.nombre == "Algoritmos" for m in todas)
    assert any(m.nombre == "Contabilidad" for m in todas)


def test_materia_eliminar():
    curso = _un_curso()
    materia = Materia(nombre="Historia", curso_id=curso.curso_id)
    materia.guardar()

    assert Materia.obtener_por_id(materia.materia_id) is not None
    assert Materia.eliminar(materia.materia_id) is True
    assert Materia.obtener_por_id(materia.materia_id) is None
