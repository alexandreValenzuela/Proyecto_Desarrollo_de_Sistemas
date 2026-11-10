"""
Vista "Ver Alumnos": tabla interactiva con filtros en tiempo real.
Filtra por DNI, Nombre/Apellido y Curso usando Alumno.buscar_filtrado().
Permite editar los datos de un alumno (menos DNI y contrasena) y cambiar
su estado de acceso (Autorizado / Pendiente / Denegado).
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QTableWidget,
                                QTableWidgetItem, QHeaderView, QPushButton,
                                QDialog, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import Qt

from models.alumno import Alumno
from models.curso import Curso
from gui.componentes import alerta_error, alerta_exito


class ModalEditarAlumno(QDialog):
    """Modal para editar los datos de un alumno.

    No permite editar el DNI (clave primaria) ni la contrasena
    (esa se cambia desde su propio menu).
    """

    ESTADOS = [
        (1, "Autorizado"),
        (0, "Pendiente de autorizacion"),
        (2, "Denegado"),
    ]

    def __init__(self, dni, parent=None):
        super().__init__(parent)
        self.dni = dni
        self.setWindowTitle(f"Editar alumno DNI {dni}")
        self.setMinimumSize(560, 520)
        self.setModal(True)
        self._construir_interfaz()
        self._precargar()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        titulo = QLabel(f"Edicion de alumno - DNI {self.dni}")
        titulo.setObjectName("SectionTitle")
        titulo.setStyleSheet("font-size: 30px;")
        layout.addWidget(titulo)

        form = QVBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(12)

        self.lbl_dni = QLabel(str(self.dni))
        self.lbl_dni.setStyleSheet(
            "font-family: 'Cascadia Code', monospace; font-size: 18px;"
        )
        form.addLayout(self._campo("DNI (no editable)", self.lbl_dni))

        self.entrada_nombre = QLineEdit()
        self.entrada_nombre.setMinimumSize(300, 45)
        self.entrada_nombre.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Nombre", self.entrada_nombre))

        self.entrada_apellido = QLineEdit()
        self.entrada_apellido.setMinimumSize(300, 45)
        self.entrada_apellido.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Apellido", self.entrada_apellido))

        self.entrada_direccion = QLineEdit()
        self.entrada_direccion.setMinimumSize(300, 45)
        self.entrada_direccion.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Direccion", self.entrada_direccion))

        self.entrada_telefono = QLineEdit()
        self.entrada_telefono.setMinimumSize(300, 45)
        self.entrada_telefono.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Telefono", self.entrada_telefono))

        self.entrada_fecha = QLineEdit()
        self.entrada_fecha.setPlaceholderText("AAAA-MM-DD")
        self.entrada_fecha.setMinimumSize(300, 45)
        self.entrada_fecha.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Fecha de nacimiento", self.entrada_fecha))

        self.combo_curso = QComboBox()
        self.combo_curso.addItem("Seleccionar curso", None)
        self.combo_curso.setMinimumSize(300, 45)
        self.combo_curso.setStyleSheet("font-size: 18px;")
        self._poblar_cursos()
        form.addLayout(self._campo("Curso", self.combo_curso))

        self.combo_estado = QComboBox()
        for valor, texto in self.ESTADOS:
            self.combo_estado.addItem(texto, valor)
        self.combo_estado.setMinimumSize(300, 45)
        self.combo_estado.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Estado de acceso", self.combo_estado))

        layout.addLayout(form)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        btns.button(QDialogButtonBox.Save).setText("Guardar cambios")
        btns.button(QDialogButtonBox.Save).setObjectName("PrimaryButton")
        btns.button(QDialogButtonBox.Save).setMinimumSize(160, 45)
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        btns.button(QDialogButtonBox.Cancel).setObjectName("DestructiveButton")
        btns.button(QDialogButtonBox.Cancel).setMinimumSize(160, 45)
        btns.accepted.connect(self._guardar)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns, alignment=Qt.AlignCenter)

    def _campo(self, etiqueta, widget):
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(8)
        lbl = QLabel(etiqueta)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 18px; color: #000000; background: transparent;
        """)
        lbl.setMinimumWidth(110)
        fila.addWidget(lbl)
        fila.addWidget(widget)
        return fila

    def _poblar_cursos(self):
        try:
            for c in Curso.obtener_todos():
                self.combo_curso.addItem(c.curso, c.curso_id)
        except Exception:
            pass

    def _precargar(self):
        try:
            alumno = Alumno.obtener_por_dni(self.dni)
        except (ValueError, RuntimeError):
            return
        if alumno is None:
            return
        self.entrada_nombre.setText(alumno.nombre)
        self.entrada_apellido.setText(alumno.apellido)
        self.entrada_direccion.setText(alumno.direccion or "")
        self.entrada_telefono.setText(alumno.telefono or "")
        self.entrada_fecha.setText(alumno.fecha_nacimiento or "")
        if alumno.curso_id is not None:
            idx = self.combo_curso.findData(alumno.curso_id)
            self.combo_curso.setCurrentIndex(
                idx if idx != -1 else 0
            )
        idx = self.combo_estado.findData(alumno.autorizado)
        self.combo_estado.setCurrentIndex(
            idx if idx != -1 else 0
        )

    def _guardar(self):
        nombre = self.entrada_nombre.text().strip()
        apellido = self.entrada_apellido.text().strip()
        direccion = self.entrada_direccion.text().strip()
        telefono = self.entrada_telefono.text().strip()
        fecha = self.entrada_fecha.text().strip()
        curso_id = self.combo_curso.currentData()
        autorizado = self.combo_estado.currentData()

        self.lbl_error.clear()

        if not all([nombre, apellido, direccion, telefono, fecha, curso_id]):
            self.lbl_error.setText("Todos los campos son obligatorios.")
            alerta_error(
                self, "Error al guardar",
                "Todos los campos son obligatorios."
            )
            return

        try:
            alumno = Alumno.obtener_por_dni(self.dni)
            if alumno is None:
                raise ValueError("No se encontro el alumno.")
            alumno.nombre = nombre
            alumno.apellido = apellido
            alumno.direccion = direccion
            alumno.telefono = telefono
            alumno.fecha_nacimiento = fecha
            alumno.curso_id = curso_id
            alumno.autorizado = int(autorizado)
            alumno.actualizar()
        except (ValueError, RuntimeError) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al guardar", str(e))
            return

        alerta_exito(self, "Exito", "Alumno actualizado correctamente.")
        self.accept()


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
        self.txt_buscar.setMinimumSize(400, 45)
        self.txt_buscar.setStyleSheet("font-size: 18px;")
        self.txt_buscar.textChanged.connect(self.cargar_datos)

        self.cmb_cursos = QComboBox()
        self.cmb_cursos.addItem("Todos los Cursos", 0)
        self.cmb_cursos.setMinimumSize(200, 45)
        self.cmb_cursos.setStyleSheet("font-size: 18px;")
        self._poblar_combo_cursos()
        self.cmb_cursos.currentIndexChanged.connect(self.cargar_datos)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("FilterButton")
        btn_filtrar.setMinimumSize(140, 45)
        btn_filtrar.setStyleSheet("font-size: 20px;")
        btn_filtrar.setCursor(Qt.PointingHandCursor)
        btn_filtrar.clicked.connect(self.cargar_datos)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("DestructiveButton")
        btn_limpiar.setMinimumSize(140, 45)
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
        self.tabla.setMinimumSize(800, 400)
        layout.addWidget(self.tabla)

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

            if aut_val == 1:
                estado = "Autorizado"
            elif aut_val == 2:
                estado = "Denegado"
            else:
                estado = "Pendiente"
            self.tabla.setItem(row_idx, 4, QTableWidgetItem(estado))

            contenedor = QWidget()
            lay = QHBoxLayout(contenedor)
            lay.setContentsMargins(4, 4, 4, 4)
            lay.setSpacing(4)
            lay.setAlignment(Qt.AlignCenter)

            btn_editar = QPushButton("Editar")
            btn_editar.setObjectName("FilterButton")
            btn_editar.setStyleSheet("font-size: 14px; padding: 4px 8px;")
            btn_editar.setCursor(Qt.PointingHandCursor)
            btn_editar.clicked.connect(
                lambda _, d=dni_val: self._editar_alumno(d)
            )
            lay.addWidget(btn_editar)

            self.tabla.setCellWidget(row_idx, 5, contenedor)

    def _editar_alumno(self, dni):
        modal = ModalEditarAlumno(dni, parent=self)
        if modal.exec() == QDialog.Accepted:
            self.cargar_datos()

    def _limpiar_filtros(self):
        self.txt_buscar.clear()
        self.cmb_cursos.setCurrentIndex(0)
        self.cargar_datos()

    def _volver_al_menu(self):
        if self._menu_callback:
            self._menu_callback()
