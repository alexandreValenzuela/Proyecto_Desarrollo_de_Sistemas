"""
Vista "Cambiar Contraseña": self-service para cualquier usuario logueado y
reseteo por parte de un administrador (nivel 10).

- Cualquier usuario cambia su propia contrasena conociendo la actual.
- Un administrador puede resetear la contrasena de personal o de alumno
  sin conocer la actual.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito
from models.personal import Personal
from models.alumno import Alumno
from auth.permisos import tiene_permiso

NIVEL_ADMIN = 10


class VistaCambiarPassword(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._construir_interfaz()

    # ========================================================================
    # INTERFAZ
    # ========================================================================

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl = QLabel("Cambiar Contraseña")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        # Cambio propio
        layout.addWidget(self._titulo_seccion("CAMBIAR MI CONTRASEÑA"))
        layout.addLayout(self._fila_formulario("Contraseña actual", "actual"))
        layout.addLayout(self._fila_formulario("Contraseña nueva", "nueva"))
        layout.addLayout(
            self._fila_formulario("Repetir contraseña nueva", "confirmar")
        )

        self.btn_cambiar = QPushButton("Cambiar mi contraseña")
        self.btn_cambiar.setObjectName("PrimaryButton")
        self.btn_cambiar.setMinimumSize(280, 50)
        self.btn_cambiar.setStyleSheet("font-size: 18px;")
        self.btn_cambiar.setCursor(Qt.PointingHandCursor)
        self.btn_cambiar.clicked.connect(self._cambiar_mi_password)
        layout.addWidget(self.btn_cambiar, alignment=Qt.AlignCenter)

        # Reseteo por administrador
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        self.panel_admin = QWidget()
        layout_admin = QVBoxLayout(self.panel_admin)
        layout_admin.setContentsMargins(0, 8, 0, 0)
        layout_admin.setSpacing(12)

        layout_admin.addWidget(self._titulo_seccion(
            "RESETEAR CONTRASEÑA (SOLO ADMINISTRADOR)"
        ))
        layout_admin.addLayout(
            self._fila_formulario("DNI del usuario", "dni_reset")
        )
        layout_admin.addLayout(
            self._fila_formulario("Contraseña nueva", "nueva_reset")
        )
        layout_admin.addLayout(
            self._fila_formulario("Repetir contraseña nueva", "confirmar_reset")
        )

        self.btn_resetear = QPushButton("Resetear contraseña")
        self.btn_resetear.setObjectName("SecondaryButton")
        self.btn_resetear.setMinimumSize(280, 50)
        self.btn_resetear.setStyleSheet("font-size: 18px;")
        self.btn_resetear.setCursor(Qt.PointingHandCursor)
        self.btn_resetear.clicked.connect(self._resetear_password)
        layout_admin.addWidget(self.btn_resetear, alignment=Qt.AlignCenter)

        layout.addWidget(self.panel_admin)

        self.panel_admin.setVisible(
            tiene_permiso(self.usuario, NIVEL_ADMIN)
        )

        layout.addStretch()

    def _titulo_seccion(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("ResumenTitulo")
        return lbl

    def _fila_formulario(self, etiqueta, atributo):
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        lbl = self._label(etiqueta)
        fila.addWidget(lbl)

        entrada = QLineEdit()
        entrada.setEchoMode(QLineEdit.Password)
        entrada.setMinimumSize(280, 45)
        entrada.setStyleSheet("font-size: 18px;")
        fila.addWidget(entrada)

        setattr(self, f"entrada_{atributo}", entrada)

        return fila

    def _label(self, texto):
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setMinimumWidth(220)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 16px;
            color: #000000;
            background: transparent;
        """)
        return lbl

    def _error(self, mensaje):
        self.lbl_error.setText(mensaje)
        alerta_error(self, "Error", mensaje)

    # ========================================================================
    # CAMBIO POR EL PROPIO USUARIO
    # ========================================================================

    def _cambiar_mi_password(self):
        dni = self.usuario.get("dni")
        actual = self.entrada_actual.text()
        nueva = self.entrada_nueva.text()
        confirmar = self.entrada_confirmar.text()

        if not all([dni, actual, nueva, confirmar]):
            self._error("Completá todos los campos.")
            return

        if nueva != confirmar:
            self._error("La contraseña nueva no coincide en ambos campos.")
            return

        try:
            if self.usuario.get("tipo") == "alumno":
                Alumno.cambiar_password(dni, actual, nueva)
            else:
                Personal.cambiar_password(dni, actual, nueva)

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self._error(str(e))
            return

        except Exception as e:
            self._error(str(e))
            return

        self.lbl_error.clear()
        self.entrada_actual.clear()
        self.entrada_nueva.clear()
        self.entrada_confirmar.clear()
        alerta_exito(self, "Exito", "Contraseña actualizada.")

    # ========================================================================
    # RESETEO POR ADMINISTRADOR
    # ========================================================================

    def _resetear_password(self):
        if not tiene_permiso(self.usuario, NIVEL_ADMIN):
            self._error("Necesitás ser administrador para resetear contraseñas.")
            return

        dni = self.entrada_dni_reset.text().strip()
        nueva = self.entrada_nueva_reset.text()
        confirmar = self.entrada_confirmar_reset.text()

        if not all([dni, nueva, confirmar]):
            self._error("Completá todos los campos.")
            return

        if nueva != confirmar:
            self._error("La contraseña nueva no coincide en ambos campos.")
            return

        try:
            if Personal.resetear_password(dni, nueva) is None:
                if Alumno.resetear_password(dni, nueva) is None:
                    raise ValueError(
                        "No existe un usuario con ese DNI en el sistema."
                    )

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self._error(str(e))
            return

        except Exception as e:
            self._error(str(e))
            return

        self.lbl_error.clear()
        self.entrada_dni_reset.clear()
        self.entrada_nueva_reset.clear()
        self.entrada_confirmar_reset.clear()
        alerta_exito(self, "Exito", f"Contraseña de {dni} reseteada.")