"""
Vista "Historial de Accesos": tabla de intentos de inicio de sesion con
filtro por DNI.

Cada intento (exitoso o fallido) queda registrado en la tabla accesos.
Ver el historial es tarea de un profesor o superior.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QTableWidget,
                                QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error
from models.acceso import Acceso
from auth.permisos import tiene_permiso

NIVEL_MINIMO = 5


class VistaAccesos(QWidget):

    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()
        self.cargar_datos()

    # ========================================================================
    # INTERFAZ
    # ========================================================================

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        lbl = QLabel("Historial de Accesos")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        layout.addLayout(self._fila_filtro())

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(
            ["Fecha y hora", "DNI", "Estado"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(800, 420)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setMinimumSize(250, 60)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        if self.on_volver:
            btn_volver.clicked.connect(self.on_volver)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

    def _fila_filtro(self):
        """Filtro por DNI: vacio = todos los accesos."""
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        lbl = self._label("DNI")
        fila.addWidget(lbl)

        self.entrada_filtro = QLineEdit()
        self.entrada_filtro.setPlaceholderText("DNI del usuario")
        self.entrada_filtro.setMinimumSize(220, 45)
        self.entrada_filtro.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_filtro)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("FilterButton")
        btn_filtrar.setMinimumSize(140, 45)
        btn_filtrar.setStyleSheet("font-size: 18px;")
        btn_filtrar.setCursor(Qt.PointingHandCursor)
        btn_filtrar.clicked.connect(self.cargar_datos)
        fila.addWidget(btn_filtrar)

        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.setObjectName("SecondaryButton")
        btn_refrescar.setMinimumSize(140, 45)
        btn_refrescar.setStyleSheet("font-size: 18px;")
        btn_refrescar.setCursor(Qt.PointingHandCursor)
        btn_refrescar.clicked.connect(self.cargar_datos)
        fila.addWidget(btn_refrescar)

        return fila

    def _label(self, texto):
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 18px;
            color: #000000;
            background: transparent;
        """)
        return lbl

    # ========================================================================
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    # ========================================================================
    # CARGA DE DATOS
    # ========================================================================

    def cargar_datos(self):
        if not self._tiene_acceso():
            self.tabla.setRowCount(0)
            self.lbl_error.setText(
                "No tenés permisos para ver el historial de accesos."
            )
            return

        dni = self.entrada_filtro.text().strip()

        try:
            filas = (
                Acceso.historial_por_dni(dni) if dni
                else Acceso.historial()
            )

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar accesos", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)
        self.lbl_error.clear()

        for row_idx, fila in enumerate(filas):
            _, dni_fila, fecha_hora, exitoso = fila
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(fecha_hora)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(dni_fila)))
            estado = QTableWidgetItem("Exitoso" if exitoso else "Fallido")
            if not exitoso:
                estado.setForeground(Qt.red)
            self.tabla.setItem(row_idx, 2, estado)

        if not filas:
            self.lbl_error.setText("No hay accesos registrados.")