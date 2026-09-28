"""
Ventana de Registro publico de NeoED.
Registro de alumnos — queda pendiente de autorizacion (autorizado=0).
Dimensiones: 1600x900px, fondo #66B2FF.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt

from gui.componentes import (HeaderTitleLabel, PrimaryButton,
                              DestructiveButton, CustomLineEdit, ErrorLabel)
from models.alumno import Alumno
from models.curso import Curso


class VentanaRegistro(QWidget):

    def __init__(self, al_registrar=None, al_volver=None):
        super().__init__()

        self.al_registrar = al_registrar
        self.al_volver = al_volver

        self.setWindowTitle("NeoED - Registro de alumno")
        self.setFixedSize(1600, 900)
        self.setObjectName("CanvasBase")

        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Titulo
        layout.addWidget(HeaderTitleLabel("Registro de Alumno", 50))

        layout.addSpacing(20)

        # Campos del formulario
        campos_config = [
            ("Nombre Completo", False),
            ("DNI / Documento", False),
        ]

        self.entradas = []
        for texto, es_pass in campos_config:
            lbl = QLabel(texto)
            lbl.setStyleSheet("""
                font-family: 'Cascadia Code', monospace;
                font-size: 20px; color: #000000; background: transparent;
            """)
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)

            entrada = CustomLineEdit(placeholder=texto, es_password=es_pass, size=20)
            entrada.setFixedSize(450, 50)
            contenedor = QHBoxLayout()
            contenedor.setAlignment(Qt.AlignCenter)
            contenedor.addWidget(entrada)
            layout.addLayout(contenedor)
            self.entradas.append(entrada)

        # Curso
        lbl_curso = QLabel("Curso")
        lbl_curso.setStyleSheet("""
            font-family: 'Cascadia Code', monospace;
            font-size: 20px; color: #000000; background: transparent;
        """)
        lbl_curso.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_curso)

        self.combo_curso = QComboBox()
        self.combo_curso.addItem("Seleccionar curso", None)
        self.combo_curso.setFixedSize(450, 50)
        self.combo_curso.setStyleSheet("font-size: 20px;")
        try:
            cursos = Curso.obtener_todos()
            for c in cursos:
                self.combo_curso.addItem(c.curso, c.curso_id)
        except Exception:
            pass
        contenedor_curso = QHBoxLayout()
        contenedor_curso.setAlignment(Qt.AlignCenter)
        contenedor_curso.addWidget(self.combo_curso)
        layout.addLayout(contenedor_curso)

        # Contrasena
        lbl_pass = QLabel("Contrasena")
        lbl_pass.setStyleSheet("""
            font-family: 'Cascadia Code', monospace;
            font-size: 20px; color: #000000; background: transparent;
        """)
        lbl_pass.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_pass)

        self.entrada_password = CustomLineEdit(placeholder="Contrasena", es_password=True, size=20)
        self.entrada_password.setFixedSize(450, 50)
        contenedor_pass = QHBoxLayout()
        contenedor_pass.setAlignment(Qt.AlignCenter)
        contenedor_pass.addWidget(self.entrada_password)
        layout.addLayout(contenedor_pass)

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

        btn_registrar = PrimaryButton("Registrarme", self._intentar_registro, 25)
        btn_registrar.setFixedSize(210, 60)
        btn_layout.addWidget(btn_registrar)

        if self.al_volver:
            btn_volver = DestructiveButton("Volver", self.al_volver, 25)
            btn_volver.setFixedSize(210, 60)
            btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _intentar_registro(self):
        curso_id = self.combo_curso.currentData()

        try:
            nuevo = Alumno(
                dni=self.entradas[0].text().strip(),
                nombre=self.entradas[0].text().strip(),
                apellido=self.entradas[1].text().strip(),
                direccion="",
                fecha_nacimiento="2000-01-01",
                telefono="0000000000",
                password=self.entrada_password.text().strip(),
                curso_id=curso_id,
                autorizado=0
            )
            nuevo.guardar()

        except (ValueError, RuntimeError) as e:
            self.label_error.setText(str(e))
            return

        QMessageBox.information(
            self, "Registro exitoso",
            "Tu cuenta fue creada. Queda pendiente de autorizacion."
        )

        if self.al_registrar:
            self.al_registrar()
