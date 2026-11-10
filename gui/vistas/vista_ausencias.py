"""
Vista "Cargar / Ver Ausencias": dos modales intercambiables.

- "Ausencias recientes": lista de faltas con filtro por DNI, alta y
  justificacion (lista estilo tabla superior original).
- "Ausencias por alumno": listado filtrado de alumnos con sus conteos de
  faltas justificadas y sin justificar (lista estilo tabla inferior
  original), con alerta al superar LIMITE_INJUSTIFICADAS.

El modelo tiene UNIQUE(dni, fecha): guardar dos veces la misma fecha falla,
asi que el handler decide entre guardar() y actualizar() segun
Ausencia.existe(dni, fecha).
"""
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QCheckBox, QPushButton,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QDialog)
from PySide6.QtCore import Qt

from gui.componentes import alerta_error, alerta_exito, adjuntar_vista_previa_dni
from models.ausencia import Ausencia
from models.alumno import Alumno
from auth.permisos import tiene_permiso

# Cargar y justificar ausencias es tarea de un preceptor: Preceptor o superior.
NIVEL_MINIMO = 3

# Mas de este numero de faltas sin justificar enciende la alerta.
LIMITE_INJUSTIFICADAS = 5


class VistaAusencias(QWidget):
    """Ventana principal: lanza uno de los dos modales intercambiables."""

    def __init__(self, usuario, on_volver=None):
        super().__init__()
        self.usuario = usuario
        self.on_volver = on_volver
        self._construir_interfaz()

    # ========================================================================
    # INTERFAZ PRINCIPAL (launcher de modales)
    # ========================================================================

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Titulo
        lbl = QLabel("Cargar / Ver Ausencias")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 40px;")
        layout.addWidget(lbl)

        # Error global (se reutiliza si algun modal lo necesita, aunque cada
        # modal tiene el suyo propio).
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        # Dos botones para abrir los modales intercambiables.
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(30)

        btn_recientes = QPushButton("Ausencias recientes")
        btn_recientes.setObjectName("PrimaryButton")
        btn_recientes.setMinimumSize(260, 60)
        btn_recientes.setStyleSheet("font-size: 20px;")
        btn_recientes.setCursor(Qt.PointingHandCursor)
        btn_recientes.clicked.connect(self._abrir_recientes)
        btn_layout.addWidget(btn_recientes)

        btn_por_alumno = QPushButton("Ausencias por alumno")
        btn_por_alumno.setObjectName("SecondaryButton")
        btn_por_alumno.setMinimumSize(260, 60)
        btn_por_alumno.setStyleSheet("font-size: 20px;")
        btn_por_alumno.setCursor(Qt.PointingHandCursor)
        btn_por_alumno.clicked.connect(self._abrir_por_alumno)
        btn_layout.addWidget(btn_por_alumno)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # Boton volver
        btn_volver = QPushButton("Volver")
        btn_volver.setObjectName("DestructiveButton")
        btn_volver.setMinimumSize(250, 60)
        btn_volver.setStyleSheet("font-size: 25px;")
        btn_volver.setCursor(Qt.PointingHandCursor)
        if self.on_volver:
            btn_volver.clicked.connect(self.on_volver)
        layout.addWidget(btn_volver, alignment=Qt.AlignCenter)

    # ========================================================================
    # MODALES INTERCAMBIABLES
    # ========================================================================

    def _abrir_recientes(self):
        if not tiene_permiso(self.usuario, NIVEL_MINIMO):
            self.lbl_error.setText(
                "No tenés permisos para gestionar las ausencias."
            )
            alerta_error(
                self, "Permiso denegado",
                "No tenés permisos para gestionar las ausencias."
            )
            return
        modal = ModalAusenciasRecientes(self.usuario, parent=self)
        modal.exec()

    def _abrir_por_alumno(self):
        if not tiene_permiso(self.usuario, NIVEL_MINIMO):
            self.lbl_error.setText(
                "No tenés permisos para gestionar las ausencias."
            )
            alerta_error(
                self, "Permiso denegado",
                "No tenés permisos para gestionar las ausencias."
            )
            return
        modal = ModalAusenciasPorAlumno(self.usuario, parent=self)
        modal.exec()


