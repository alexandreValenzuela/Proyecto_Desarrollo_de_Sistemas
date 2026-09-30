"""
Ventana de Login de NeoED.
Formulario centrado: titulo NeoED, campos DNI + Contrasena, botones Ingresar + Volver.
Dimensiones: 1600x900px, fondo #66B2FF.
"""
import sqlite3

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from gui.componentes import (HeaderTitleLabel, PrimaryButton,
                              DestructiveButton, CustomLineEdit, ErrorLabel,
                              alerta_error)
from models.personal import Personal
from auth.autenticacion import login_unificado
from auth.permisos import PermisoDenegadoError


class VentanaLogin(QWidget):

    def __init__(self, al_loguear=None, al_volver=None):
        super().__init__()

        self.al_loguear = al_loguear
        self.al_volver = al_volver

        self.setWindowTitle("NeoED - Inicio de sesion")
        self.resize(1600, 900)
        self.setMinimumSize(1280, 800)
        self.setObjectName("CanvasBase")

        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # Titulo
        layout.addWidget(HeaderTitleLabel("NeoED", 60))

        layout.addSpacing(60)

        # Campo usuario (DNI)
        self.entrada_dni = CustomLineEdit("DNI", size=25)
        self.entrada_dni.setMinimumSize(500, 70)
        self.entrada_dni.setAlignment(Qt.AlignCenter)

        contenedor_dni = QHBoxLayout()
        contenedor_dni.setAlignment(Qt.AlignCenter)
        contenedor_dni.addWidget(self.entrada_dni)
        layout.addLayout(contenedor_dni)

        # Campo contrasena
        self.entrada_password = CustomLineEdit("Contrasena", es_password=True, size=25)
        self.entrada_password.setMinimumSize(500, 70)
        self.entrada_password.setAlignment(Qt.AlignCenter)

        contenedor_pass = QHBoxLayout()
        contenedor_pass.setAlignment(Qt.AlignCenter)
        contenedor_pass.addWidget(self.entrada_password)
        layout.addLayout(contenedor_pass)

        # Error
        self.label_error = ErrorLabel()

        contenedor_error = QHBoxLayout()
        contenedor_error.setAlignment(Qt.AlignCenter)
        contenedor_error.addWidget(self.label_error)
        layout.addLayout(contenedor_error)

        layout.addSpacing(20)

        # Botones de accion
        layout_btn = QHBoxLayout()
        layout_btn.setAlignment(Qt.AlignCenter)
        layout_btn.setSpacing(60)

        btn_ingresar = PrimaryButton("Ingresar", self._intentar_login, 35)
        btn_ingresar.setMinimumSize(220, 70)
        layout_btn.addWidget(btn_ingresar)

        btn_volver = DestructiveButton("Volver", self._volver, 35)
        btn_volver.setMinimumSize(220, 70)
        layout_btn.addWidget(btn_volver)

        layout.addLayout(layout_btn)

        self.setLayout(layout)

    def _intentar_login(self):
        dni = self.entrada_dni.text().strip()
        password = self.entrada_password.text().strip()

        try:
            try:
                usuario = login_unificado(dni, password)

            except PermisoDenegadoError as e:
                self.label_error.setText(str(e))
                alerta_error(self, "Acceso denegado", str(e))
                self.entrada_dni.setStyleSheet(
                    self.entrada_dni.styleSheet() + "border: 2px solid #ff0000;"
                )
                return

            except (ValueError, RuntimeError, sqlite3.Error) as e:
                self.label_error.setText(str(e))
                alerta_error(self, "Error al iniciar sesiÃ³n", str(e))
                return

            if usuario is None:
                self.label_error.setText("Usuario o contrasena incorrectos.")
                self.entrada_dni.setStyleSheet(
                    self.entrada_dni.styleSheet() + "border: 2px solid #ff0000;"
                )
                return

            # Resetear estilos de error
            self.entrada_dni.setStyleSheet("")
            self.entrada_password.setStyleSheet("")
            self.label_error.clear()

            if self.al_loguear:
                self.al_loguear(usuario)

        except Exception as e:
            # Red de seguridad: ningun error de login puede cerrar la app.
            self.label_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

    def _volver(self):
        if self.al_volver:
            self.al_volver()

