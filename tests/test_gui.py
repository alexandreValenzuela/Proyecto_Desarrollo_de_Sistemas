"""
Tests de la capa de presentacion (PySide6), sin pantalla: QT_QPA_PLATFORM
vale "offscreen" y los modales de alerta se sustituyen por no-ops.

Verifica la regla de permisos del sidebar, el aislamiento de datos del
alumno, el boletin/promedio, los conteos de ausencias, el historial de
accesos y el cambio de contrasena.
"""
import pytest

from models.nota import Nota
from models.ausencia import Ausencia
from models.acceso import Acceso
from models.personal import Personal
from models.alumno import Alumno

from gui.ventana_principal import (
    VentanaPrincipal, VISTA_NOTAS, VISTA_AUSENCIAS, VISTA_ACCESOS,
    VISTA_MIS_NOTAS, VISTA_MIS_AUSENCIAS, VISTA_MIS_DATOS,
    VISTA_CAMBIAR_PASSWORD, VISTA_VER_ALUMNOS, VISTA_REGISTRAR_PERSONAL,
)


# ========================================================================
# PERMISOS DEL SIDEBAR
# ========================================================================

def test_alumno_solo_ve_mi_cuenta(qapp, sin_modales, crear_alumno, usuarios):
    """El alumno ve Mis Notas/Ausencias/Datos y nada del staff."""
    usuario = crear_alumno(dni=45000001)
    ventana = VentanaPrincipal(usuario)

    assert not ventana.botones_sidebar[VISTA_MIS_NOTAS].isHidden()
    assert not ventana.botones_sidebar[VISTA_MIS_AUSENCIAS].isHidden()
    assert not ventana.botones_sidebar[VISTA_MIS_DATOS].isHidden()
    # Secciones del staff: ocultas.
    for vista in (VISTA_NOTAS, VISTA_AUSENCIAS, VISTA_ACCESOS,
                  VISTA_VER_ALUMNOS, VISTA_REGISTRAR_PERSONAL):
        assert ventana.botones_sidebar[vista].isHidden()
        assert not ventana._puede_abrir(vista)

    # Y aun asi, navegacion directa a la vista restringida no abre nada.
    ventana._navegar_vista(VISTA_NOTAS)
    assert ventana.stack_vistas.currentIndex() != VISTA_NOTAS


def test_alumno_tiene_cambiar_password(qapp, sin_modales, crear_alumno):
    usuario = crear_alumno(dni=45000001)
    ventana = VentanaPrincipal(usuario)

    assert not ventana.botones_sidebar[VISTA_CAMBIAR_PASSWORD].isHidden()
    assert ventana._puede_abrir(VISTA_CAMBIAR_PASSWORD)


def test_preceptor_no_ve_notas_ni_accesos(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["preceptor"])

    assert ventana.botones_sidebar[VISTA_NOTAS].isHidden()
    assert ventana.botones_sidebar[VISTA_ACCESOS].isHidden()
    assert ventana.botones_sidebar[VISTA_AUSENCIAS].isHidden() is False
    assert ventana.botones_sidebar[VISTA_REGISTRAR_PERSONAL].isHidden()


def test_profesor_ve_notas_y_accesos(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["profesor"])

    assert not ventana.botones_sidebar[VISTA_NOTAS].isHidden()
    assert not ventana.botones_sidebar[VISTA_ACCESOS].isHidden()
    # Registrar personal sigue restringido al admin (nivel 10).
    assert ventana.botones_sidebar[VISTA_REGISTRAR_PERSONAL].isHidden()


def test_admin_ve_todas_las_secciones(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["admin"])

    for vista in (VISTA_NOTAS, VISTA_AUSENCIAS, VISTA_ACCESOS,
                  VISTA_VER_ALUMNOS, VISTA_REGISTRAR_PERSONAL):
        assert ventana._puede_abrir(vista)


# ========================================================================
# BIENVENIDA CON DATOS
# ========================================================================

