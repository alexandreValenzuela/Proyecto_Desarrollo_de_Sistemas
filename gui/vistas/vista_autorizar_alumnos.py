"""
Vista de Autorizacion de Alumnos.
Lista alumnos pendientes (autorizado=0) y, para cada uno, permite
autorizarlo (autorizado=1) o denegarle el acceso (autorizado=2) con
botones uno al lado del otro.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import (alerta_error, alerta_exito, SectionTitle,
                              DestructiveButton)
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
        lbl = SectionTitle("Autorizacion de Alumnos", 40)
        layout.addWidget(lbl)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        # Lista unica de alumnos pendientes (autorizado = 0).
        lbl_lista = QLabel("Alumnos pendientes de autorizacion")
        lbl_lista.setObjectName("ResumenLinea")
        lbl_lista.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-top: 10px;"
        )
        layout.addWidget(lbl_lista)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Nombre", "Apellido", "Autorizar", "Denegar"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_volver = DestructiveButton("Volver", self.on_volver, 25)
        btn_volver.setMinimumSize(220, 55)
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

            # Celda Accion: Autorizar y Denegar lado a lado.
            contenedor = QWidget()
            lay = QHBoxLayout(contenedor)
            lay.setContentsMargins(2, 2, 2, 2)
            lay.setSpacing(6)
            lay.setAlignment(Qt.AlignCenter)

            btn_autorizar = QPushButton("Autorizar")
            btn_autorizar.setObjectName("PrimaryButton")
            btn_autorizar.setStyleSheet("font-size: 13px; padding: 4px 8px;")
            btn_autorizar.setCursor(Qt.PointingHandCursor)
            btn_autorizar.clicked.connect(lambda _, d=dni: self._autorizar(d))
            lay.addWidget(btn_autorizar)

            btn_denegar = QPushButton("Denegar")
            btn_denegar.setObjectName("DestructiveButton")
            btn_denegar.setStyleSheet("font-size: 13px; padding: 4px 8px;")
            btn_denegar.setCursor(Qt.PointingHandCursor)
            btn_denegar.clicked.connect(lambda _, d=dni: self._denegar(d))
            lay.addWidget(btn_denegar)

            self.tabla.setCellWidget(row_idx, 3, contenedor)
            # Columna 4 (Denegar header) queda vacia; la accion esta en la 3.
            self.tabla.setItem(row_idx, 4, QTableWidgetItem(""))

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

    def _denegar(self, dni):
        # Defensa en profundidad: la vista se oculta para quien no llega a
        # NIVEL_MINIMO, pero el handler vuelve a validar antes de escribir.
        if not tiene_permiso(self.usuario, NIVEL_MINIMO):
            self.lbl_error.setText("No tenés permisos para denegar alumnos.")
            alerta_error(
                self, "Permiso denegado",
                "No tenés permisos para denegar alumnos."
            )
            return

        try:
            Alumno.denegar(self.usuario, dni)

        except (PermisoDenegadoError, ValueError, RuntimeError,
                sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al denegar", str(e))
            return

        except Exception as e:
            # Red de seguridad: ningun error puede cerrar la app.
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", f"Alumno DNI {dni} denegado.")
        self.lbl_error.clear()
        self._cargar_pendientes()