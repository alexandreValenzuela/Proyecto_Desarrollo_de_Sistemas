"""
Vista de bienvenida dentro del Dashboard.

Se muestra al iniciar sesion con el nombre del usuario logueado y un
resumen de datos segun el rol:
- Alumno: promedio general y ausencias propias.
- Personal: totales del sistema (alumnos, pendientes de autorizar, notas).
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from models.alumno import Alumno
from models.nota import Nota
from models.ausencia import Ausencia


class VistaBienvenido(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        nombre = self.usuario.get("nombre", "")
        cargo = self.usuario.get("cargo", "")

        lbl = QLabel(f"Bienvenido, {nombre}")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 30px;")
        layout.addWidget(lbl)

        lbl_rol = QLabel(f"Rol: {cargo}")
        lbl_rol.setObjectName("ResumenLinea")
        layout.addWidget(lbl_rol)

        self._agregar_resumen(layout)

        layout.addStretch()

    def _agregar_resumen(self, layout):
        """Muestra los datos de resumen segun el rol del usuario."""
        lbl_titulo = QLabel("Resumen")
        lbl_titulo.setObjectName("ResumenTitulo")
        layout.addWidget(lbl_titulo)

        try:
            if self.usuario.get("tipo") == "alumno":
                self._resumen_alumno(layout)
            else:
                self._resumen_staff(layout)

        except Exception:
            # La bienvenida jamas debe romper por una consulta fallida: el
            # resto del sistema sigue funcional.
            self._linea_resumen(layout, "No se pudo cargar el resumen.")

    def _resumen_alumno(self, layout):
        dni = self.usuario.get("dni")

        promedio = Nota.promedio_por_alumno(dni)
        total_ausencias = Ausencia.contar_por_alumno(dni)
        justificadas = Ausencia.contar_por_alumno(
            dni, solo_justificadas=True
        )

        texto_promedio = (
            f"Promedio general: {promedio:.1f}"
            if promedio is not None
            else "Promedio general: sin notas cargadas"
        )
        self._linea_resumen(layout, texto_promedio)
        self._linea_resumen(
            layout,
            f"Ausencias: {total_ausencias} "
            f"({justificadas} justificadas, "
            f"{total_ausencias - justificadas} sin justificar)"
        )

    def _resumen_staff(self, layout):
        total_alumnos = len(Alumno.obtener_todos())
        pendientes = len(Alumno.obtener_pendientes())
        total_notas = len(Nota.obtener_todas())
        total_ausencias = len(Ausencia.obtener_todas())

        self._linea_resumen(layout, f"Alumnos cargados: {total_alumnos}")
        self._linea_resumen(layout, f"Pendientes de autorizar: {pendientes}")
        self._linea_resumen(layout, f"Notas cargadas: {total_notas}")
        self._linea_resumen(layout, f"Ausencias registradas: {total_ausencias}")

    def _linea_resumen(self, layout, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("ResumenLinea")
        layout.addWidget(lbl)