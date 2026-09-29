"""
Vista de bienvenida dentro del Dashboard.
Se muestra al iniciar sesion con el nombre del usuario logueado.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


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
        lbl_rol.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 20px;
            color: #000000;
            background: transparent;
        """)
        layout.addWidget(lbl_rol)

        layout.addStretch()
