"""
Vista de Registro de Personal.
Alta de administradores/profesores/preceptores (nivel_permisos >= 10).
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                QLabel, QLineEdit, QComboBox, QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import (alerta_error, alerta_exito, SectionTitle,
                              PrimaryButton, DestructiveButton)
from models.personal import Personal
from models.cargo import Cargo
from auth.permisos import PermisoDenegadoError, tiene_permiso

# Nivel minimo para dar de alta personal (crea administradores).
NIVEL_MINIMO = 10


class VistaRegistrarPersonal(QWidget):

    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Titulo
        lbl = SectionTitle("Registro de Personal", 40)
        layout.addWidget(lbl)

        # Formulario en cuadrícula de 2 columnas
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        grid.setAlignment(Qt.AlignCenter)

        def _crear_campo_layout(label_widget, input_widget):
            box = QVBoxLayout()
            box.setSpacing(4)
            box.addWidget(label_widget)
            box.addWidget(input_widget)
            return box

        # Fila 0: Nombre y Apellido
        self.entrada_nombre = QLineEdit()
        self.entrada_nombre.setPlaceholderText("Nombre")
        self.entrada_nombre.setMinimumSize(320, 42)
        self.entrada_nombre.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("Nombre de Usuario"), self.entrada_nombre), 0, 0)

        self.entrada_apellido = QLineEdit()
        self.entrada_apellido.setPlaceholderText("Apellido")
        self.entrada_apellido.setMinimumSize(320, 42)
        self.entrada_apellido.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("Apellido"), self.entrada_apellido), 0, 1)

        # Fila 1: DNI y Dirección
        self.entrada_dni = QLineEdit()
        self.entrada_dni.setPlaceholderText("Ej: 55555555")
        self.entrada_dni.setMinimumSize(320, 42)
        self.entrada_dni.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("DNI"), self.entrada_dni), 1, 0)

        self.entrada_direccion = QLineEdit()
        self.entrada_direccion.setPlaceholderText("Direccion")
        self.entrada_direccion.setMinimumSize(320, 42)
        self.entrada_direccion.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("Direccion"), self.entrada_direccion), 1, 1)

        # Fila 2: Teléfono y Cargo
        self.entrada_telefono = QLineEdit()
        self.entrada_telefono.setPlaceholderText("Solo numeros")
        self.entrada_telefono.setMinimumSize(320, 42)
        self.entrada_telefono.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("Telefono"), self.entrada_telefono), 2, 0)

        self.combo_cargo = QComboBox()
        self.combo_cargo.addItem("Seleccionar cargo", None)
        try:
            cargos = Cargo.obtener_todos()
            for c in cargos:
                self.combo_cargo.addItem(c.cargo, c.cargo_id)
        except Exception:
            pass
        self.combo_cargo.setMinimumSize(320, 42)
        self.combo_cargo.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("Cargo"), self.combo_cargo), 2, 1)

        # Fila 3: Contraseña (columna 0)
        self.entrada_password = QLineEdit()
        self.entrada_password.setPlaceholderText("Contrasena")
        self.entrada_password.setEchoMode(QLineEdit.Password)
        self.entrada_password.setMinimumSize(320, 42)
        self.entrada_password.setStyleSheet("font-size: 16px;")
        grid.addLayout(_crear_campo_layout(self._label("Contrasena"), self.entrada_password), 3, 0)

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

        btn_registrar = PrimaryButton("Registrar Usuario", self._intentar_registro, 25)
        btn_registrar.setMinimumSize(220, 55)
        btn_layout.addWidget(btn_registrar)

        btn_volver = DestructiveButton("Volver", self.on_volver, 25)
        btn_volver.setMinimumSize(220, 55)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

    def _label(self, texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 15px;
            font-weight: bold;
            color: #000000;
            background: transparent;
        """)
        return lbl

    def _intentar_registro(self):
        cargo_id = self.combo_cargo.currentData()

        # Defensa en profundidad: la vista se oculta para quien no llega a
        # NIVEL_MINIMO, pero el handler vuelve a validar antes de escribir.
        if not tiene_permiso(self.usuario, NIVEL_MINIMO):
            self.lbl_error.setText("No tenÃ©s permisos para registrar personal.")
            alerta_error(
                self, "Permiso denegado",
                "No tenÃ©s permisos para registrar personal."
            )
            return

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

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al registrar", str(e))
            return

        except Exception as e:
            # Red de seguridad: ningun error de alta puede cerrar la app.
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", "Personal registrado correctamente.")
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

