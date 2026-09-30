"""
Vista "Cargar / Ver Notas": grilla de notas con filtro por DNI y alta
o edicion de notas.

El modelo tiene UNIQUE(dni, materia): guardar dos veces la misma materia
falla, asi que el handler decide entre guardar() y actualizar() segun
Nota.existe(dni, materia).
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QTableWidget,
                                QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito
from models.nota import Nota
from auth.permisos import tiene_permiso

# Cargar y editar notas es tarea docente: Profesor o superior.
NIVEL_MINIMO = 5


class VistaNotas(QWidget):

    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()
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

        # Fila de carga
        layout.addLayout(self._fila_carga())

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Materia", "Nota", "Comentario", "Accion"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setFixedSize(1150, 420)
        layout.addWidget(self.tabla, alignment=Qt.AlignCenter)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setFixedSize(210, 60)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        if self.on_volver:
            btn_volver.clicked.connect(self.on_volver)
        btn_layout.addWidget(btn_volver)

        layout.addLayout(btn_layout)

    def _fila_filtro(self):
        """Filtro por DNI: vacio = todas las notas."""
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        lbl = self._label("DNI")
        fila.addWidget(lbl)

        self.entrada_filtro = QLineEdit()
        self.entrada_filtro.setPlaceholderText("DNI del alumno")
        self.entrada_filtro.setFixedSize(220, 45)
        self.entrada_filtro.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_filtro)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("FilterButton")
        btn_filtrar.setFixedSize(140, 45)
        btn_filtrar.setStyleSheet("font-size: 18px;")
        btn_filtrar.setCursor(Qt.PointingHandCursor)
        btn_filtrar.clicked.connect(self.cargar_datos)
        fila.addWidget(btn_filtrar)

        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.setObjectName("SecondaryButton")
        btn_refrescar.setFixedSize(140, 45)
        btn_refrescar.setStyleSheet("font-size: 18px;")
        btn_refrescar.setCursor(Qt.PointingHandCursor)
        btn_refrescar.clicked.connect(self.cargar_datos)
        fila.addWidget(btn_refrescar)

        return fila

    def _fila_carga(self):
        """Alta o edicion de una nota."""
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        fila.addWidget(self._label("DNI"))
        self.entrada_dni = QLineEdit()
        self.entrada_dni.setPlaceholderText("DNI")
        self.entrada_dni.setFixedSize(160, 45)
        self.entrada_dni.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_dni)

        fila.addWidget(self._label("Materia"))
        self.entrada_materia = QLineEdit()
        self.entrada_materia.setPlaceholderText("Materia")
        self.entrada_materia.setFixedSize(200, 45)
        self.entrada_materia.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_materia)

        fila.addWidget(self._label("Nota"))
        self.entrada_nota = QLineEdit()
        self.entrada_nota.setPlaceholderText(f"{Nota.NOTA_MINIMA}-{Nota.NOTA_MAXIMA}")
        self.entrada_nota.setFixedSize(90, 45)
        self.entrada_nota.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_nota)

        fila.addWidget(self._label("Comentario"))
        self.entrada_comentario = QLineEdit()
        self.entrada_comentario.setPlaceholderText("Opcional")
        self.entrada_comentario.setFixedSize(220, 45)
        self.entrada_comentario.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_comentario)

        btn_guardar = QPushButton("Guardar nota")
        btn_guardar.setObjectName("PrimaryButton")
        btn_guardar.setFixedSize(200, 45)
        btn_guardar.setStyleSheet("font-size: 18px;")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar_nota)
        fila.addWidget(btn_guardar)

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

    # ========================================================================
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def _sin_permiso(self):
        """Avisa el permiso denegado y devuelve True si no se puede seguir."""
        if self._tiene_acceso():
            return False

        self.lbl_error.setText("No tenés permisos para gestionar las notas.")
        alerta_error(
            self, "Permiso denegado",
            "No tenés permisos para gestionar las notas."
        )
        return True

    # ========================================================================
    # CARGA DE DATOS
    # ========================================================================

    def cargar_datos(self):
        # Defensa en profundidad: la seccion esta oculta y bloqueada para
        # quien no llega a NIVEL_MINIMO, pero la vista se construye siempre,
        # asi que la carga tambien valida. Sin modal: __init__ la invoca.
        if not self._tiene_acceso():
            self.tabla.setRowCount(0)
            self.lbl_error.setText("No tenés permisos para gestionar las notas.")
            return

        dni = self.entrada_filtro.text().strip()

        try:
            notas = Nota.obtener_por_alumno(dni) if dni else Nota.obtener_todas()

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar notas", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)

        if not notas:
            self.lbl_error.clear()
            return

        for row_idx, nota in enumerate(notas):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(nota.dni)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(nota.materia))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(str(nota.nota)))
            self.tabla.setItem(
                row_idx, 3, QTableWidgetItem(nota.comentario or "")
            )
            self.tabla.setCellWidget(row_idx, 4, self._botones_accion(nota))

        self.lbl_error.clear()

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
            lambda _, n=nota: self._cargar_en_formulario(n)
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

    def _cargar_en_formulario(self, nota):
        """Trae la nota al formulario para editarla y guardar."""
        self.entrada_dni.setText(str(nota.dni))
        self.entrada_materia.setText(nota.materia)
        self.entrada_nota.setText(str(nota.nota))
        self.entrada_comentario.setText(nota.comentario or "")

    # ========================================================================
    # ALTA / EDICION / BAJA
    # ========================================================================

    def _guardar_nota(self):
        # Defensa en profundidad: el handler vuelve a validar antes de escribir.
        if self._sin_permiso():
            return

        dni = self.entrada_dni.text().strip()
        materia = self.entrada_materia.text().strip()
        valor = self.entrada_nota.text().strip()
        comentario = self.entrada_comentario.text().strip()

        try:
            if not all([dni, materia, valor]):
                self.lbl_error.setText("DNI, materia y nota son obligatorios.")
                alerta_error(
                    self, "Error al guardar",
                    "DNI, materia y nota son obligatorios."
                )
                return

            # UNIQUE(dni, materia): si ya existe, se actualiza en el lugar.
            existente = self._buscar_existente(dni, materia)

            if existente is not None:
                # int() aca: validar_datos() compara contra el rango y una
                # cadena tiraria TypeError en vez de ValueError.
                existente.nota = int(valor)
                existente.comentario = comentario or None
                existente.actualizar()
                mensaje = f"Nota de {materia} actualizada."
            else:
                nuevo = Nota(
                    dni=dni,
                    materia=materia,
                    nota=valor,
                    comentario=comentario
                )
                nuevo.guardar()
                mensaje = f"Nota de {materia} guardada."

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al guardar", str(e))
            return

        except Exception as e:
            # Red de seguridad: ningun error puede cerrar la app.
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", mensaje)
        self._limpiar_formulario()
        self.cargar_datos()

    def _buscar_existente(self, dni, materia):
        """Devuelve la Nota ya cargada, o None si todavia no existe."""
        if not Nota.existe(dni, materia):
            return None

        for candidata in Nota.obtener_por_alumno(dni):
            if candidata.materia == materia:
                return candidata

        return None

    def _eliminar(self, nota_id):
        # Defensa en profundidad: el handler vuelve a validar antes de borrar.
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

    def _limpiar_formulario(self):
        self.entrada_dni.clear()
        self.entrada_materia.clear()
        self.entrada_nota.clear()
        self.entrada_comentario.clear()
        self.lbl_error.clear()
