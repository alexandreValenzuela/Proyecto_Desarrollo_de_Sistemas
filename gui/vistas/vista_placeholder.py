"""
Vista generica para secciones en desarrollo (placeholder).
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class VistaPlaceholder(QWidget):

    def __init__(self, titulo="Modulo en mantenimiento"):
        super().__init__()
        self._construir_interfaz(titulo)

    def _construir_interfaz(self, titulo):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("SectionTitle")
        lbl_titulo.setStyleSheet("font-size: 40px;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        lbl_detalle = QLabel("Este modulo esta en fase de mantenimiento\no actualizacion. Volve pronto.")
        lbl_detalle.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 20px;
            color: #000000;
            background: transparent;
        """)
        lbl_detalle.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_detalle)

        layout.addStretch()
