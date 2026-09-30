"""
Vista "Mis Ausencias" (solo alumno): lectura de las propias inasistencias.
Siempre filtra por el DNI del usuario logueado.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                                QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error
from models.ausencia import Ausencia


class VistaMisAusencias(QWidget):

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._construir_interfaz()
        self.cargar_datos()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        lbl = QLabel("Mis Ausencias")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        lbl_ayuda = QLabel("Tus inasistencias, con su estado de justificación.")
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
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(700, 400)
        layout.addWidget(self.tabla)

    def cargar_datos(self):
        dni = self.usuario.get("dni")

        try:
            ausencias = Ausencia.obtener_por_alumno(dni)
        except RuntimeError as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar ausencias", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)
        self.lbl_error.clear()

        for row_idx, ausencia in enumerate(ausencias):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(ausencia.fecha)))
            estado = "Justificada" if ausencia.justificada else "No justificada"
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(estado))

        if not ausencias:
            self.lbl_error.setText("No tenés ausencias registradas.")