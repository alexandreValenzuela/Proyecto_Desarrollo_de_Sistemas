"""
Vista "Ver Alumnos": tabla interactiva con filtros en tiempo real.
Filtra por DNI, Nombre/Apellido y Curso usando Alumno.buscar_filtrado().
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QTableWidget,
                                QTableWidgetItem, QHeaderView, QPushButton)
from PySide6.QtCore import Qt

from models.alumno import Alumno
from models.curso import Curso


class VistaVerAlumnos(QWidget):

    def __init__(self):
        super().__init__()
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        # Titulo
        lbl = QLabel("Listado de Alumnos")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 50px;")
        layout.addWidget(lbl)

        # Barra de busqueda y filtros
        layout_filtros = QHBoxLayout()
        layout_filtros.setSpacing(20)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por Nombre o DNI...")
        self.txt_buscar.setFixedSize(500, 45)
        self.txt_buscar.setStyleSheet("font-size: 18px;")
        self.txt_buscar.textChanged.connect(self.cargar_datos)

        self.cmb_cursos = QComboBox()
        self.cmb_cursos.addItem("Todos los Cursos", 0)
        self.cmb_cursos.setFixedSize(200, 45)
        self.cmb_cursos.setStyleSheet("font-size: 18px;")
        self._poblar_combo_cursos()
        self.cmb_cursos.currentIndexChanged.connect(self.cargar_datos)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("FilterButton")
        btn_filtrar.setFixedSize(140, 45)
        btn_filtrar.setStyleSheet("font-size: 20px;")
        btn_filtrar.setCursor(Qt.PointingHandCursor)
        btn_filtrar.clicked.connect(self.cargar_datos)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("DestructiveButton")
        btn_limpiar.setFixedSize(120, 45)
        btn_limpiar.setStyleSheet("font-size: 18px;")
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_limpiar.clicked.connect(self._limpiar_filtros)

        layout_filtros.addWidget(self.txt_buscar)
        layout_filtros.addWidget(self.cmb_cursos)
        layout_filtros.addWidget(btn_filtrar)
        layout_filtros.addWidget(btn_limpiar)
        layout.addLayout(layout_filtros)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Nombre", "Apellido", "Curso", "Estado", "Accion"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setFixedSize(1200, 520)
        layout.addWidget(self.tabla, alignment=Qt.AlignCenter)

        # Boton volver
        layout_volver = QHBoxLayout()
        layout_volver.setAlignment(Qt.AlignRight)
        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setFixedSize(180, 55)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.clicked.connect(self._volver_al_menu)
        layout_volver.addWidget(btn_volver)
        layout.addLayout(layout_volver)

        self._menu_callback = None

    def set_menu_callback(self, callback):
        self._menu_callback = callback

    def _poblar_combo_cursos(self):
        try:
            cursos = Curso.obtener_todos()
            for c in cursos:
                self.cmb_cursos.addItem(c.curso, c.curso_id)
        except Exception:
            pass

    def cargar_datos(self):
        texto_buscar = self.txt_buscar.text()
        id_curso = self.cmb_cursos.currentData()

        # Busqueda unificada por nombre o DNI
        registros = Alumno.buscar_filtrado(
            dni=texto_buscar if texto_buscar.isdigit() else None,
            nombre=None if texto_buscar.isdigit() else texto_buscar,
            id_curso=id_curso
        )

        self.tabla.setRowCount(0)
        for row_idx, row_data in enumerate(registros):
            self.tabla.insertRow(row_idx)
            dni_val, nom_val, ape_val, curso_val, aut_val = row_data

            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(dni_val)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(nom_val)))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(str(ape_val)))
            self.tabla.setItem(
                row_idx, 3,
                QTableWidgetItem(str(curso_val) if curso_val else "Sin Asignar")
            )

            estado = "Autorizado" if aut_val == 1 else "Pendiente"
            self.tabla.setItem(row_idx, 4, QTableWidgetItem(estado))

            self.tabla.setItem(row_idx, 5, QTableWidgetItem(""))

    def _limpiar_filtros(self):
        self.txt_buscar.clear()
        self.cmb_cursos.setCurrentIndex(0)
        self.cargar_datos()

    def _volver_al_menu(self):
        if self._menu_callback:
            self._menu_callback()
