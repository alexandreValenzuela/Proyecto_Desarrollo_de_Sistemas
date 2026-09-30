"""
Ventana de Registro publico de NeoED.
Registro de alumnos — queda pendiente de autorizacion (autorizado=0).
Dimensiones: 1600x900px, fondo #66B2FF.

El formulario va dentro de un QScrollArea: son 8 filas y la ventana tiene
tamaño fijo, asi que sin scroll los ultimos campos quedan recortados.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QScrollArea)
from PySide6.QtCore import Qt

from gui.componentes import (HeaderTitleLabel, PrimaryButton,
                             DestructiveButton, CustomLineEdit, ErrorLabel,
                             alerta_error, alerta_exito)
from models.alumno import Alumno
from models.curso import Curso

# Orden de los campos de texto del formulario.
# El indice de cada clave es el que usa _leer_campos().
CAMPOS = [
    ("Nombre Completo", "nombre"),
    ("Apellido", "apellido"),
    ("DNI / Documento", "dni"),
    ("Fecha de Nacimiento (AAAA-MM-DD)", "fecha_nacimiento"),
    ("Dirección", "direccion"),
    ("Teléfono", "telefono"),
]


class VentanaRegistro(QWidget):

    def __init__(self, al_registrar=None, al_volver=None):
        super().__init__()

        self.al_registrar = al_registrar
        self.al_volver = al_volver

        self.setWindowTitle("NeoED - Registro de alumno")
        self.setFixedSize(1600, 900)
        self.setObjectName("CanvasBase")

        self._construir_interfaz()

    # ========================================================================
    # INTERFAZ
    # ========================================================================

    def _construir_interfaz(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        # Titulo
        layout.addWidget(HeaderTitleLabel("Registro de Alumno", 44))

        # Todo el formulario scrollea dentro de la ventana fija.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        contenedor = QWidget()
        contenedor.setObjectName("CanvasBase")
        form = QVBoxLayout(contenedor)
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(10)

        self.entradas = {}
        for texto, key in CAMPOS:
            form.addWidget(self._label(texto))
            entrada = CustomLineEdit(placeholder=texto, es_password=False, size=18)
            entrada.setFixedSize(450, 44)
            self.entradas[key] = entrada
            form.addLayout(self._centrado(entrada))

        # Curso
        form.addWidget(self._label("Curso"))

        self.combo_curso = QComboBox()
        self.combo_curso.addItem("Seleccionar curso", None)
        self.combo_curso.setFixedSize(450, 44)
        self.combo_curso.setStyleSheet("font-size: 18px;")
        self._poblar_combo_cursos()
        form.addLayout(self._centrado(self.combo_curso))

        # Contrasena
        form.addWidget(self._label("Contrasena"))

        self.entrada_password = CustomLineEdit(
            placeholder="Contrasena", es_password=True, size=18
        )
        self.entrada_password.setFixedSize(450, 44)
        form.addLayout(self._centrado(self.entrada_password))

        scroll.setWidget(contenedor)
        layout.addWidget(scroll, stretch=1)

        # Error
        self.label_error = ErrorLabel()
        layout.addWidget(self.label_error)

        # Info
        lbl_info = QLabel("Tu cuenta quedara pendiente hasta que\nun profesor o preceptor la autorice.")
        lbl_info.setStyleSheet("""
            font-family: 'Cascadia Code', monospace;
            font-size: 16px; color: #000000; background: transparent;
        """)
        lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_info)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_registrar = PrimaryButton("Registrarme", self._intentar_registro, 22)
        btn_registrar.setFixedSize(210, 55)
        btn_layout.addWidget(btn_registrar)

        if self.al_volver:
            btn_volver = DestructiveButton("Volver", self.al_volver, 22)
            btn_volver.setFixedSize(210, 55)
            btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _label(self, texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', monospace;
            font-size: 18px; color: #000000; background: transparent;
        """)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def _centrado(self, widget):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(widget)
        return layout

    def _poblar_combo_cursos(self):
        try:
            cursos = Curso.obtener_todos()
            for c in cursos:
                self.combo_curso.addItem(c.curso, c.curso_id)
        except Exception:
            pass

    # ========================================================================
    # ALTA DE ALUMNO
    # ========================================================================

    def _leer_campos(self):
        valores = {key: self.entradas[key].text().strip() for key in self.entradas}
        valores["password"] = self.entrada_password.text().strip()
        valores["curso_id"] = self.combo_curso.currentData()
        return valores

    def _intentar_registro(self):
        try:
            datos = self._leer_campos()

            if not all([
                datos["nombre"],
                datos["apellido"],
                datos["dni"],
                datos["fecha_nacimiento"],
                datos["direccion"],
                datos["telefono"],
                datos["password"],
                datos["curso_id"],
            ]):
                self.label_error.setText("Todos los campos son obligatorios.")
                alerta_error(
                    self, "Error al registrar",
                    "Todos los campos son obligatorios."
                )
                return

            # Regla de negocio: el registro publico nunca queda preautorizado.
            nuevo = Alumno(
                dni=datos["dni"],
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                direccion=datos["direccion"],
                fecha_nacimiento=datos["fecha_nacimiento"],
                telefono=datos["telefono"],
                password=datos["password"],
                curso_id=datos["curso_id"],
                autorizado=0
            )
            nuevo.guardar()

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.label_error.setText(str(e))
            alerta_error(self, "Error al registrar", str(e))
            return

        except Exception as e:
            # Red de seguridad: ningun error de alta puede cerrar la app.
            self.label_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(
            self, "Registro exitoso",
            "Tu cuenta fue creada. Queda pendiente de autorizacion."
        )

        if self.al_registrar:
            self.al_registrar()