# ============================================================================
# MODAL 1: AUSENCIAS RECIENTES (lista + carga + acciones)
# ============================================================================

class ModalAusenciasRecientes(QDialog):
    """Modal con la lista de ausencias (filtro por DNI) y el formulario de
    alta de una nueva ausencia."""

    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Ausencias recientes")
        self.setMinimumSize(900, 560)
        self.setModal(True)
        self._construir_interfaz()
        self.cargar_datos()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Titulo del modal
        lbl = QLabel("Ausencias recientes")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 30px;")
        layout.addWidget(lbl)

        # Fila de filtro por DNI + DNI preview.
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

        # Tabla de ausencias.
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["DNI", "Fecha", "Justificada", "Accion"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setMinimumSize(800, 300)
        layout.addWidget(self.tabla)

        # Fila de carga de nueva ausencia + DNI preview.
        layout.addLayout(self._fila_carga())
        self.lbl_preview_carga_dni = QLabel("")
        self.lbl_preview_carga_dni.setAlignment(Qt.AlignCenter)
        self.lbl_preview_carga_dni.setStyleSheet(
            "font-family: 'Cascadia Code', 'Consolas', monospace;"
            " font-size: 13px; background: transparent;"
        )
        layout.addWidget(self.lbl_preview_carga_dni)
        adjuntar_vista_previa_dni(
            self.entrada_dni, self.lbl_preview_carga_dni
        )

        # Error.
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        # Boton cerrar.
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("DestructiveButton")
        btn_cerrar.setMinimumSize(200, 45)
        btn_cerrar.setStyleSheet("font-size: 18px;")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(self.reject)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)

    # ---- filtro / carga filas ----

    def _fila_filtro(self):
        """Filtro por DNI: vacio = todas las ausencias."""
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
        self.entrada_dni.setMinimumSize(180, 45)
        self.entrada_dni.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_dni)

        fila.addWidget(self._label("Fecha"))
        self.entrada_fecha = QLineEdit()
        self.entrada_fecha.setPlaceholderText("AAAA-MM-DD")
        self.entrada_fecha.setMinimumSize(180, 45)
        self.entrada_fecha.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.entrada_fecha)

        self.check_justificada = QCheckBox("Justificada")
        self.check_justificada.setStyleSheet("font-size: 18px;")
        fila.addWidget(self.check_justificada)

        btn_guardar = QPushButton("Guardar ausencia")
        btn_guardar.setObjectName("PrimaryButton")
        btn_guardar.setMinimumSize(220, 45)
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
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def _sin_permiso(self):
        if self._tiene_acceso():
            return False
        self.lbl_error.setText("No tenés permisos para gestionar las ausencias.")
        alerta_error(
            self, "Permiso denegado",
            "No tenés permisos para gestionar las ausencias."
        )
        return True

    # ========================================================================
    # CARGA DE DATOS (lista de ausencias recientes)
    # ========================================================================

    def cargar_datos(self):
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
        self.lbl_error.clear()

        for row_idx, ausencia in enumerate(ausencias):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(ausencia.dni)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(ausencia.fecha))
            self.tabla.setItem(
                row_idx, 2,
                QTableWidgetItem("Si" if ausencia.justificada else "No")
            )
            self.tabla.setCellWidget(row_idx, 3, self._botones_accion(ausencia))

    # ========================================================================
    # ALTA / JUSTIFICACION / BAJA
    # ========================================================================

    def _guardar_ausencia(self):
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


# ============================================================================
# MODAL 2: AUSENCIAS POR ALUMNO (conteos por alumno + filtro)
# ============================================================================

