"""
Vista "Cargar / Ver Ausencias": grilla de faltas con filtro por DNI, alta
y justificacion.

El modelo tiene UNIQUE(dni, fecha): guardar dos veces la misma fecha falla,
asi que el handler decide entre guardar() y actualizar() segun
Ausencia.existe(dni, fecha).
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QCheckBox, QPushButton,
                                QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito
from models.ausencia import Ausencia
from auth.permisos import tiene_permiso

# Cargar y justificar ausencias es tarea de unpreceptor: Preceptor o superior.
NIVEL_MINIMO = 3


class VistaAusencias(QWidget):

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
        lbl = QLabel("Ausencias por Alumno")
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
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Fecha", "Justificada", "Accion"]
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
        """Filtro por DNI: vacio = todas las ausencias."""
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
        """Alta de una ausencia."""
        fila = QHBoxLayout()
        fila.setAlignment(Qt.AlignCenter)
        fila.setSpacing(15)

        fila.addWidget(self._label("DNI"))
        self.entrada_dni = QLineEdit()
        self.entrada_dni.setPlaceholderText("DNI")
        self.entrada_dni.setFixedSize(180, 45)
        self.entrada_dni.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_dni)

        fila.addWidget(self._label("Fecha"))
        self.entrada_fecha = QLineEdit()
        self.entrada_fecha.setPlaceholderText("AAAA-MM-DD")
        self.entrada_fecha.setFixedSize(180, 45)
        self.entrada_fecha.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_fecha)

        self.check_justificada = QCheckBox("Justificada")
        self.check_justificada.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.check_justificada)

        btn_guardar = QPushButton("Guardar ausencia")
        btn_guardar.setObjectName("PrimaryButton")
        btn_guardar.setFixedSize(220, 45)
        btn_guardar.setStyleSheet("font-size: 18px;")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar_ausencia)
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
    # CARGA DE DATOS
    # ========================================================================

    # ========================================================================
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def _sin_permiso(self):
        """Avisa el permiso denegado y devuelve True si no se puede seguir."""
        if self._tiene_acceso():
            return False

        self.lbl_error.setText("No tenés permisos para gestionar las ausencias.")
        alerta_error(
            self, "Permiso denegado",
            "No tenés permisos para gestionar las ausencias."
        )
        return True

    def cargar_datos(self):
        # Defensa en profundidad: la seccion esta oculta y bloqueada para
        # quien no llega a NIVEL_MINIMO, pero la vista se construye siempre,
        # asi que la carga tambien valida. Sin modal: __init__ la invoca.
        if not self._tiene_acceso():
            self.tabla.setRowCount(0)
            self.lbl_error.setText("No tenés permisos para gestionar las ausencias.")
            return

        dni = self.entrada_filtro.text().strip()

        try:
            ausencias = (
                Ausencia.obtener_por_alumno(dni) if dni
                else Ausencia.obtener_todas()
            )

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al cargar ausencias", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        self.tabla.setRowCount(0)

        for row_idx, ausencia in enumerate(ausencias):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(ausencia.dni)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(ausencia.fecha))
            self.tabla.setItem(
                row_idx, 2,
                QTableWidgetItem("Si" if ausencia.justificada else "No")
            )
            self.tabla.setCellWidget(row_idx, 3, self._botones_accion(ausencia))

        self.lbl_error.clear()

    def _botones_accion(self, ausencia):
        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        texto_toggle = "Desjustificar" if ausencia.justificada else "Justificar"

        btn_toggle = QPushButton(texto_toggle)
        btn_toggle.setObjectName("FilterButton")
        btn_toggle.setStyleSheet("font-size: 14px; padding: 4px 8px;")
        btn_toggle.setCursor(Qt.PointingHandCursor)
        btn_toggle.clicked.connect(
            lambda _, i=ausencia.ausencia_id: self._alternar_justificada(i)
        )
        layout.addWidget(btn_toggle)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setObjectName("DestructiveButton")
        btn_eliminar.setStyleSheet("font-size: 14px; padding: 4px 8px;")
        btn_eliminar.setCursor(Qt.PointingHandCursor)
        btn_eliminar.clicked.connect(
            lambda _, i=ausencia.ausencia_id: self._eliminar(i)
        )
        layout.addWidget(btn_eliminar)

        return contenedor

    # ========================================================================
    # ALTA / JUSTIFICACION / BAJA
    # ========================================================================

    def _guardar_ausencia(self):
        # Defensa en profundidad: el handler vuelve a validar antes de escribir.
        if self._sin_permiso():
            return

        dni = self.entrada_dni.text().strip()
        fecha = self.entrada_fecha.text().strip()
        justificada = self.check_justificada.isChecked()

        try:
            if not all([dni, fecha]):
                self.lbl_error.setText("DNI y fecha son obligatorios.")
                alerta_error(
                    self, "Error al guardar",
                    "DNI y fecha son obligatorios."
                )
                return

            # UNIQUE(dni, fecha): si ya existe, se actualiza en el lugar.
            if Ausencia.existe(dni, fecha):
                existente = Ausencia.obtener_por_id(
                    self._buscar_id(dni, fecha)
                )
                existente.justificada = justificada
                existente.actualizar()
                mensaje = f"Ausencia del {fecha} actualizada."
            else:
                nueva = Ausencia(
                    dni=dni, fecha=fecha, justificada=justificada
                )
                nueva.guardar()
                mensaje = f"Ausencia del {fecha} guardada."

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

    def _buscar_id(self, dni, fecha):
        for candidata in Ausencia.obtener_por_alumno(dni):
            if candidata.fecha == fecha:
                return candidata.ausencia_id

        raise ValueError("No se encontró la ausencia indicada.")

    def _alternar_justificada(self, ausencia_id):
        # Defensa en profundidad: el handler vuelve a validar antes de escribir.
        if self._sin_permiso():
            return

        try:
            ausencia = Ausencia.obtener_por_id(ausencia_id)
            ausencia.justificada = not ausencia.justificada
            ausencia.actualizar()

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al actualizar", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        estado = "justificada" if ausencia.justificada else "no justificada"
        alerta_exito(self, "Exito", f"Ausencia del {ausencia.fecha} {estado}.")
        self.cargar_datos()

    def _eliminar(self, ausencia_id):
        # Defensa en profundidad: el handler vuelve a validar antes de borrar.
        if self._sin_permiso():
            return

        try:
            Ausencia.eliminar(ausencia_id)

        except (ValueError, RuntimeError, sqlite3.Error) as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error al eliminar", str(e))
            return

        except Exception as e:
            self.lbl_error.setText(str(e))
            alerta_error(self, "Error inesperado", str(e))
            return

        alerta_exito(self, "Exito", "Ausencia eliminada.")
        self.cargar_datos()

    def _limpiar_formulario(self):
        self.entrada_dni.clear()
        self.entrada_fecha.clear()
        self.check_justificada.setChecked(False)
        self.lbl_error.clear()
