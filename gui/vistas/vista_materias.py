"""
Vista "Crear / Ver Materias": catalogo de materias.

Cada materia pertenece a un curso (NxGy). Se puede filtrar por año (N1..N6)
y por especialidad (G1/G3 = Computacion, G2/G4 = Gestion y Administracion de las Organizaciones).
Se pueden agregar materias (solo nombre y curso, sin descripciones ni demas campos).
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QPushButton,
                                QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

from gui.componentes import (alerta_error, alerta_exito, SectionTitle,
                              PrimaryButton, SecondaryButton, FilterButton,
                              DestructiveButton)
from models.materia import Materia, nivel_de_curso, especialidad_de_curso, ESPECIALIDADES
from models.curso import Curso
from auth.permisos import tiene_permiso

# Gestionar materias es tarea de personal (Preceptor o superior).
NIVEL_MINIMO = 3

ANIOS = ["N1", "N2", "N3", "N4", "N5", "N6"]


class VistaMaterias(QWidget):
    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()
        self._poblar_cursos()
        self.cargar_datos()

    # ========================================================================
    # INTERFAZ
    # ========================================================================

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Titulo
        lbl = SectionTitle("Crear / Ver Materias", 40)
        layout.addWidget(lbl)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        # Fila de filtro: año y especialidad.
        layout.addLayout(self._fila_filtro())

        # Tabla de materias.
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Materia", "Curso", "Anio", "Especialidad", "Accion"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(800, 300)
        layout.addWidget(self.tabla)

        # Formulario de alta (solo nombre y curso, nada mas).
        lbl_alta = QLabel("Agregar materia")
        lbl_alta.setObjectName("ResumenLinea")
        lbl_alta.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-top: 14px;"
        )
        layout.addWidget(lbl_alta)

        form = QHBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(10)

        self.entrada_nombre = QLineEdit()
        self.entrada_nombre.setPlaceholderText("Nombre de la materia")
        self.entrada_nombre.setMinimumSize(260, 45)
        self.entrada_nombre.setStyleSheet("font-size: 18px;")
        form.addWidget(self.entrada_nombre)

        self.combo_curso = QComboBox()
        self.combo_curso.setMinimumSize(200, 45)
        self.combo_curso.setStyleSheet("font-size: 18px;")
        form.addWidget(self.combo_curso)

        btn_agregar = PrimaryButton("Agregar materia", self._agregar, 18)
        btn_agregar.setMinimumSize(180, 45)
        form.addWidget(btn_agregar)

        layout.addLayout(form)

        # Botones de navegacion.
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_volver = DestructiveButton("Volver", self.on_volver, 25)
        btn_volver.setMinimumSize(220, 55)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

    def _fila_filtro(self):
        """Filtro por año (N1..N6) y especialidad (Computacion / Gestion)."""
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        lbl_anio = QLabel("Anio")
        lbl_anio.setAlignment(Qt.AlignCenter)
        lbl_anio.setStyleSheet(
            "font-family: 'Cascadia Code', 'Consolas', monospace;"
            " font-size: 18px; color: #000000; background: transparent;"
        )
        fila.addWidget(lbl_anio)

        self.combo_anio = QComboBox()
        self.combo_anio.addItems(["Todos"] + ANIOS)
        self.combo_anio.setMinimumSize(130, 45)
        self.combo_anio.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.combo_anio)

        lbl_esp = QLabel("Especialidad")
        lbl_esp.setAlignment(Qt.AlignCenter)
        lbl_esp.setStyleSheet(
            "font-family: 'Cascadia Code', 'Consolas', monospace;"
            " font-size: 18px; color: #000000; background: transparent;"
        )
        fila.addWidget(lbl_esp)

        self.combo_especialidad = QComboBox()
        self.combo_especialidad.addItems(["Todas"] + list(ESPECIALIDADES))
        self.combo_especialidad.setMinimumSize(260, 45)
        self.combo_especialidad.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.combo_especialidad)

        btn_filtrar = FilterButton("Filtrar", self.cargar_datos, 18)
        btn_filtrar.setMinimumSize(140, 45)
        fila.addWidget(btn_filtrar)

        btn_refrescar = SecondaryButton("Refrescar", self._refrescar, 18)
        btn_refrescar.setMinimumSize(140, 45)
        fila.addWidget(btn_refrescar)

        return fila

    def _refrescar(self):
        self._poblar_cursos()
        self.cargar_datos()

    def _poblar_cursos(self):
        """Llena el combo de cursos al agregar una materia nueva."""
        seleccion = self.combo_curso.currentData()
        self.combo_curso.clear()
        self.combo_curso.addItem("Seleccionar curso", None)

        try:
            for c in Curso.obtener_todos():
                self.combo_curso.addItem(c.curso, c.curso_id)
        except RuntimeError:
            pass

        if seleccion is not None:
            indice = self.combo_curso.findData(seleccion)
            self.combo_curso.setCurrentIndex(indice if indice != -1 else 0)

    # ========================================================================
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def _sin_permiso(self):
        if self._tiene_acceso():
            return False
        self.lbl_error.setText("No tenés permisos para gestionar materias.")
        alerta_error(
            self, "Permiso denegado",
            "No tenés permisos para gestionar materias."
        )
        return True

    # ========================================================================
    # CARGA DE DATOS
    # ========================================================================

    def cargar_datos(self):
        if not self._tiene_acceso():
            self.tabla.setRowCount(0)
            self.lbl_error.setText("No tenés permisos para gestionar materias.")
            return

        anio = self.combo_anio.currentText().strip()
        especialidad = self.combo_especialidad.currentText().strip()

        nivel = None if anio == "Todos" else int(anio[1:])
        esp = None if especialidad == "Todas" else especialidad

        try:
            materias = Materia.obtener_por_filtro(nivel=nivel, especialidad=esp)
        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar materias", str(e))
            return
        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)
        self.lbl_error.clear()

        for row_idx, materia in enumerate(materias):
            try:
                curso = Curso.obtener_por_id(materia.curso_id)
                curso_texto = str(curso) if curso else "?"
                anio_texto = f"N{nivel_de_curso(curso_texto)}" \
                    if curso else "?"
                esp_texto = especialidad_de_curso(curso_texto) if curso else "?"
            except (ValueError, RuntimeError):
                curso_texto = "?"
                anio_texto = "?"
                esp_texto = "?"

            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(materia.nombre))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(curso_texto))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(anio_texto))
            self.tabla.setItem(row_idx, 3, QTableWidgetItem(esp_texto))
            self.tabla.setCellWidget(
                row_idx, 4, self._boton_eliminar(materia.materia_id)
            )

    def _boton_eliminar(self, materia_id):
        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        btn = QPushButton("Eliminar")
        btn.setObjectName("DestructiveButton")
        btn.setStyleSheet("font-size: 13px; padding: 3px 7px;")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _, m=materia_id: self._eliminar(m))
        layout.addWidget(btn)

        return contenedor

    def _agregar(self):
        if self._sin_permiso():
            return

        nombre = self.entrada_nombre.text().strip()
        curso_id = self.combo_curso.currentData()

        self.lbl_error.clear()

        if not nombre:
            self.lbl_error.setText("El nombre de la materia es obligatorio.")
            alerta_error(
                self, "Error al agregar",
                "El nombre de la materia es obligatorio."
            )
            return

        if curso_id is None:
            self.lbl_error.setText("Debe seleccionar un curso.")
            alerta_error(
                self, "Error al agregar", "Debe seleccionar un curso."
            )
            return

        try:
            nueva = Materia(nombre=nombre, curso_id=curso_id)
            nueva.guardar()
        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al agregar", str(e))
            return
        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", f"Materia '{nombre}' creada.")
        self.entrada_nombre.clear()
        self.combo_curso.setCurrentIndex(0)
        self.cargar_datos()

    def _eliminar(self, materia_id):
        if self._sin_permiso():
            return

        try:
            Materia.eliminar(materia_id)
        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al eliminar", str(e))
            return
        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", "Materia eliminada.")
        self.cargar_datos()
