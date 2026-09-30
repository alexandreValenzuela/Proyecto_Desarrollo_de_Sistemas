"""
Ventana de Bienvenida / Landing de NeoED.
Primera pantalla que ve el usuario: titulo NeoED + botones Iniciar Sesion / Crear Cuenta.
Dimensiones: 1600x900px, fondo #66B2FF.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from gui.componentes import HeaderTitleLabel, PrimaryButton, SecondaryButton


class VentanaLanding(QWidget):

    def __init__(self, al_iniciar_sesion=None, al_crear_cuenta=None):
        super().__init__()

        self.al_iniciar_sesion = al_iniciar_sesion
        self.al_crear_cuenta = al_crear_cuenta

        self.setWindowTitle("NeoED - Bienvenida")
        self.resize(1600, 900)
        self.setMinimumSize(1280, 800)
        self.setObjectName("CanvasBase")

        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(40)

        # Titulo principal
        layout.addWidget(HeaderTitleLabel("NeoED", 60))

        # Espaciador superior
        layout.addSpacing(80)

        # Contenedor de botones
        layout_btn = QVBoxLayout()
        layout_btn.setAlignment(Qt.AlignCenter)
        layout_btn.setSpacing(38)

        btn_ingresar = PrimaryButton("Iniciar Sesion", self.al_iniciar_sesion, 40)
        btn_ingresar.setMinimumSize(400, 80)
        layout_btn.addWidget(btn_ingresar)

        btn_crear = SecondaryButton("Crear Cuenta", self.al_crear_cuenta, 40)
        btn_crear.setMinimumSize(400, 80)
        layout_btn.addWidget(btn_crear)

        layout.addLayout(layout_btn)

        # Espaciador inferior
        layout.addSpacing(80)

        self.setLayout(layout)
