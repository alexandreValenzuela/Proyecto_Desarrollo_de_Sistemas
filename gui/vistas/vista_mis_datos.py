"""
Vista "Mis Datos" (solo alumno): datos personales del propio usuario.
El curso se resuelve por el curso_id del alumno logueado.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGridLayout,
                                QFrame)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error
from models.alumno import Alumno
from models.curso import Curso


class VistaMisDatos(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._construir_interfaz()
        self.cargar_datos()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        lbl = QLabel("Mis Datos")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        lbl_ayuda = QLabel("Tu información personal.")
        lbl_ayuda.setAlignment(Qt.AlignCenter)
        lbl_ayuda.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 18px;
            color: #000000;
            background: transparent;
        """)
        layout.addWidget(lbl_ayuda)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        tarjeta = QFrame()
        tarjeta.setObjectName("CardFrame")
        cuadricula = QGridLayout(tarjeta)
        cuadricula.setContentsMargins(24, 24, 24, 24)
        cuadricula.setHorizontalSpacing(40)
        cuadricula.setVerticalSpacing(18)

        self.campos = {}
        filas = [
            ("DNI", "dni"),
            ("Nombre", "nombre"),
            ("Apellido", "apellido"),
            ("Curso", "curso"),
            ("Fecha de nacimiento", "fecha_nacimiento"),
            ("Teléfono", "telefono"),
            ("Dirección", "direccion"),
            ("Estado", "estado"),
        ]
        for i, (etiqueta, clave) in enumerate(filas):
            lbl_clave = QLabel(etiqueta)
            lbl_clave.setStyleSheet(
                "font-size: 18px; font-weight: bold;"
            )
            lbl_valor = QLabel("-")
            lbl_valor.setStyleSheet("font-size: 18px;")
            lbl_valor.setWordWrap(True)
            cuadricula.addWidget(lbl_clave, i, 0, Qt.AlignLeft)
            cuadricula.addWidget(lbl_valor, i, 1, Qt.AlignLeft)
            self.campos[clave] = lbl_valor

        cuadricula.setColumnStretch(0, 0)
        cuadricula.setColumnStretch(1, 1)

        layout.addWidget(tarjeta)
        layout.addStretch()

    def cargar_datos(self):
        try:
            alumno = Alumno.obtener_por_dni(self.usuario.get("dni"))
        except RuntimeError as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar datos", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        if alumno is None:
            self.lbl_error.setText("No se encontraron tus datos.")
            return

        self.lbl_error.clear()

        curso = "-"
        try:
            if alumno.curso_id is not None:
                c = Curso.obtener_por_id(alumno.curso_id)
                curso = c.curso if c is not None else "-"
        except RuntimeError:
            curso = "-"

        self.campos["dni"].setText(str(alumno.dni))
        self.campos["nombre"].setText(str(alumno.nombre))
        self.campos["apellido"].setText(str(alumno.apellido))
        self.campos["fecha_nacimiento"].setText(str(alumno.fecha_nacimiento))
        self.campos["telefono"].setText(str(alumno.telefono or "-"))
        self.campos["direccion"].setText(str(alumno.direccion or "-"))
        self.campos["curso"].setText(curso)
        estado = "Autorizado" if alumno.autorizado else "Pendiente de autorización"
        self.campos["estado"].setText(estado)