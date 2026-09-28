"""
Ventana Principal de NeoED — Menu Centralizado + Dashboard con Sidebar.

Hibrida segun ambas especificaciones:
- Menu Principal: botones centrados (Draw.io SSOT)
- Dashboard interno: Sidebar fijo + QStackedWidget (Spec 1)

Flujo:
  Menu Principal (botones centrados)
    └─ click seccion → Dashboard (Sidebar + vistas apiladas)
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QStackedWidget, QFrame, QLabel, QPushButton)
from PySide6.QtCore import Qt

from gui.componentes import (HeaderTitleLabel, PrimaryButton, SecondaryButton,
                              DestructiveButton)
from gui.vistas.vista_bienvenido import VistaBienvenido
from gui.vistas.vista_ver_alumnos import VistaVerAlumnos
from gui.vistas.vista_cargar_alumnos import VistaCargarAlumnos
from gui.vistas.vista_autorizar_alumnos import VistaAutorizarAlumnos
from gui.vistas.vista_registrar_personal import VistaRegistrarPersonal
from gui.vistas.vista_placeholder import VistaPlaceholder


class VentanaPrincipal(QMainWindow):

    def __init__(self, usuario, on_logout_callback=None):
        super().__init__()
        self.usuario = usuario
        self.on_logout_callback = on_logout_callback

        self.setWindowTitle("NeoED - Sistema de Gestion Escolar")
        self.setFixedSize(1600, 900)
        self.setObjectName("CanvasBase")

        # Stack global: [0] = Menu Centralizado, [1] = Dashboard Sidebar
        self.stack_global = QStackedWidget()
        self.setCentralWidget(self.stack_global)

        self._crear_menu_central()
        self._crear_dashboard_sidebar()

        self.stack_global.setCurrentIndex(0)

    # ========================================================================
    # MENU CENTRALIZADO (Draw.io SSOT — spec 5.3)
    # ========================================================================

    def _crear_menu_central(self):
        menu_widget = QWidget()
        menu_widget.setObjectName("CanvasBase")
        layout = QVBoxLayout(menu_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(28)

        # Titulo
        layout.addWidget(HeaderTitleLabel("NeoED", 60))

        layout.addSpacing(40)

        # Botones del menu
        btn_crear = PrimaryButton("Crear Alumno", lambda: self.stack_global.setCurrentIndex(1), 40)
        btn_crear.setFixedSize(400, 85)
        contenedor_btn = QHBoxLayout()
        contenedor_btn.setAlignment(Qt.AlignCenter)
        contenedor_btn.addWidget(btn_crear)
        layout.addLayout(contenedor_btn)

        btn_ver = SecondaryButton("Ver Alumnos", lambda: self._abrir_seccion(1), 40)
        btn_ver.setFixedSize(400, 85)
        contenedor_btn2 = QHBoxLayout()
        contenedor_btn2.setAlignment(Qt.AlignCenter)
        contenedor_btn2.addWidget(btn_ver)
        layout.addLayout(contenedor_btn2)

        btn_autorizar = SecondaryButton("Autorizar Alumnos", lambda: self._abrir_seccion(3), 40)
        btn_autorizar.setFixedSize(400, 85)
        contenedor_btn3 = QHBoxLayout()
        contenedor_btn3.setAlignment(Qt.AlignCenter)
        contenedor_btn3.addWidget(btn_autorizar)
        layout.addLayout(contenedor_btn3)

        btn_personal = SecondaryButton("Registrar Personal", lambda: self._abrir_seccion(4), 40)
        btn_personal.setFixedSize(400, 85)
        contenedor_btn4 = QHBoxLayout()
        contenedor_btn4.setAlignment(Qt.AlignCenter)
        contenedor_btn4.addWidget(btn_personal)
        layout.addLayout(contenedor_btn4)

        layout.addStretch()

        self.stack_global.addWidget(menu_widget)  # Index 0

    # ========================================================================
    # DASHBOARD CON SIDEBAR (Spec 1 — QStackedWidget interno)
    # ========================================================================

    def _crear_dashboard_sidebar(self):
        dashboard = QWidget()
        dashboard.setObjectName("DashboardContainer")
        layout = QHBoxLayout(dashboard)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = self._crear_sidebar()
        layout.addWidget(sidebar)

        # Stack de vistas
        self.stack_vistas = QStackedWidget()
        layout.addWidget(self.stack_vistas)

        # Instanciar vistas
        self.vista_bienvenido = VistaBienvenido(self.usuario)
        self.vista_ver_alumnos = VistaVerAlumnos()
        self.vista_cargar_alumnos = VistaCargarAlumnos(
            on_guardado=self._refrescar_tabla_alumnos
        )
        self.vista_autorizar = VistaAutorizarAlumnos(self.usuario)
        self.vista_registrar_personal = VistaRegistrarPersonal(self.usuario)
        self.vista_placeholder = VistaPlaceholder("Profesores — Modulo en mantenimiento")

        self.stack_vistas.addWidget(self.vista_bienvenido)             # 0
        self.stack_vistas.addWidget(self.vista_ver_alumnos)            # 1
        self.stack_vistas.addWidget(self.vista_cargar_alumnos)         # 2
        self.stack_vistas.addWidget(self.vista_autorizar)              # 3
        self.stack_vistas.addWidget(self.vista_registrar_personal)     # 4
        self.stack_vistas.addWidget(self.vista_placeholder)            # 5

        self.stack_vistas.setCurrentIndex(0)

        self.stack_global.addWidget(dashboard)  # Index 1

    def _crear_sidebar(self):
        frame = QFrame()
        frame.setObjectName("SidebarFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        # Header
        lbl_logo = QLabel("NeoED Admin")
        lbl_logo.setObjectName("SidebarHeader")
        layout.addWidget(lbl_logo)

        # Grupo Alumnos
        layout.addWidget(self._label_grupo("ALUMNOS"))

        btn_ver = QPushButton("Ver Alumnos")
        btn_ver.setObjectName("BtnSidebarItem")
        btn_ver.setCheckable(True)
        btn_ver.clicked.connect(lambda: self._navegar_vista(1))
        layout.addWidget(btn_ver)

        btn_cargar = QPushButton("Cargar Alumnos")
        btn_cargar.setObjectName("BtnSidebarItem")
        btn_cargar.setCheckable(True)
        btn_cargar.clicked.connect(lambda: self._navegar_vista(2))
        layout.addWidget(btn_cargar)

        # Grupo Personal
        layout.addWidget(self._label_grupo("PERSONAL"))

        btn_autorizar = QPushButton("Autorizar Alumnos")
        btn_autorizar.setObjectName("BtnSidebarItem")
        btn_autorizar.setCheckable(True)
        btn_autorizar.clicked.connect(lambda: self._navegar_vista(3))
        layout.addWidget(btn_autorizar)

        btn_registrar = QPushButton("Registrar Personal")
        btn_registrar.setObjectName("BtnSidebarItem")
        btn_registrar.setCheckable(True)
        btn_registrar.clicked.connect(lambda: self._navegar_vista(4))
        layout.addWidget(btn_registrar)

        # Grupo Profesores
        layout.addWidget(self._label_grupo("PROFESORES"))

        btn_profes = QPushButton("Ver Profesores")
        btn_profes.setObjectName("BtnSidebarItem")
        btn_profes.setCheckable(True)
        btn_profes.clicked.connect(lambda: self._navegar_vista(5))
        layout.addWidget(btn_profes)

        # Grupo Notas
        layout.addWidget(self._label_grupo("NOTAS Y INFORMES"))

        btn_notas = QPushButton("Cargar / Ver Notas")
        btn_notas.setObjectName("BtnSidebarItem")
        btn_notas.setCheckable(True)
        btn_notas.clicked.connect(lambda: self._navegar_vista(5))
        layout.addWidget(btn_notas)

        layout.addStretch()

        # Volver al Menu
        btn_menu = QPushButton("Volver al Menu")
        btn_menu.setObjectName("BtnSidebarItem")
        btn_menu.clicked.connect(lambda: self.stack_global.setCurrentIndex(0))
        layout.addWidget(btn_menu)

        # Cerrar Sesion
        btn_logout = QPushButton("Cerrar Sesion")
        btn_logout.setObjectName("BtnSidebarItem")
        btn_logout.clicked.connect(self._ejecutar_logout)
        layout.addWidget(btn_logout)

        return frame

    def _label_grupo(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("SidebarGroupLabel")
        return lbl

    # ========================================================================
    # NAVEGACION
    # ========================================================================

    def _abrir_seccion(self, index_vista):
        """Abre el dashboard directamente en la vista indicada."""
        self.stack_vistas.setCurrentIndex(index_vista)
        if index_vista == 1:
            self.vista_ver_alumnos.cargar_datos()
        self.stack_global.setCurrentIndex(1)

    def _navegar_vista(self, index):
        """Navega entre vistas dentro del dashboard sidebar."""
        self.stack_vistas.setCurrentIndex(index)
        if index == 1:
            self.vista_ver_alumnos.cargar_datos()

    def _refrescar_tabla_alumnos(self):
        self.vista_ver_alumnos.cargar_datos()
        self.stack_vistas.setCurrentIndex(1)

    def _ejecutar_logout(self):
        if self.on_logout_callback:
            self.on_logout_callback()
