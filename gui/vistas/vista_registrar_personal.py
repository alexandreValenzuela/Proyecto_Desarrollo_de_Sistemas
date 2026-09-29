"""
Vista de Registro de Personal.
Alta de administradores/profesores/preceptores (nivel_permisos >= 10).
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt

from models.personal import Personal
from models.cargo import Cargo
from auth.permisos import PermisoDenegadoError


class VistaRegistrarPersonal(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Titulo
        lbl = QLabel("Registro de Personal")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 30px;")
        layout.addWidget(lbl)

        # Formulario
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(20)

        form_layout.addWidget(self._label("Nombre de Usuario"))
        self.entrada_nombre = QLineEdit()
        self.entrada_nombre.setPlaceholderText("Nombre")
        self.entrada_nombre.setFixedSize(450, 50)
        self.entrada_nombre.setStyleSheet("font-size: 20px;")
        contenedor = QHBoxLayout()
        contenedor.setAlignment(Qt.AlignCenter)
        contenedor.addWidget(self.entrada_nombre)
        form_layout.addLayout(contenedor)

        form_layout.addWidget(self._label("Apellido"))
        self.entrada_apellido = QLineEdit()
        self.entrada_apellido.setPlaceholderText("Apellido")
        self.entrada_apellido.setFixedSize(450, 50)
        self.entrada_apellido.setStyleSheet("font-size: 20px;")
        contenedor2 = QHBoxLayout()
        contenedor2.setAlignment(Qt.AlignCenter)
        contenedor2.addWidget(self.entrada_apellido)
        form_layout.addLayout(contenedor2)

        form_layout.addWidget(self._label("DNI"))
        self.entrada_dni = QLineEdit()
        self.entrada_dni.setPlaceholderText("Ej: 55555555")
        self.entrada_dni.setFixedSize(450, 50)
        self.entrada_dni.setStyleSheet("font-size: 20px;")
        contenedor3 = QHBoxLayout()
        contenedor3.setAlignment(Qt.AlignCenter)
        contenedor3.addWidget(self.entrada_dni)
        form_layout.addLayout(contenedor3)

        form_layout.addWidget(self._label("Direccion"))
        self.entrada_direccion = QLineEdit()
        self.entrada_direccion.setPlaceholderText("Direccion")
        self.entrada_direccion.setFixedSize(450, 50)
        self.entrada_direccion.setStyleSheet("font-size: 20px;")
        contenedor4 = QHBoxLayout()
        contenedor4.setAlignment(Qt.AlignCenter)
        contenedor4.addWidget(self.entrada_direccion)
        form_layout.addLayout(contenedor4)

        form_layout.addWidget(self._label("Telefono"))
        self.entrada_telefono = QLineEdit()
        self.entrada_telefono.setPlaceholderText("Solo numeros")
        self.entrada_telefono.setFixedSize(450, 50)
        self.entrada_telefono.setStyleSheet("font-size: 20px;")
        contenedor5 = QHBoxLayout()
        contenedor5.setAlignment(Qt.AlignCenter)
        contenedor5.addWidget(self.entrada_telefono)
        form_layout.addLayout(contenedor5)

        form_layout.addWidget(self._label("Cargo"))
        self.combo_cargo = QComboBox()
        self.combo_cargo.addItem("Seleccionar cargo", None)
        try:
            cargos = Cargo.obtener_todos()
            for c in cargos:
                self.combo_cargo.addItem(c.cargo, c.cargo_id)
        except Exception:
            pass
        self.combo_cargo.setFixedSize(450, 50)
        self.combo_cargo.setStyleSheet("font-size: 20px;")
        contenedor6 = QHBoxLayout()
        contenedor6.setAlignment(Qt.AlignCenter)
        contenedor6.addWidget(self.combo_cargo)
        form_layout.addLayout(contenedor6)

        form_layout.addWidget(self._label("Contrasena"))
        self.entrada_password = QLineEdit()
        self.entrada_password.setPlaceholderText("Contrasena")
        self.entrada_password.setEchoMode(QLineEdit.Password)
        self.entrada_password.setFixedSize(450, 50)
        self.entrada_password.setStyleSheet("font-size: 20px;")
        contenedor7 = QHBoxLayout()
        contenedor7.setAlignment(Qt.AlignCenter)
        contenedor7.addWidget(self.entrada_password)
        form_layout.addLayout(contenedor7)

        layout.addLayout(form_layout)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_registrar = QPushButton("Registrar Usuario")
        btn_registrar.setObjectName("PrimaryButton")
        btn_registrar.setFixedSize(210, 60)
        btn_registrar.setStyleSheet("font-size: 25px;")
        btn_registrar.setCursor(Qt.PointingHandCursor)
        btn_registrar.clicked.connect(self._intentar_registro)
        btn_layout.addWidget(btn_registrar)

        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setFixedSize(210, 60)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

    def _label(self, texto):
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 20px;
            color: #000000;
            background: transparent;
        """)
        return lbl

    def _intentar_registro(self):
        cargo_id = self.combo_cargo.currentData()

        try:
            nuevo = Personal(
                dni=self.entrada_dni.text().strip(),
                nombre=self.entrada_nombre.text().strip(),
                apellido=self.entrada_apellido.text().strip(),
                direccion=self.entrada_direccion.text().strip(),
                telefono=self.entrada_telefono.text().strip(),
                cargo_id=cargo_id,
                password=self.entrada_password.text().strip()
            )
            nuevo.guardar()

        except (ValueError, RuntimeError) as e:
            self.lbl_error.setText(str(e))
            return

        QMessageBox.information(self, "Exito", "Personal registrado correctamente.")
        self.lbl_error.clear()
        self._limpiar_formulario()

    def _limpiar_formulario(self):
        self.entrada_dni.clear()
        self.entrada_nombre.clear()
        self.entrada_apellido.clear()
        self.entrada_direccion.clear()
        self.entrada_telefono.clear()
        self.entrada_password.clear()
        self.combo_cargo.setCurrentIndex(0)
