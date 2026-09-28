"""
Vista de Autorizacion de Alumnos.
Lista alumnos pendientes (autorizado=0) y permite aprobarlos.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QPushButton, QMessageBox)
from PySide6.QtCore import Qt

from models.alumno import Alumno
from auth.permisos import PermisoDenegadoError


class VistaAutorizarAlumnos(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
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

        self._cargar_pendientes()

    def _cargar_pendientes(self):
        try:
            pendientes = Alumno.obtener_pendientes()
        except Exception as e:
            self.lbl_error.setText(str(e))
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
        try:
            Alumno.autorizar(self.usuario, dni)
        except (PermisoDenegadoError, RuntimeError) as e:
            self.lbl_error.setText(str(e))
            return

        QMessageBox.information(self, "Exito", f"Alumno DNI {dni} autorizado.")
        self.lbl_error.clear()
        self._cargar_pendientes()
