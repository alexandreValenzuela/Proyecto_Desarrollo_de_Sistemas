"""
Vista "Cargar Alumnos": formulario de alta institucional.
Al guardar, crea el alumno con autorizado=1.
Dimensiones y estilo segun Draw.io SSOT.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito
from models.alumno import Alumno
from models.curso import Curso

# Campos obligatorios del alta institucional, en orden de captura.
# El key es el que se usa para leer el valor desde self.entradas.
CAMPOS = [
    ("Nombre Completo", "nombre"),
    ("DNI / Documento", "dni"),
    ("Apellido", "apellido"),
    ("Dirección", "direccion"),
    ("Teléfono", "telefono"),
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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Titulo
        lbl = QLabel("Registro de Alumno")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 50px;")
        layout.addWidget(lbl)

        # Formulario centrado
        form = QVBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(20)

        self.entradas = {}
        for texto, key in CAMPOS:
            lbl_campo = QLabel(texto)
            lbl_campo.setStyleSheet("""
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 20px; color: #000000; background: transparent;
            """)
            form.addWidget(lbl_campo, alignment=Qt.AlignCenter)

            entrada = QLineEdit()
            entrada.setPlaceholderText(texto)
            entrada.setFixedSize(450, 50)
            entrada.setStyleSheet("font-size: 20px;")
            self.entradas[key] = entrada
            contenedor = QHBoxLayout()
            contenedor.setAlignment(Qt.AlignCenter)
            contenedor.addWidget(entrada)
            form.addLayout(contenedor)

        # Curso (ComboBox)
        lbl_curso = QLabel("Curso")
        lbl_curso.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 20px; color: #000000; background: transparent;
        """)
        form.addWidget(lbl_curso, alignment=Qt.AlignCenter)

        self.combo_curso = QComboBox()
        self.combo_curso.addItem("Seleccionar curso", None)
        self.combo_curso.setFixedSize(450, 50)
        self.combo_curso.setStyleSheet("font-size: 20px;")
        self._poblar_combo_cursos()
        contenedor_curso = QHBoxLayout()
        contenedor_curso.setAlignment(Qt.AlignCenter)
        contenedor_curso.addWidget(self.combo_curso)
        form.addLayout(contenedor_curso)

        # Contrasena
        lbl_pass = QLabel("Contrasena")
        lbl_pass.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 20px; color: #000000; background: transparent;
        """)
        form.addWidget(lbl_pass, alignment=Qt.AlignCenter)

        self.entrada_password = QLineEdit()
        self.entrada_password.setPlaceholderText("Contrasena")
        self.entrada_password.setEchoMode(QLineEdit.Password)
        self.entrada_password.setFixedSize(450, 50)
        self.entrada_password.setStyleSheet("font-size: 20px;")
        contenedor_pass = QHBoxLayout()
        contenedor_pass.setAlignment(Qt.AlignCenter)
        contenedor_pass.addWidget(self.entrada_password)
        form.addLayout(contenedor_pass)

        layout.addLayout(form)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_guardar = QPushButton("Guardar Alumno")
        btn_guardar.setObjectName("PrimaryButton")
        btn_guardar.setFixedSize(210, 60)
        btn_guardar.setStyleSheet("font-size: 25px;")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar_alumno)
        btn_layout.addWidget(btn_guardar)

        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setFixedSize(210, 60)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        if self.on_volver:
            btn_volver.clicked.connect(self.on_volver)
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
