"""
Vista "Mis Notas" (solo alumno): lectura de las propias notas por materia.
Siempre filtra por el DNI del usuario logueado: un alumno nunca ve notas
de otro alumno.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QComboBox)
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

        fila_filtro = QHBoxLayout()
        fila_filtro.setAlignment(Qt.AlignCenter)
        fila_filtro.setSpacing(15)

        lbl_materia = QLabel("Materia")
        lbl_materia.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 18px;
            color: #000000;
            background: transparent;
        """)
        fila_filtro.addWidget(lbl_materia)

        self.combo_materia = QComboBox()
        self.combo_materia.setMinimumSize(280, 45)
        self.combo_materia.setStyleSheet("font-size: 18px;")
        self.combo_materia.currentIndexChanged.connect(self.cargar_datos)
        fila_filtro.addWidget(self.combo_materia)

        layout.addLayout(fila_filtro)

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

        # Promedio general (siempre sobre todas las materias).
        self.lbl_promedio = QLabel("")
        self.lbl_promedio.setObjectName("ResumenLinea")
        self.lbl_promedio.setAlignment(Qt.AlignCenter)
        self.lbl_promedio.setStyleSheet(
            "font-size: 22px; font-weight: bold; margin-top: 8px;"
        )
        layout.addWidget(self.lbl_promedio)

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

        # Combo de materias, sin perder la seleccion actual. Se reconstruye
        # con signals bloqueadas para no re-disparar cargar_datos en loop.
        seleccion = self.combo_materia.currentText()
        self.combo_materia.blockSignals(True)
        self.combo_materia.clear()
        self.combo_materia.addItem("Todas las materias")
        for materia in sorted({n.materia for n in notas}):
            self.combo_materia.addItem(materia)
        indice = self.combo_materia.findText(seleccion)
        self.combo_materia.setCurrentIndex(indice if indice != -1 else 0)
        self.combo_materia.blockSignals(False)

        filtro = self.combo_materia.currentText().strip()
        if filtro and filtro != "Todas las materias":
            notas = [n for n in notas if n.materia == filtro]

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

        texto_promedio = self._texto_promedio(dni)
        self.lbl_promedio.setText(texto_promedio)

    def _texto_promedio(self, dni):
        try:
            promedio = Nota.promedio_por_alumno(dni)
        except RuntimeError:
            return ""

        if promedio is None:
            return "Promedio general: sin notas"

        return f"Promedio general: {promedio:.1f}"