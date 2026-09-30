"""
Vista "Mis Notas" (solo alumno): lectura de las propias notas por materia.
Siempre filtra por el DNI del usuario logueado: un alumno nunca ve notas
de otro alumno.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                                QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error
from models.nota import Nota


class VistaMisNotas(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._construir_interfaz()
        self.cargar_datos()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        lbl = QLabel("Mis Notas")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        lbl_ayuda = QLabel("Calificaciones por materia.")
        lbl_ayuda.setAlignment(Qt.AlignCenter)
        lbl_ayuda.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 18px;
            color: #000000;
            background: transparent;
        """)
        layout.addWidget(lbl_ayuda)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Materia", "Nota", "Comentario"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(700, 400)
        layout.addWidget(self.tabla)

    def cargar_datos(self):
        dni = self.usuario.get("dni")

        try:
            notas = Nota.obtener_por_alumno(dni)
        except RuntimeError as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar notas", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)
        self.lbl_error.clear()

        for row_idx, nota in enumerate(notas):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(nota.materia))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(nota.nota)))
            self.tabla.setItem(
                row_idx, 2, QTableWidgetItem(nota.comentario or "")
            )

        if not notas:
            self.lbl_error.setText("Todavía no tenés notas cargadas.")