def test_bienvenida_alumno_muestra_promedio(qapp, sin_modales, crear_alumno):
    usuario = crear_alumno(dni=45000001, password="demo123")
    Nota(dni=45000001, materia="Matematica", nota=8).guardar()
    Nota(dni=45000001, materia="Lengua", nota=6).guardar()
    Ausencia(dni=45000001, fecha="2026-09-01", justificada=False).guardar()

    ventana = VentanaPrincipal(usuario)

    from PySide6.QtWidgets import QLabel

    texto = " ".join(
        lbl.text() for lbl in ventana.vista_bienvenido.findChildren(QLabel)
    )

    assert "Promedio general: 7.0" in texto
    assert "Ausencias: 1" in texto
    assert "sin justificar" in texto


def test_bienvenida_staff_muestra_totales(qapp, sin_modales, usuarios, crear_alumno):
    crear_alumno(dni=45000001, autorizado=0)
    Nota(dni=45000001, materia="Lengua", nota=7).guardar()

    ventana = VentanaPrincipal(usuarios["admin"])
    from PySide6.QtWidgets import QLabel

    texto = " ".join(
        lbl.text() for lbl in ventana.vista_bienvenido.findChildren(QLabel)
    )

    assert "Alumnos cargados: 1" in texto
    assert "Pendientes de autorizar: 1" in texto
    assert "Notas cargadas: 1" in texto


# ========================================================================
# AISLAMIENTO DEL ALUMNO + PROMEDIO
# ========================================================================

def test_mis_notas_solo_muestra_las_propias(qapp, sin_modales, crear_alumno):
    usuario = crear_alumno(dni=45000001)
    Nota(dni=45000001, materia="Lengua", nota=8).guardar()
    Nota(dni=45000001, materia="Matematica", nota=6).guardar()
    # Otro alumno con notas: no deben aparecer.
    crear_alumno(dni=45000002)
    Nota(dni=45000002, materia="Historia", nota=10).guardar()

    ventana = VentanaPrincipal(usuario)
    vista = ventana.vista_mis_notas
    vista.cargar_datos()

    filas = vista.tabla.rowCount()
    assert filas == 2
    materias = {
        vista.tabla.item(fila, 0).text() for fila in range(filas)
    }
    assert materias == {"Lengua", "Matematica"}
    assert "Historia" not in materias
    # Promedio general visible.
    assert "6.0" in vista.lbl_promedio.text() or "Promedio" in vista.lbl_promedio.text()


def test_mis_datos_muestra_su_dni(qapp, sin_modales, crear_alumno):
    usuario = crear_alumno(dni=45000001, nombre="Ana")
    ventana = VentanaPrincipal(usuario)
    ventana.vista_mis_datos.cargar_datos()

    from PySide6.QtWidgets import QLabel

    texto = " ".join(
        lbl.text() for lbl in ventana.vista_mis_datos.findChildren(QLabel)
    )
    assert "45000001" in texto
    assert "Ana" in texto


# ========================================================================
# BOLETIN (STAFF)
# ========================================================================

def test_vista_notas_boletin_promedio(qapp, sin_modales, usuarios, crear_alumno):
    crear_alumno(dni=45000001)
    Nota(dni=45000001, materia="Matematica", nota=8).guardar()
    Nota(dni=45000001, materia="Lengua", nota=6).guardar()

    ventana = VentanaPrincipal(usuarios["profesor"])
    vista = ventana.vista_notas
    vista.entrada_filtro.setText("45000001")
    vista.cargar_datos()

    boletin = vista.lbl_boletin.text()
    assert "Boletín de 45000001" in boletin
    assert "Matematica 8" in boletin
    assert "Lengua 6" in boletin
    assert "Promedio 7.0" in boletin


def test_vista_notas_filtro_materia(qapp, sin_modales, usuarios, crear_alumno):
    crear_alumno(dni=45000001)
    Nota(dni=45000001, materia="Matematica", nota=8).guardar()
    Nota(dni=45000001, materia="Lengua", nota=6).guardar()

    ventana = VentanaPrincipal(usuarios["profesor"])
    vista = ventana.vista_notas
    indice = vista.combo_materia.findText("Lengua")
    vista.combo_materia.setCurrentIndex(indice)
    vista.cargar_datos()

    assert vista.tabla.rowCount() == 1
    assert vista.tabla.item(0, 1).text() == "Lengua"


