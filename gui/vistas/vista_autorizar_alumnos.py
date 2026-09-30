"""
Vista de Autorizacion de Alumnos.
Lista alumnos pendientes (autorizado=0) y permite aprobarlos.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito
from models.alumno import Alumno
from auth.permisos import PermisoDenegadoError, tiene_permiso

# Mismo nivel que Alumno.NIVEL_MINIMO_PARA_AUTORIZAR (Preceptor o superior).
NIVEL_MINIMO = 3


class VistaAutorizarAlumnos(QWidget):

    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Titulo
        lbl = QLabel("Autorizacion de Alumnos")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 30px;")
        layout.addWidget(lbl)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        # Tabla de pendientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["DNI", "Nombre", "Apellido", "Accion"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Botones
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

        self._cargar_pendientes()

    def _cargar_pendientes(self):
        try:
            pendientes = Alumno.obtener_pendientes()
        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar pendientes", str(e))
            return

        self.tabla.setRowCount(0)

        if not pendientes:
            self.tabla.setRowCount(1)
            self.tabla.setItem(0, 0, QTableWidgetItem("No hay alumnos pendientes."))
            return

        for row_idx, (dni, nombre, apellido) in enumerate(pendientes):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(dni)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(nombre)))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(str(apellido)))

            btn = QPushButton("Autorizar")
            btn.setObjectName("PrimaryButton")
            btn.setStyleSheet("font-size: 14px; padding: 4px 8px;")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, d=dni: self._autorizar(d))
            self.tabla.setCellWidget(row_idx, 3, btn)

    def _autorizar(self, dni):
        # Defensa en profundidad: la vista se oculta para quien no llega a
        # NIVEL_MINIMO, pero el handler vuelve a validar antes de escribir.
        if not tiene_permiso(self.usuario, NIVEL_MINIMO):
            self.lbl_error.setText("No tenés permisos para autorizar alumnos.")
            alerta_error(
                self, "Permiso denegado",
                "No tenés permisos para autorizar alumnos."
            )
            return

        try:
            Alumno.autorizar(self.usuario, dni)

        except (PermisoDenegadoError, ValueError, RuntimeError,
                sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al autorizar", str(e))
            return

        except Exception as e:
            # Red de seguridad: ningun error puede cerrar la app.
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", f"Alumno DNI {dni} autorizado.")
        self.lbl_error.clear()
        self._cargar_pendientes()
