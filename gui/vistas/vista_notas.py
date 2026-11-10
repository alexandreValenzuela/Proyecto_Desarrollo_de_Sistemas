"""
Vista "Cargar / Ver Notas": grilla de notas con filtro por DNI y materia,
boletin por bimestre y modal de alta/edicion de notas.

El modelo tiene UNIQUE(dni, materia, bimestre): guardar dos veces la misma
materia para el mismo bimestre falla, asi que el handler decide entre
guardar() y actualizar() segun Nota.existe(dni, materia, bimestre).
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QPushButton,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QDialog, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import Qt

from gui.componentes import (
    alerta_error, alerta_exito, adjuntar_vista_previa_dni
)
from models.nota import Nota
from auth.permisos import tiene_permiso

# Cargar y editar notas es tarea docente: Profesor o superior.
NIVEL_MINIMO = 5


class ModalNota(QDialog):
    """
    Modal para alta o edicion de una nota.

    Si se pasa una Nota existente, se abre precargada y al guardar se llama
    a actualizar(). Si no, se abre vacia y al guardar se llama a guardar().
    """

    def __init__(self, usuario, nota=None, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.nota = nota  # None = alta, Nota = edicion
        self.setWindowTitle(
            "Editar nota" if nota is not None else "Agregar nota"
        )
        self.setMinimumSize(620, 420)
        self.setModal(True)
        self._construir_interfaz()
        if nota is not None:
            self._precargar(nota)

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        titulo = QLabel(
            "Edicion de nota" if self.nota is not None else "Nueva nota"
        )
        titulo.setObjectName("SectionTitle")
        titulo.setStyleSheet("font-size: 30px;")
        layout.addWidget(titulo)

        form = QVBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(12)

        self.entrada_dni = QLineEdit()
        self.entrada_dni.setPlaceholderText("DNI del alumno")
        self.entrada_dni.setMinimumSize(300, 45)
        self.entrada_dni.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("DNI", self.entrada_dni))

        self.lbl_previa_dni = QLabel("")
        self.lbl_previa_dni.setAlignment(Qt.AlignCenter)
        form.addWidget(self.lbl_previa_dni)
        adjuntar_vista_previa_dni(self.entrada_dni, self.lbl_previa_dni)

        self.entrada_materia = QLineEdit()
        self.entrada_materia.setPlaceholderText("Materia")
        self.entrada_materia.setMinimumSize(300, 45)
        self.entrada_materia.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Materia", self.entrada_materia))

        self.combo_bimestre = QComboBox()
        self.combo_bimestre.addItems([
            "Bimestre 1", "Bimestre 2", "Bimestre 3", "Bimestre 4"
        ])
        self.combo_bimestre.setMinimumSize(200, 45)
        self.combo_bimestre.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Bimestre", self.combo_bimestre))

        self.entrada_nota = QLineEdit()
        self.entrada_nota.setPlaceholderText(
            f"{Nota.NOTA_MINIMA}-{Nota.NOTA_MAXIMA}"
        )
        self.entrada_nota.setMinimumSize(120, 45)
        self.entrada_nota.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Nota", self.entrada_nota))

        self.entrada_comentario = QLineEdit()
        self.entrada_comentario.setPlaceholderText("Comentario (opcional)")
        self.entrada_comentario.setMinimumSize(300, 45)
        self.entrada_comentario.setStyleSheet("font-size: 18px;")
        form.addLayout(self._campo("Comentario", self.entrada_comentario))

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
        btns.button(QDialogButtonBox.Save).setText("Guardar nota")
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
        lbl.setMinimumWidth(90)
        fila.addWidget(lbl)
        fila.addWidget(widget)
        return fila

    def _precargar(self, nota):
        self.entrada_dni.setText(str(nota.dni))
        self.entrada_materia.setText(nota.materia)
        self.combo_bimestre.setCurrentText(f"Bimestre {nota.bimestre}")
        self.entrada_nota.setText(str(nota.nota))
        self.entrada_comentario.setText(nota.comentario or "")
        self.lbl_previa_dni.setText("")

    def _guardar(self):
        dni = self.entrada_dni.text().strip()
        materia = self.entrada_materia.text().strip()
        valor = self.entrada_nota.text().strip()
        comentario = self.entrada_comentario.text().strip()
        bimestre_texto = self.combo_bimestre.currentText().strip()
        bimestre = int(bimestre_texto.split()[-1])

        self.lbl_error.clear()

        if not all([dni, materia, valor]):
            self.lbl_error.setText(
                "DNI, materia, bimestre y nota son obligatorios."
            )
            alerta_error(
                self, "Error al guardar",
                "DNI, materia, bimestre y nota son obligatorios."
            )
            return

        try:
            if self.nota is not None:
                # Edicion: actualizar en el lugar.
                self.nota.dni = int(dni)
                self.nota.materia = materia
                self.nota.nota = int(valor)
                self.nota.comentario = comentario or None
                self.nota.bimestre = bimestre
                self.nota.actualizar()
                mensaje = f"Nota de {materia} (bimestre {bimestre}) actualizada."
            else:
                # Alta: si ya existe, actualizar en el lugar.
                if Nota.existe(dni, materia, bimestre):
                    existente = None
                    for candidata in Nota.obtener_por_alumno_bimestre(
                        dni, bimestre
                    ):
                        if candidata.materia == materia:
                            existente = candidata
                            break
                    if existente is not None:
                        existente.nota = int(valor)
                        existente.comentario = comentario or None
                        existente.actualizar()
                        mensaje = (
                            f"Nota de {materia} (bimestre {bimestre}) "
                            "actualizada."
                        )
                    else:
                        mensaje = "No se encontro la nota existente."
                else:
                    nueva = Nota(
                        dni=dni, materia=materia, nota=valor,
                        comentario=comentario, bimestre=bimestre
                    )
                    nueva.guardar()
                    mensaje = (
                        f"Nota de {materia} (bimestre {bimestre}) guardada."
                    )

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al guardar", str(e))
            return
        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", mensaje)
        self.accept()


class VistaNotas(QWidget):
    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()
        self._poblar_materias()
        self.cargar_datos()

    # ========================================================================
    # INTERFAZ
    # ========================================================================

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Titulo
        lbl = QLabel("Notas por Alumno")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        # Fila de filtro
        layout.addLayout(self._fila_filtro())

        self.lbl_preview_filtro_dni = QLabel("")
        self.lbl_preview_filtro_dni.setAlignment(Qt.AlignCenter)
        self.lbl_preview_filtro_dni.setStyleSheet(
            "font-family: 'Cascadia Code', 'Consolas', monospace;"
            " font-size: 13px; background: transparent;"
        )
        layout.addWidget(self.lbl_preview_filtro_dni)
        adjuntar_vista_previa_dni(
            self.entrada_filtro, self.lbl_preview_filtro_dni
        )

        # Boton agregar nota (reemplaza el formulario inline anterior)
        btn_agregar = QPushButton("Agregar nota")
        btn_agregar.setObjectName("PrimaryButton")
        btn_agregar.setMinimumSize(200, 45)
        btn_agregar.setStyleSheet("font-size: 18px;")
        btn_agregar.setCursor(Qt.PointingHandCursor)
        btn_agregar.clicked.connect(self._abrir_modal_nota)
        layout.addWidget(btn_agregar, alignment=Qt.AlignCenter)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        # Boletin del alumno filtrado por DNI
        self.lbl_boletin = QLabel("")
        self.lbl_boletin.setObjectName("ResumenLinea")
        self.lbl_boletin.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_boletin)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Materia", "Nota", "Comentario", "Accion"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(800, 360)
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

    def _fila_filtro(self):
        """Filtro por DNI, materia y bimestre: vacios = todas las notas."""
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        lbl = self._label("DNI")
        fila.addWidget(lbl)

        self.entrada_filtro = QLineEdit()
        self.entrada_filtro.setPlaceholderText("DNI del alumno")
        self.entrada_filtro.setMinimumSize(220, 45)
        self.entrada_filtro.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_filtro)

        fila.addWidget(self._label("Materia"))
        self.combo_materia = QComboBox()
        self.combo_materia.setMinimumSize(220, 45)
        self.combo_materia.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.combo_materia)

        fila.addWidget(self._label("Bimestre"))
        self.combo_bimestre_filtro = QComboBox()
        self.combo_bimestre_filtro.addItems(["Todos", "Bimestre 1", "Bimestre 2",
                                              "Bimestre 3", "Bimestre 4"])
        self.combo_bimestre_filtro.setMinimumSize(200, 45)
        self.combo_bimestre_filtro.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.combo_bimestre_filtro)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("FilterButton")
        btn_filtrar.setMinimumSize(140, 45)
        btn_filtrar.setStyleSheet("font-size: 18px;")
        btn_filtrar.setCursor(Qt.PointingHandCursor)
        btn_filtrar.clicked.connect(self.cargar_datos)
        fila.addWidget(btn_filtrar)

        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.setObjectName("SecondaryButton")
        btn_refrescar.setMinimumSize(140, 45)
        btn_refrescar.setStyleSheet("font-size: 18px;")
        btn_refrescar.setCursor(Qt.PointingHandCursor)
        btn_refrescar.clicked.connect(self._refrescar)
        fila.addWidget(btn_refrescar)

        return fila

    def _label(self, texto):
        lbl = QLabel(texto)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("""
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 18px;
            color: #000000;
            background: transparent;
        """)
        return lbl

    def _refrescar(self):
        self._poblar_materias()
        self.cargar_datos()

    def _poblar_materias(self):
        """Llena el combo con las materias existentes, sin perder la
        seleccion actual si esa materia sigue estando."""
        seleccion = self.combo_materia.currentText()
        self.combo_materia.clear()
        self.combo_materia.addItem("Todas las materias")

        try:
            for materia in Nota.obtener_materias():
                self.combo_materia.addItem(materia)
        except RuntimeError:
            pass

        indice = self.combo_materia.findText(seleccion)
        self.combo_materia.setCurrentIndex(
            indice if indice != -1 else 0
        )

    # ========================================================================
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def _sin_permiso(self):
        if self._tiene_acceso():
            return False
        self.lbl_error.setText("No tenés permisos para gestionar las notas.")
        alerta_error(
            self, "Permiso denegado",
            "No tenés permisos para gestionar las notas."
        )
        return True

    # ========================================================================
    # MODAL DE NOTA
    # ========================================================================

    def _abrir_modal_nota(self, nota=None):
        """Abre el modal de nota vacia (alta) o precargada (edicion)."""
        if not self._tiene_acceso():
            return
        modal = ModalNota(self.usuario, nota=nota, parent=self)
        if modal.exec() == QDialog.Accepted:
            self.cargar_datos()

    # ========================================================================
    # CARGA DE DATOS
    # ========================================================================

    def cargar_datos(self):
        if not self._tiene_acceso():
            self.tabla.setRowCount(0)
            self.lbl_boletin.clear()
            self.lbl_error.setText("No tenés permisos para gestionar las notas.")
            return

        dni = self.entrada_filtro.text().strip()
        materia = self.combo_materia.currentText().strip()
        bimestre_texto = self.combo_bimestre_filtro.currentText().strip()

        try:
            if dni:
                if bimestre_texto == "Todos":
                    notas = Nota.obtener_por_alumno(dni)
                else:
                    bimestre = int(bimestre_texto.split()[-1])
                    notas = Nota.obtener_por_alumno_bimestre(dni, bimestre)
            else:
                notas = Nota.obtener_todas()

            if materia and materia != "Todas las materias":
                notas = [n for n in notas if n.materia == materia]

            if bimestre_texto and bimestre_texto != "Todos":
                bimestre = int(bimestre_texto.split()[-1])
                notas = [n for n in notas if n.bimestre == bimestre]

        except (ValueError, RuntimeError, sqlite3.Error) as e:
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
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(nota.dni)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(nota.materia))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(str(nota.nota)))
            self.tabla.setItem(
                row_idx, 3, QTableWidgetItem(nota.comentario or "")
            )
            self.tabla.setCellWidget(row_idx, 4, self._botones_accion(nota))

        self._actualizar_boletin(dni)
        self.lbl_error.clear()

    def _actualizar_boletin(self, dni):
        """Resumen del alumno filtrado: notas del bimestre seleccionado,
        promedio del bimestre y promedio general."""
        if not dni:
            self.lbl_boletin.clear()
            return

        bimestre_texto = self.combo_bimestre_filtro.currentText().strip()

        try:
            if bimestre_texto == "Todos":
                notas_dni = Nota.obtener_por_alumno(dni)
                promedio = Nota.promedio_por_alumno(dni)
                etiqueta = "todos los bimestres"
            else:
                bimestre = int(bimestre_texto.split()[-1])
                notas_dni = Nota.obtener_por_alumno_bimestre(dni, bimestre)
                promedio = Nota.promedio_por_alumno_bimestre(dni, bimestre)
                etiqueta = f"bimestre {bimestre}"

            promedio_general = Nota.promedio_por_alumno(dni)
        except RuntimeError:
            self.lbl_boletin.clear()
            return

        texto_promedio = (
            f"Promedio {promedio:.1f}"
            if promedio is not None
            else "sin notas"
        )
        texto_general = (
            f"Promedio general: {promedio_general:.1f}"
            if promedio_general is not None
            else "sin notas generales"
        )

        detalle = " · ".join(
            f"{n.materia} {n.nota}" for n in notas_dni
        )

        self.lbl_boletin.setText(
            f"Boletín de {dni} ({etiqueta}): {detalle} → {texto_promedio} | "
            f"{texto_general}" if detalle
            else f"Boletín de {dni} ({etiqueta}): {texto_promedio} | "
            f"{texto_general}"
        )

    def _botones_accion(self, nota):
        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setObjectName("FilterButton")
        btn_actualizar.setStyleSheet("font-size: 14px; padding: 4px 8px;")
        btn_actualizar.setCursor(Qt.PointingHandCursor)
        btn_actualizar.clicked.connect(
            lambda _, n=nota: self._abrir_modal_nota(n)
        )
        layout.addWidget(btn_actualizar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setObjectName("DestructiveButton")
        btn_eliminar.setStyleSheet("font-size: 14px; padding: 4px 8px;")
        btn_eliminar.setCursor(Qt.PointingHandCursor)
        btn_eliminar.clicked.connect(
            lambda _, i=nota.nota_id: self._eliminar(i)
        )
        layout.addWidget(btn_eliminar)

        return contenedor

    def _eliminar(self, nota_id):
        if self._sin_permiso():
            return
        try:
            Nota.eliminar(nota_id)
        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al eliminar", str(e))
            return
        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return
        alerta_exito(self, "Exito", "Nota eliminada.")
        self.cargar_datos()