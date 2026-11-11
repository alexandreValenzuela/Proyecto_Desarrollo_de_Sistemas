"""
Vista "Cargar Alumnos": formulario de alta institucional.
Al guardar, crea el alumno con autorizado=1.
Dimensiones y estilo segun Draw.io SSOT.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                QLabel, QLineEdit, QComboBox, QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import (alerta_error, alerta_exito, SectionTitle,
                              PrimaryButton, DestructiveButton)
from models.alumno import Alumno
from models.curso import Curso

# Campos obligatorios del alta institucional, en orden de captura.
# El key es el que se usa para leer el valor desde self.entradas.
CAMPOS = [
    ("Nombre Completo", "nombre"),
    ("DNI / Documento", "dni"),
    ("Apellido", "apellido"),
    ("DirecciÃ³n", "direccion"),
    ("TelÃ©fono", "telefono"),
    ("Fecha de Nacimiento (AAAA-MM-DD)", "fecha_nacimiento"),
]


class VistaCargarAlumnos(QWidget):

    def __init__(self, on_guardado=None, on_volver=None):
        super().__init__()
        self.on_guardado = on_guardado
        self.on_volver = on_volver
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Titulo
        lbl = SectionTitle("Registro de Alumno", 40)
        layout.addWidget(lbl)

        # Formulario centrado en cuadrícula 2 columnas
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        grid.setAlignment(Qt.AlignCenter)

        def _crear_label_form(texto):
            label = QLabel(texto)
            label.setStyleSheet("""
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 15px;
                font-weight: bold;
                color: #000000;
                background: transparent;
            """)
            return label

        def _crear_campo_layout(label_widget, input_widget):
            box = QVBoxLayout()
            box.setSpacing(4)
            box.addWidget(label_widget)
            box.addWidget(input_widget)
            return box

        self.entradas = {}
        # Fila 0: Nombre y Apellido
        self.entradas["nombre"] = QLineEdit()
        self.entradas["nombre"].setPlaceholderText("Nombre Completo")
        self.entradas["nombre"].setMinimumSize(320, 42)
        self.entradas["nombre"].setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("Nombre Completo"), self.entradas["nombre"]), 0, 0)

        self.entradas["apellido"] = QLineEdit()
        self.entradas["apellido"].setPlaceholderText("Apellido")
        self.entradas["apellido"].setMinimumSize(320, 42)
        self.entradas["apellido"].setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("Apellido"), self.entradas["apellido"]), 0, 1)

        # Fila 1: DNI y Fecha de Nacimiento
        self.entradas["dni"] = QLineEdit()
        self.entradas["dni"].setPlaceholderText("DNI / Documento")
        self.entradas["dni"].setMinimumSize(320, 42)
        self.entradas["dni"].setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("DNI / Documento"), self.entradas["dni"]), 1, 0)

        self.entradas["fecha_nacimiento"] = QLineEdit()
        self.entradas["fecha_nacimiento"].setPlaceholderText("AAAA-MM-DD")
        self.entradas["fecha_nacimiento"].setMinimumSize(320, 42)
        self.entradas["fecha_nacimiento"].setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("Fecha de Nacimiento (AAAA-MM-DD)"), self.entradas["fecha_nacimiento"]), 1, 1)

        # Fila 2: Dirección y Teléfono
        self.entradas["direccion"] = QLineEdit()
        self.entradas["direccion"].setPlaceholderText("Dirección")
        self.entradas["direccion"].setMinimumSize(320, 42)
        self.entradas["direccion"].setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("Dirección"), self.entradas["direccion"]), 2, 0)

        self.entradas["telefono"] = QLineEdit()
        self.entradas["telefono"].setPlaceholderText("Teléfono")
        self.entradas["telefono"].setMinimumSize(320, 42)
        self.entradas["telefono"].setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("Teléfono"), self.entradas["telefono"]), 2, 1)

        # Fila 3: Curso y Contraseña
        self.combo_curso = QComboBox()
        self.combo_curso.addItem("Seleccionar curso", None)
        self.combo_curso.setMinimumSize(320, 42)
        self.combo_curso.setStyleSheet("font-size: 16px;")
        self._poblar_combo_cursos()
        grid.addLayout(_crear_campo_layout(_crear_label_form("Curso"), self.combo_curso), 3, 0)

        self.entrada_password = QLineEdit()
        self.entrada_password.setPlaceholderText("Contraseña")
        self.entrada_password.setEchoMode(QLineEdit.Password)
        self.entrada_password.setMinimumSize(320, 42)
        self.entrada_password.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(_crear_label_form("Contraseña"), self.entrada_password), 3, 1)

        contenedor_grid = QHBoxLayout()
        contenedor_grid.setAlignment(Qt.AlignCenter)
        contenedor_grid.addLayout(grid)
        layout.addLayout(contenedor_grid)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet("color: #ff0000; font-size: 15px; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_guardar = PrimaryButton("Guardar Alumno", self._guardar_alumno, 25)
        btn_guardar.setMinimumSize(220, 55)
        btn_layout.addWidget(btn_guardar)

        btn_volver = DestructiveButton("Volver", self.on_volver, 25)
        btn_volver.setMinimumSize(220, 55)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

    def _poblar_combo_cursos(self):
        try:
            cursos = Curso.obtener_todos()
            for c in cursos:
                self.combo_curso.addItem(c.curso, c.curso_id)
        except Exception:
            pass

    def _leer_campos(self):
        valores = {key: self.entradas[key].text().strip() for key in self.entradas}
        valores["password"] = self.entrada_password.text().strip()
        valores["curso_id"] = self.combo_curso.currentData()
        return valores

    def _guardar_alumno(self):
        try:
            datos = self._leer_campos()

            if not all([
                datos["nombre"],
                datos["dni"],
                datos["apellido"],
                datos["direccion"],
                datos["telefono"],
                datos["fecha_nacimiento"],
                datos["password"],
                datos["curso_id"],
            ]):
                self.lbl_error.setText("Todos los campos son obligatorios.")
                alerta_error(
                    self, "Error al guardar",
                    "Todos los campos son obligatorios."
                )
                return

            # Regla de negocio: el alta institucional ya nasce autorizada.
            nuevo = Alumno(
                dni=datos["dni"],
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                direccion=datos["direccion"],
                fecha_nacimiento=datos["fecha_nacimiento"],
                telefono=datos["telefono"],
                password=datos["password"],
                curso_id=datos["curso_id"],
                autorizado=1
            )
            nuevo.guardar()

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al guardar", str(e))
            return

        except Exception as e:
            # Red de seguridad: ningun error de alta puede cerrar la app.
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", "Alumno registrado exitosamente.")
        self._limpiar_formulario()

        if self.on_guardado:
            self.on_guardado()

    def _limpiar_formulario(self):
        for entrada in self.entradas.values():
            entrada.clear()
        self.entrada_password.clear()
        self.combo_curso.setCurrentIndex(0)
        self.lbl_error.clear()

