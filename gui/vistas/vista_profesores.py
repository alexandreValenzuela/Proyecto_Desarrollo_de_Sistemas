"""
Vista "Ver Profesores": listado del personal con su cargo y nivel de permisos.
Solo un administrador (nivel 10) puede cambiar el cargo de una fila.
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QTableWidget, QTableWidgetItem,
                                QHeaderView, QPushButton, QInputDialog)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito
from models.personal import Personal
from models.cargo import Cargo
from auth.permisos import PermisoDenegadoError, tiene_permiso

# Cambiar el cargo de un miembro del personal es tarea de administrador.
NIVEL_MINIMO = 10


class VistaProfesores(QWidget):

    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        # Titulo
        lbl = QLabel("Listado de Profesores")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 50px;")
        layout.addWidget(lbl)

        # Barra de busqueda
        layout_busqueda = QHBoxLayout()
        layout_busqueda.setSpacing(20)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por Nombre, Apellido o DNI...")
        self.txt_buscar.setMinimumSize(440, 45)
        self.txt_buscar.setStyleSheet("font-size: 18px;")
        self.txt_buscar.textChanged.connect(self.cargar_datos)
        layout_busqueda.addWidget(self.txt_buscar)

        layout_busqueda.addStretch()
        layout.addLayout(layout_busqueda)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Nombre", "Apellido", "Cargo", "Nivel"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(800, 400)
        layout.addWidget(self.tabla)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_cambiar = QPushButton("Cambiar Cargo")
        btn_cambiar.setObjectName("FilterButton")
        btn_cambiar.setMinimumSize(220, 60)
        btn_cambiar.setStyleSheet("font-size: 22px;")
        btn_cambiar.setCursor(Qt.PointingHandCursor)
        btn_cambiar.clicked.connect(self.cambiar_cargo)
        btn_cambiar.setVisible(self._tiene_acceso())
        btn_layout.addWidget(btn_cambiar)

        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setMinimumSize(220, 60)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        if self.on_volver:
            btn_volver.clicked.connect(self.on_volver)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

        self.cargar_datos()

    def _tiene_acceso(self):
        """Solo el administrador puede reasignar cargos."""
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def cargar_datos(self):
        texto = self.txt_buscar.text().strip().lower()

        try:
            filas = Personal.obtener_todos_detalle()
        except (ValueError, RuntimeError, sqlite3.Error) as e:
            alerta_error(self, "Error al cargar", str(e))
            return
        except Exception as e:
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)

        for row_idx, (dni, nombre, apellido, cargo, nivel) in enumerate(filas):
            if texto and texto not in f"{dni} {nombre} {apellido}".lower():
                continue

            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(dni)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(nombre))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(apellido))
            self.tabla.setItem(row_idx, 3, QTableWidgetItem(cargo))
            self.tabla.setItem(row_idx, 4, QTableWidgetItem(str(nivel)))

    def cambiar_cargo(self):
        # Defensa en profundidad: el handler vuelve a validar antes de escribir.
        if not self._tiene_acceso():
            alerta_error(
                self, "Permiso denegado",
                "No tenés permisos para cambiar cargos."
            )
            return

        try:
            cargos = Cargo.obtener_todos()
        except (ValueError, RuntimeError, sqlite3.Error) as e:
            alerta_error(self, "Error al cargar cargos", str(e))
            return

        nombres = [c.cargo for c in cargos]

        dni_texto, ok = QInputDialog.getText(
            self, "Cambiar cargo",
            "DNI del personal:"
        )
        if not ok or not dni_texto.strip():
            return

        try:
            dni = int(dni_texto.strip())
        except ValueError:
            alerta_error(self, "Error", "El DNI debe contener solamente números.")
            return

        nombre, nuevo_nombre, ok2 = QInputDialog.getItem(
            self, "Cambiar cargo", f"Nuevo cargo para DNI {dni}:",
            nombres, 0, False
        )
        if not ok2 or not nombre:
            return

        cargo_id = next(c.cargo_id for c in cargos if c.cargo == nombre)

        try:
            Personal.asignar_cargo(self.usuario, dni, cargo_id)

        except (PermisoDenegadoError, ValueError, RuntimeError,
                sqlite3.Error) as e:
            alerta_error(self, "Error al asignar cargo", str(e))
            return

        except Exception as e:
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", f"Cargo de DNI {dni} actualizado a {nombre}.")
        self.cargar_datos()