class ModalAusenciasPorAlumno(QDialog):
    """Modal con el listado de alumnos y sus conteos de faltas, con filtro
    por DNI y alerta al superar el limite de faltas sin justificar."""

    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Ausencias por alumno")
        self.setMinimumSize(900, 560)
        self.setModal(True)
        self._construir_interfaz()
        self.cargar_datos()

    def _construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        lbl = QLabel("Ausencias por alumno")
        lbl.setObjectName("SectionTitle")
        lbl.setStyleSheet("font-size: 30px;")
        layout.addWidget(lbl)

        # Fila de filtro por DNI + DNI preview.
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

        # Subtitulo de conteos.
        lbl_conteos = QLabel(
            f"Conteos por alumno (alerta: más de "
            f"{LIMITE_INJUSTIFICADAS} faltas sin justificar)"
        )
        lbl_conteos.setObjectName("ResumenTitulo")
        lbl_conteos.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_conteos)

        # Tabla de conteos por alumno.
        self.tabla_conteos = QTableWidget()
        self.tabla_conteos.setColumnCount(5)
        self.tabla_conteos.setHorizontalHeaderLabels(
            ["DNI", "Alumno", "Justificadas", "Sin justificar", "Estado"]
        )
        self.tabla_conteos.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tabla_conteos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_conteos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_conteos.setMaximumHeight(340)
        layout.addWidget(self.tabla_conteos)

        # Error.
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(
            "color: #ff0000; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.lbl_error)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("DestructiveButton")
        btn_cerrar.setMinimumSize(200, 45)
        btn_cerrar.setStyleSheet("font-size: 18px;")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(self.reject)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)

    def _fila_filtro(self):
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
        btn_refrescar.clicked.connect(self.cargar_datos)
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

    # ========================================================================
    # ACCESO
    # ========================================================================

    def _tiene_acceso(self):
        return tiene_permiso(self.usuario, NIVEL_MINIMO)

    def _sin_permiso(self):
        if self._tiene_acceso():
            return False
        self.lbl_error.setText("No tenés permisos para gestionar las ausencias.")
        alerta_error(
            self, "Permiso denegado",
            "No tenés permisos para gestionar las ausencias."
        )
        return True

    # ========================================================================
    # CARGA DE DATOS (conteos por alumno)
    # ========================================================================

    def cargar_datos(self):
        if not self._tiene_acceso():
            self.tabla_conteos.setRowCount(0)
            self.lbl_error.setText("No tenés permisos para gestionar las ausencias.")
            return

        dni_filtro = self.entrada_filtro.text().strip()

        try:
            ausencias = Ausencia.obtener_todas()
        except (ValueError, RuntimeError, sqlite3.Error):
            self.tabla_conteos.setRowCount(0)
            return
        except Exception:
            self.tabla_conteos.setRowCount(0)
            return

        conteo = {}
        for ausencia in ausencias:
            if dni_filtro and str(ausencia.dni) != dni_filtro:
                continue
            entrada = conteo.setdefault(
                ausencia.dni, {"justificadas": 0, "injustificadas": 0}
            )
            if ausencia.justificada:
                entrada["justificadas"] += 1
            else:
                entrada["injustificadas"] += 1

        self.tabla_conteos.setRowCount(0)
        self.lbl_error.clear()

        for row_idx, dni in enumerate(sorted(conteo)):
            datos = conteo[dni]
            en_alerta = datos["injustificadas"] > LIMITE_INJUSTIFICADAS

            self.tabla_conteos.insertRow(row_idx)
            self.tabla_conteos.setItem(
                row_idx, 0, QTableWidgetItem(str(dni))
            )
            self.tabla_conteos.setItem(
                row_idx, 1, QTableWidgetItem(self._alumno_nombre(dni))
            )
            self.tabla_conteos.setItem(
                row_idx, 2, QTableWidgetItem(str(datos["justificadas"]))
            )
            self.tabla_conteos.setItem(
                row_idx, 3, QTableWidgetItem(str(datos["injustificadas"]))
            )

            estado = QTableWidgetItem("Alerta" if en_alerta else "OK")
            if en_alerta:
                estado.setForeground(Qt.red)
            self.tabla_conteos.setItem(row_idx, 4, estado)

    def _alumno_nombre(self, dni):
        try:
            alumno = Alumno.obtener_por_dni(dni)
        except (ValueError, RuntimeError, sqlite3.Error):
            return "DNI desconocido"
        if alumno is None:
            return "DNI desconocido"
        return f"{alumno.nombre} {alumno.apellido}"