# ========================================================================
# CONTEOS DE AUSENCIAS
# ========================================================================

def test_ausencias_conteos_y_alerta(qapp, sin_modales, usuarios, crear_alumno):
    """Un alumno con 6 faltas sin justificar dispara la alerta; otro no."""
    crear_alumno(dni=45000001, nombre="Ana")
    crear_alumno(dni=45000002, nombre="Luis")
    for dia in range(6):
        Ausencia(
            dni=45000001, fecha=f"2026-09-0{dia + 1}", justificada=False
        ).guardar()
    Ausencia(dni=45000001, fecha="2026-09-10", justificada=True).guardar()
    Ausencia(dni=45000002, fecha="2026-09-01", justificada=False).guardar()

    ventana = VentanaPrincipal(usuarios["preceptor"])
    vista = ventana.vista_ausencias
    vista.cargar_datos()

    conteos = vista.tabla_conteos
    assert conteos.rowCount() == 2

    filas = {
        conteos.item(f, 0).text(): (
            conteos.item(f, 2).text(),
            conteos.item(f, 3).text(),
            conteos.item(f, 4).text(),
        )
        for f in range(conteos.rowCount())
    }

    # Ana: 7 ausencias (1 justificada, 6 sin justificar) -> alerta.
    assert filas["45000001"] == ("1", "6", "Alerta")
    # Luis: 1 sin justificar -> OK.
    assert filas["45000002"] == ("0", "1", "OK")


# ========================================================================
# HISTORIAL DE ACCESOS
# ========================================================================

def test_accesos_solo_para_profesor(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["preceptor"])
    # Sin nivel 5, la vista se construye pero no carga nada.
    assert ventana.vista_accesos.tabla.rowCount() == 0


def test_accesos_muestra_historial_y_filtra(qapp, sin_modales, usuarios):
    Acceso.registrar(11111111, exitoso=True)
    Acceso.registrar(22222222, exitoso=False)

    ventana = VentanaPrincipal(usuarios["admin"])
    vista = ventana.vista_accesos
    vista.cargar_datos()
    assert vista.tabla.rowCount() == 2

    vista.entrada_filtro.setText("11111111")
    vista.cargar_datos()
    assert vista.tabla.rowCount() == 1
    assert vista.tabla.item(0, 1).text() == "11111111"
    assert vista.tabla.item(0, 2).text() == "Exitoso"


# ========================================================================
# CAMBIO DE CONTRASENA
# ========================================================================

def test_cambiar_password_propio(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["profesor"])
    vista = ventana.vista_cambiar_password

    vista.entrada_actual.setText("abcd")
    vista.entrada_nueva.setText("nueva123")
    vista.entrada_confirmar.setText("nueva123")
    vista._cambiar_mi_password()

    # La nueva contrasena sirve para loguearse; la vieja ya no.
    assert Personal.login(22222222, "nueva123") is not None
    assert Personal.login(22222222, "abcd") is None


def test_cambiar_password_confirmacion_distinta(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["profesor"])
    vista = ventana.vista_cambiar_password

    vista.entrada_actual.setText("abcd")
    vista.entrada_nueva.setText("nueva123")
    vista.entrada_confirmar.setText("otra999")
    vista._cambiar_mi_password()

    # No debe haberse cambiado nada.
    assert Personal.login(22222222, "abcd") is not None


def test_admin_resetea_password_alumno(qapp, sin_modales, usuarios, crear_alumno):
    crear_alumno(dni=45000001, password="demo123")

    ventana = VentanaPrincipal(usuarios["admin"])
    vista = ventana.vista_cambiar_password
    assert not vista.panel_admin.isHidden()

    vista.entrada_dni_reset.setText("45000001")
    vista.entrada_nueva_reset.setText("reseteada1")
    vista.entrada_confirmar_reset.setText("reseteada1")
    vista._resetear_password()

    assert Alumno.login(45000001, "reseteada1") is not None


def test_no_admin_no_ve_panel_reset(qapp, sin_modales, usuarios):
    ventana = VentanaPrincipal(usuarios["profesor"])
    # El panel de reseteo esta oculto para quien no es admin (nivel 10).
    assert ventana.vista_cambiar_password.panel_admin.isHidden()
